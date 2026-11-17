# -*- coding: utf-8 -*-
"""
COLETA DE DADOS BRUTOS: Projeto A3 (Mobilidade urbana em Salvador)
=====================================================================
Etapa "E" (Extração) do ETL. Este script baixa, DIRETAMENTE DAS FONTES OFICIAIS,
todos os arquivos brutos usados no projeto e salva tudo em uma pasta `dados_brutos/`
(e, no final, em um arquivo `dados_brutos.zip`).

Pode ser executado:
  * no Google Colab:   !python coleta_dados_brutos.py
  * no computador:     python coleta_dados_brutos.py  (precisa de Python 3 + biblioteca requests)

Fontes baixadas
---------------
1. IBGE / SIDRA (API oficial)      -> população (estimativas e censos), IPCA, deslocamento casa-trabalho (Censo 2022)
2. SENATRAN / Ministério dos Transportes -> frota de veículos por município e tipo (dezembro de cada ano)
3. Ministério das Cidades / PEMOB   -> Pesquisa Nacional de Mobilidade Urbana (bases municipais)
4. SEI-BA (Governo da Bahia)        -> tabelas do IMEC (índice de passageiros de ônibus urbanos)
5. CTB (Governo da Bahia)           -> gráfico oficial de passageiros do metrô

Cada arquivo é baixado do endereço oficial, e o script grava um
`log_coleta.csv` com URL, data/hora, tamanho e status de cada download (rastreabilidade).
"""

import csv
import datetime as dt
import json
import os
import re
import shutil
import sys
import time
from urllib.parse import urljoin

import requests

# ---------------------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------------------
PASTA = os.path.abspath(os.environ.get("PASTA_DADOS_BRUTOS", "dados_brutos"))
ANOS_FROTA = list(range(2014, 2026))          # dez/2014 a dez/2025 (antes de 2014 o SENATRAN não publica a frota por município E tipo)
HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico UNIFACS - analise de dados)"}

# Salvador + as 12 outras capitais com mais de 1 milhão de habitantes no Censo 2022
CAPITAIS = {
    2927408: "Salvador", 3550308: "São Paulo", 3304557: "Rio de Janeiro",
    5300108: "Brasília", 2304400: "Fortaleza", 3106200: "Belo Horizonte",
    1302603: "Manaus", 4106902: "Curitiba", 2611606: "Recife",
    5208707: "Goiânia", 1501402: "Belém", 4314902: "Porto Alegre",
    2111300: "São Luís",
}

LOG = []


def registrar(fonte, url, arquivo, status, detalhe=""):
    tamanho = os.path.getsize(arquivo) if arquivo and os.path.exists(arquivo) else 0
    LOG.append({
        "fonte": fonte, "url": url, "arquivo": os.path.relpath(arquivo, PASTA) if arquivo else "",
        "bytes": tamanho, "status": status, "detalhe": detalhe,
        "data_hora": dt.datetime.now().isoformat(timespec="seconds"),
    })
    print(f"[{status}] {fonte}: {os.path.basename(arquivo) if arquivo else url} {detalhe}")


def baixar(url, destino, fonte, tentativas=2, limite_total=150):
    """Baixa um arquivo (até 2 tentativas). Aborta se o download inteiro passar de `limite_total` segundos.
    Retorna o caminho salvo ou None."""
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    ultimo = ""
    for i in range(tentativas):
        inicio = time.time()
        try:
            with requests.get(url, headers=HEADERS, timeout=(20, 40), stream=True) as r:
                if r.status_code != 200:
                    ultimo = f"HTTP {r.status_code}"
                    if r.status_code in (403, 404, 410):   # arquivo inexistente: não adianta tentar de novo
                        break
                    continue
                partes = []
                for bloco in r.iter_content(chunk_size=65536):
                    partes.append(bloco)
                    if time.time() - inicio > limite_total:
                        raise TimeoutError(f"passou de {limite_total}s")
                conteudo = b"".join(partes)
            if len(conteudo) > 200:
                with open(destino, "wb") as f:
                    f.write(conteudo)
                registrar(fonte, url, destino, "OK")
                return destino
            ultimo = "arquivo vazio"
        except Exception as e:  # noqa: BLE001
            ultimo = f"erro: {e}"
        time.sleep(2 * (i + 1))
    registrar(fonte, url, None, "FALHA", ultimo)
    return None


def pagina(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=(20, 40))
        return r.text if r.status_code == 200 else ""
    except Exception:  # noqa: BLE001
        return ""


# ---------------------------------------------------------------------------
# 1) IBGE / SIDRA
# ---------------------------------------------------------------------------
def sidra(tabela, nivel, locais, variaveis="all", periodos="all", classif="", nome=None):
    url = (f"https://apisidra.ibge.gov.br/values/t/{tabela}/{nivel}/{locais}"
           f"/v/{variaveis}/p/{periodos}{classif}")
    nome = nome or f"sidra_{tabela}.json"
    return baixar(url, os.path.join(PASTA, "ibge", nome), f"IBGE/SIDRA tabela {tabela}")


def coletar_ibge():
    caps = ",".join(str(c) for c in CAPITAIS)
    # Estimativas anuais da população residente (2001-2026)
    sidra(6579, "n6", caps, nome="sidra_6579_estimativas_populacao.json")
    # Censo 2022: população residente e variação em relação ao Censo 2010 compatibilizado
    sidra(4709, "n6", caps, nome="sidra_4709_censo2022_variacao2010.json")
    # Censo 2022: população e densidade demográfica (área territorial)
    sidra(4714, "n6", caps, nome="sidra_4714_censo2022_densidade.json")
    # IPCA - número-índice mensal (Brasil), para deflacionar a tarifa
    sidra(1737, "n1", "all", "2266", "all", nome="sidra_1737_ipca_indice.json")


def coletar_censo_deslocamento():
    """Censo 2022 - deslocamento casa-trabalho. As tabelas foram publicadas pelo IBGE na faixa 10320-10345
    do SIDRA (ex.: 10331 = tempo habitual de deslocamento). Para cada número, lemos os METADADOS
    (arquivo pequeno) e só baixamos as tabelas cujo nome fala de deslocamento para o trabalho."""
    caps = ",".join(str(c) for c in CAPITAIS)
    for tab in range(10320, 10346):
        meta_arq = os.path.join(PASTA, "ibge", f"meta_{tab}.json")
        if not baixar(f"https://servicodados.ibge.gov.br/api/v3/agregados/{tab}/metadados",
                      meta_arq, f"IBGE metadados {tab}", tentativas=1, limite_total=30):
            continue
        try:
            with open(meta_arq, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:  # noqa: BLE001
            continue
        nome_tab = meta.get("nome", "").lower()
        if not ("deslocamento" in nome_tab and "trabalho" in nome_tab):
            os.remove(meta_arq)
            continue
        if "N6" not in meta.get("nivelTerritorial", {}).get("Administrativo", []):
            continue
        # tempo ou meio de transporte: todas as categorias; demais classificações: só o "Total"
        partes = []
        for c in meta.get("classificacoes", []):
            nome_c = c["nome"].lower()
            if "tempo" in nome_c or "meio de transporte" in nome_c:
                partes.append(f"/c{c['id']}/all")
            else:
                total = [k for k in c["categorias"] if k["nome"].strip().lower() == "total"]
                if total:
                    partes.append(f"/c{c['id']}/{total[0]['id']}")
        sidra(tab, "n6", caps, "all", "all", "".join(partes),
              nome=f"sidra_{tab}_censo2022_deslocamento.json")


# ---------------------------------------------------------------------------
# 2) SENATRAN - frota por município e tipo (dezembro de cada ano)
# ---------------------------------------------------------------------------
BASE_SENATRAN = "https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/"


# Endereços exatos dos arquivos de dezembro, conferidos nas páginas oficiais do SENATRAN
# (o nome do arquivo muda de um ano para outro, por isso guardamos a lista).
RENAVAM = "https://www.gov.br/transportes/pt-br/assuntos/transito/arquivos-senatran/estatisticas/renavam/"
URLS_SENATRAN = {
    2014: RENAVAM + "2014/dezembro/frota_por_municipio_e_tipo_dez_2014.xlsx/@@download/file",
    2015: RENAVAM + "2015/dezembro/frota_por_municipio_e_tipo-dez_15.rar/@@download/file",
    2016: RENAVAM + "2016/dezembro/frota_por_municipio_e_tipo-dez_16.xlsx/@@download/file",
    2017: RENAVAM + "2017/dezembro/frota_munic_dezembro_2017.xls/@@download/file",
    2018: RENAVAM + "2018/dezembro/frota_munic_dezembro_2018.xls/@@download/file",
    2019: RENAVAM + "2019/dezembro/frota_munic_modelo_dezembro_2019.xls/@@download/file",
    2020: RENAVAM + "2020/dezembro/frota-reg-munic-tipo-modelo-07-dezembro2020.xls/@@download/file",
    2021: RENAVAM + "2021/dezembro/frota-munic-modelo-dezembro-2021.xls/@@download/file",
    2022: RENAVAM + "2022/dezembro/frota_munic_modelo_dezembro_2022.xls/@@download/file",
    2023: RENAVAM + "2023/Dezembro/frota_munic_modelo_dezembro_2023.xls/@@download/file",
    2024: BASE_SENATRAN + "FrotapormunicipioetipoDezembro2024.xlsx/@@download/file",
    2025: BASE_SENATRAN + "arquivos-renavam-2025/FrotaporMunicipioetipoDEZEMBRO2025.xlsx/@@download/file",
}


def procurar_link_senatran(ano):
    """Plano B: procura na página do ano um link de frota por MUNICÍPIO de DEZEMBRO."""
    url_pag = f"{BASE_SENATRAN}frota-de-veiculos-{ano}"
    html = pagina(url_pag)
    candidatos = []
    for href in re.findall(r'href="([^"]+)"', html):
        h = href.lower()
        # Basta ter "munic" e "dez" no nome. Não exigimos "tipo": em 2017–2023 o arquivo
        # se chama "frota_munic_(modelo_)dezembro_AAAA" e mesmo assim traz a frota por tipo.
        if "munic" in h and "dez" in h and "uf_munic" not in h and \
                not any(x in h for x in ["cep", "combust", "cor", "potenc", "restric", "especie", "fab"]):
            candidatos.append(urljoin(url_pag, href))
    # se houver mais de um, prefere o que tem "tipo" no nome
    candidatos.sort(key=lambda u: "tipo" not in u.lower())
    return candidatos[0] if candidatos else None


def coletar_senatran():
    for ano in ANOS_FROTA:
        url = URLS_SENATRAN.get(ano) or procurar_link_senatran(ano)
        if not url:
            registrar("SENATRAN", f"{BASE_SENATRAN}frota-de-veiculos-{ano}", None, "FALHA", f"link de dezembro/{ano} não encontrado")
            continue
        if "@@download" not in url:
            url = url.rstrip("/") + "/@@download/file"
        ext = re.search(r"\.(xlsx|xls|csv|zip|rar)", url.lower())
        ext = ext.group(1) if ext else "bin"
        baixar(url, os.path.join(PASTA, "senatran", f"frota_municipio_tipo_dez_{ano}.{ext}"), f"SENATRAN {ano}")


# ---------------------------------------------------------------------------
# 3) PEMOB - Ministério das Cidades
# ---------------------------------------------------------------------------
def coletar_pemob():
    base = "https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/mobilidade-urbana/arquivos/"
    for ed in range(2018, 2027):
        for nome in (f"pemob{ed}_municipal.xlsx", f"pemob{ed}_metropolitana.xlsx"):
            baixar(base + nome, os.path.join(PASTA, "pemob", nome), f"PEMOB {ed}")
    # Também procura links .xlsx nas páginas da pesquisa
    for url_pag in [
        "https://www.gov.br/cidades/pt-br/assuntos/mobilidade-urbana/pesquisa-nacional-de-mobilidade-urbana-pemob",
        "https://www.gov.br/cidades/pt-br/assuntos/mobilidade-urbana/pesquisa-nacional-de-mobilidade-urbana-pemob-2026",
    ]:
        for href in re.findall(r'href="([^"]+\.xlsx[^"]*)"', pagina(url_pag)):
            url = urljoin(url_pag, href)
            nome = os.path.basename(url.split("/@@")[0])
            destino = os.path.join(PASTA, "pemob", nome)
            if not os.path.exists(destino):
                baixar(url, destino, "PEMOB (página)")


# ---------------------------------------------------------------------------
# 4) SEI-BA - IMEC (tabelas em PDF) e 5) CTB - gráfico do metrô
# ---------------------------------------------------------------------------
def coletar_sei_ctb():
    pdfs = {
        "TABELAS_IMEC_DEZEMBRO_2025.pdf": "https://www.ba.gov.br/sei/sites/site-sei/files/2026-02/TABELAS_IMEC_DEZEMBRO_2025.pdf",
        "ind_imec_jul_26.pdf": "https://www.ba.gov.br/sei/sites/site-sei/files/2026-09/ind_imec_jul_26.pdf",
    }
    for nome, url in pdfs.items():
        baixar(url, os.path.join(PASTA, "sei", nome), "SEI-BA IMEC")
    html = pagina("https://www.ba.gov.br/trilhos/855/estatisticas-do-metro")
    for src in re.findall(r'(?:src|href)="([^"]+Passageiros[^"]+\.(?:jpg|png|pdf|xlsx))"', html, flags=re.I):
        url = urljoin("https://www.ba.gov.br/", src)
        baixar(url, os.path.join(PASTA, "ctb", os.path.basename(url)), "CTB estatísticas do metrô")


# ---------------------------------------------------------------------------
def main():
    os.makedirs(PASTA, exist_ok=True)
    print(f"Salvando em: {PASTA}\n")
    coletar_ibge()
    coletar_senatran()
    coletar_pemob()
    coletar_sei_ctb()
    coletar_censo_deslocamento()
    with open(os.path.join(PASTA, "log_coleta.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(LOG[0].keys()))
        w.writeheader()
        w.writerows(LOG)
    ok = sum(1 for x in LOG if x["status"] == "OK")
    print(f"\nConcluído: {ok} arquivos baixados, {len(LOG) - ok} falhas (veja log_coleta.csv).")
    zip_path = shutil.make_archive(PASTA, "zip", PASTA)
    print(f"Arquivo compactado: {zip_path}")


if __name__ == "__main__":
    sys.exit(main())
