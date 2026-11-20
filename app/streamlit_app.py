"""
Dashboard: Mobilidade urbana em Salvador, transporte público e população (2010–2025)
Projeto A3 · Análise de Dados e Big Data · UNIFACS

Para rodar localmente:  streamlit run app/streamlit_app.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui

# ----------------------------------------------------------------------------
# Configuração e dados
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Mobilidade em Salvador · Projeto A3", layout="wide",
                   page_icon=str(ui.ASSETS / "logo_unifacs.png"), initial_sidebar_state="collapsed")
ui.estilo()

DADOS = Path(__file__).resolve().parent.parent / "data" / "processed"
AZUL, LARANJA, AQUA, VERMELHO = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
CINZA, CINZA_CLARO, MARINHO = "#898781", "#c3c2b7", "#0e1a33"
SSA = "Salvador"
CFG = {"displayModeBar": False, "responsive": True}
REPO = "https://github.com/anthonyxnatan/mobilidade-salvador-a3"
LINKS = [("Relatório", f"{REPO}/blob/main/relatorios/Relatorio_Final_A3.pdf", "livro"),
         ("Vídeo", "https://youtu.be/loBg9GbHmdU", "video"),
         ("GitHub", REPO, "codigo")]
EQUIPE = ["Anthony Natan Santos Pereira", "Caio Branco Marques", "Clara Gil Moreira de Alencar Santiago",
          "Fernanda Santos da Silva", "Lukas Carneiro Rocha"]
PROF = "Prof. Eduardo Sidney da Silva Xavier"
UC = "UC Análise de Dados e Big Data"
COORD = {"Belém": (-48.49, -1.46), "Belo Horizonte": (-43.94, -19.92), "Brasília": (-47.88, -15.79), "Curitiba": (-49.27, -25.43),
         "Fortaleza": (-38.52, -3.73), "Goiânia": (-49.25, -16.68), "Manaus": (-60.02, -3.12), "Porto Alegre": (-51.23, -30.03),
         "Recife": (-34.88, -8.05), "Rio de Janeiro": (-43.17, -22.91), "Salvador": (-38.50, -12.97), "São Luís": (-44.30, -2.53),
         "São Paulo": (-46.63, -23.55)}


@st.cache_data
def carregar():
    d = {nome: pd.read_csv(DADOS / f"{nome}.csv") for nome in [
        "base_salvador_anual", "base_salvador_mensal", "painel_capitais_anual", "deslocamento_capitais_censo",
        "tempo_medio_por_meio_censo2022", "populacao_capitais", "pemob_capitais", "tarifa_anual", "metro_mensal",
        "recomendacoes", "hipoteses", "cenarios_2030", "projecao_motorizacao", "oferta_indicadores", "grupos_capitais",
        "decomposicao_queda", "previsao_metro_mensal", "fontes_documentais", "dicionario_dados"]}
    d["base_salvador_mensal"]["data"] = pd.to_datetime(d["base_salvador_mensal"]["data"])
    d["previsao_metro_mensal"]["data"] = pd.to_datetime(d["previsao_metro_mensal"]["data"])
    d["R"] = json.load(open(DADOS / "resultados_chave.json", encoding="utf-8"))
    d["mapa"] = json.load(open(ui.ASSETS / "america_do_sul.json", encoding="utf-8"))
    return d


D = carregar()
R = D["R"]
base, mensal, painel = D["base_salvador_anual"], D["base_salvador_mensal"], D["painel_capitais_anual"]


def br(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sinal(v, casas=1):
    return f"{'+' if v > 0 else ''}{br(v, casas)}"


def layout(fig, titulo, sub="", y="", altura=390):
    texto = f"<b>{titulo}</b>"
    if sub:
        texto += f"<br><span style='font-size:12.5px;color:{CINZA};font-weight:400'>{sub}</span>"
    fig.update_layout(
        title=dict(text=texto, x=0, xanchor="left", y=.97, yanchor="top", font=dict(size=15.5, color=MARINHO)),
        height=altura, separators=",.", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=14, t=74 if sub else 52, b=34), legend=dict(orientation="h", y=-0.17, x=0, font=dict(size=12)),
        hovermode="x unified", yaxis_title=y, font=dict(family="Inter, system-ui, sans-serif", color="#52514e", size=12.5),
        hoverlabel=dict(bgcolor="white", bordercolor="#e1e0d9", font=dict(family="Inter, system-ui, sans-serif", size=13, color="#0b0b0b")),
        transition=dict(duration=650, easing="cubic-in-out"))
    fig.update_xaxes(showgrid=False, linecolor="#d9d7cf", ticks="outside", tickcolor="#d9d7cf", ticklen=4, automargin=True)
    fig.update_yaxes(gridcolor="#ecebe5", zeroline=False, automargin=True)
    return fig


def grafico(fig, key=None):
    st.plotly_chart(fig, width="stretch", config=CFG, theme=None, key=key)


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def eixo_mes_pt(fig, datas, passo=3):
    """Rótulos de mês em português (o Plotly usa inglês por padrão)."""
    datas = pd.Series(pd.to_datetime(datas)).drop_duplicates().sort_values()
    marcas = [d for d in datas if (d.month - 1) % passo == 0]
    fig.update_xaxes(tickvals=marcas, ticktext=[f"{MESES[d.month - 1]}/{d.strftime('%y')}" for d in marcas])
    fig.update_xaxes(hoverformat="%m/%Y")
    return fig


def botoes_animacao(fig, anos, prefixo):
    """Botão de reproduzir e barra de anos para gráficos animados do Plotly."""
    fig.update_layout(
        updatemenus=[dict(type="buttons", direction="left", x=-0.02, y=-0.105, xanchor="right", yanchor="top", showactive=False, pad=dict(t=0, r=10),
                          bgcolor="#0e1a33", bordercolor="#0e1a33", font=dict(color="white", size=12.5),
                          buttons=[dict(label="  ▶  Reproduzir  ", method="animate",
                                        args=[None, dict(frame=dict(duration=650, redraw=False), transition=dict(duration=550, easing="cubic-in-out"),
                                                         fromcurrent=True, mode="immediate")]),
                                   dict(label="  ❚❚  ", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])],
        sliders=[dict(active=len(anos) - 1, x=0, y=-0.085, len=1, xanchor="left", yanchor="top", pad=dict(t=0), currentvalue=dict(visible=True, prefix="Ano: ", xanchor="right", offset=8, font=dict(size=15, color="#0e1a33")),
                      bgcolor="#e6e4dd", activebgcolor=AZUL, bordercolor="#e6e4dd", tickcolor="#c3c2b7", font=dict(size=11, color=CINZA),
                      steps=[dict(label=str(a), method="animate", args=[[f"{prefixo}{a}"], dict(mode="immediate", frame=dict(duration=0, redraw=False),
                                                                                                    transition=dict(duration=400))]) for a in anos])])
    return fig


# ----------------------------------------------------------------------------
# Barra superior e faixa principal
# ----------------------------------------------------------------------------
ui.topo(LINKS)
met_serie = base.dropna(subset=["metro_passageiros_ano"])["metro_passageiros_ano"].tolist()
ui.hero(
    "Transporte público e população · 2010 a 2025",
    "Salvador encolheu, o carro cresceu e <em>o ônibus ficou mais lento</em>",
    "Painel interativo do projeto A3, construído apenas com dados oficiais do IBGE, SENATRAN, Ministério das Cidades, "
    "SEI-BA, CTB e Prefeitura de Salvador.",
    "7 instituições · 894 registros",
    [
        dict(rotulo="População, Censo 2022", valor=br(R["pop_2022"] / 1e6, 2), unidade="mi", icone="pessoas", cor="marinho",
             delta=f"{br(R['var_pop_2010_2022_pct'], 1)}%", tom="neutro", nota="desde 2010", serie=base["populacao"].tolist()),
        dict(rotulo="Autos e motos por mil hab.", valor=br(R["motorizacao_2025"]), icone="carro", cor="laranja",
             delta=f"+{br((R['motorizacao_2025'] / R['motorizacao_2014'] - 1) * 100)}%", tom="ruim", nota="desde 2014",
             serie=base["motorizacao_por_mil_hab"].dropna().tolist()),
        dict(rotulo="Passageiros de ônibus por dia", valor=br(R["stco_pass_dia_2024"] / 1e6, 2), unidade="mi", icone="onibus", cor="azul",
             delta=f"{br(R['var_pass_dia_2019_2024_pct'], 1)}%", tom="ruim", nota="2019 → 2024",
             pares=[("2019", R["stco_pass_dia_2019"]), ("2024", R["stco_pass_dia_2024"])]),
        dict(rotulo="Velocidade do ônibus no pico", valor=br(R["vel_2025"], 1), unidade="km/h", icone="velocidade", cor="vermelho",
             delta=f"{br(R['var_vel_pct'], 0)}%", tom="ruim", nota="2022 → 2025", pares=[("2022", R["vel_2022"]), ("2025", R["vel_2025"])]),
        dict(rotulo="Passageiros do metrô (2025)", valor="117,5", unidade="mi", icone="trem", cor="aqua",
             delta="recorde", tom="bom", nota="igual a 2024", serie=met_serie),
    ])

abas = st.tabs(["Visão geral", "População e oferta", "Ônibus e metrô", "Trânsito e motorização",
                "Salvador × capitais", "Projeções 2030", "Recomendações", "Dados e fontes"])

# ----------------------------------------------------------------------------
# 1. Visão geral
# ----------------------------------------------------------------------------
with abas[0]:
    c1, c2 = st.columns([1.6, 1], gap="medium")
    with c1:
        b = base[base["ano"] >= 2014]
        fig = go.Figure()
        for col, nome, cor in [("populacao", "População", CINZA), ("autos", "Automóveis e utilitários", LARANJA), ("motos", "Motos", AQUA)]:
            serie = b[col] / b[col].iloc[0] * 100
            fig.add_scatter(x=b["ano"], y=serie, name=nome, mode="lines+markers",
                            line=dict(color=cor, width=3, shape="spline", smoothing=.5), marker=dict(size=7, line=dict(color="white", width=1.5)),
                            hovertemplate="%{y:.1f}")
            fig.add_annotation(x=b["ano"].iloc[-1], y=serie.iloc[-1], text=f"<b>{br(serie.iloc[-1])}</b>", showarrow=False, xanchor="left", xshift=8,
                               font=dict(size=12, color=cor))
        fig.add_hline(y=100, line_color=CINZA_CLARO, line_width=1)
        fig.update_xaxes(range=[2013.6, 2026])
        grafico(layout(fig, "Menos gente, muito mais veículos", "Índice, 2014 = 100", "índice", 400))
        ui.fonte("SENATRAN (frota em dezembro) e IBGE (população compatibilizada)")
    with c2:
        ui.corrida(R["tempo_onibus_min"], R["tempo_auto_min"], "Casa ao trabalho: ônibus contra carro",
                   "Tempo médio da viagem em Salvador, Censo 2022")
        ui.nota("A queda da população não explica a crise",
                f"Ela responde por só <b>{br(R['ef_pop_pct'])}%</b> da perda de passageiros do ônibus. O metrô, no máximo, por "
                f"<b>{br(R['ef_metro_pct'])}%</b>. O restante vem do carro, da moto e da perda de qualidade do serviço.",
                cor="laranja", icone="alerta")
        ui.fonte("IBGE, Censo 2022 (tab. 10330); decomposição do projeto")

    ui.linha_tempo("Uma década de mudanças", [
        ("2010", "Censo", "Salvador tinha <b>2,68 milhões</b> de habitantes.", "marinho"),
        ("2014", "Metrô inaugurado", "A cidade tinha <b>300</b> autos e motos por mil habitantes.", "azul"),
        ("2020", "Pandemia", "Metrô cai para <b>62 milhões</b> de passageiros no ano.", "vermelho"),
        ("2022", "Censo e BRT", "População de <b>2,42 milhões</b> (−9,6%); BRT começa a operar.", "laranja"),
        ("2024", "Recorde no metrô", "Metrô com <b>117,5 milhões</b>; ônibus com <b>1,25 milhão</b> por dia.", "aqua"),
    ])

    ui.secao("Em cinco pontos", "O que os dados mostram")
    ui.achados([
        ("A população não cresceu: caiu", f"Salvador perdeu <b>{br(-R['var_pop_2010_2022_pct'], 1)}%</b> dos moradores entre os Censos 2010 e 2022 e segue em queda."),
        ("Os veículos cresceram muito", f"Desde 2014, <b>+{br(R['var_autos_2014_2025_pct'])}% de autos</b> e <b>+{br(R['var_motos_2014_2025_pct'])}% de motos</b>."),
        ("O ônibus perdeu um sexto dos passageiros", f"Queda de <b>{br(-R['var_pass_dia_2019_2024_pct'])}%</b> entre 2019 e 2024, cerca de 250 mil viagens a menos por dia."),
        ("O serviço ficou mais lento e menos confiável", f"Velocidade no pico de {br(R['vel_2022'], 1)} para <b>{br(R['vel_2025'], 1)} km/h</b>; viagens não completadas de {br(R['nao_completadas_2022'])}% para <b>{br(R['nao_completadas_2025'], 1)}%</b>."),
        ("Quem depende do ônibus perde tempo", f"A viagem casa-trabalho de ônibus leva <b>{br(R['tempo_onibus_min'])} min</b>, contra <b>{br(R['tempo_auto_min'])} min</b> de carro."),
    ])

# ----------------------------------------------------------------------------
# 2. População e oferta
# ----------------------------------------------------------------------------
with abas[1]:
    ui.secao("População e oferta", "A cidade diminuiu, e a oferta de ônibus perdeu qualidade",
             "Em número de veículos a oferta acompanhou a população. Em quilômetros rodados, velocidade e cumprimento das viagens, não.")
    col1, col2 = st.columns([1.25, 1], gap="medium")
    with col1:
        p = D["populacao_capitais"]
        p = p[(p["municipio"] == SSA) & (p["ano"] <= 2026)]
        fig = go.Figure()
        fig.add_scatter(x=p["ano"], y=p["populacao"], name="Série compatibilizada (usada)", line=dict(color=AZUL, width=3),
                        fill="tozeroy", fillcolor="rgba(42,120,214,.07)", hovertemplate="%{y:,.0f}")
        q = p.dropna(subset=["pop_estimativa_oficial"])
        fig.add_scatter(x=q["ano"], y=q["pop_estimativa_oficial"], name="Estimativa oficial publicada", mode="lines+markers",
                        line=dict(color=CINZA, dash="dot"), marker=dict(size=6), hovertemplate="%{y:,.0f}")
        fig.update_yaxes(tickformat=",.0f", range=[2.2e6, 2.95e6])
        grafico(layout(fig, "População de Salvador", "A série oficial muda de base em 2022 e 2024; o projeto compatibilizou os anos", "habitantes", 410))
        ui.fonte("IBGE, Censos 2010/2022 e Estimativas (tab. 6579 e 4709); compatibilização do projeto")
    with col2:
        ui.tabela_oferta(D["oferta_indicadores"], br)
        ui.fonte("Ministério das Cidades, PEMOB 2023 e 2026 (anos-base 2022 e 2025); IBGE")
        ui.nota("A oferta acompanhou a população?",
                "<b>Em quantidade, sim</b>: ônibus por habitante até subiu, porque a população caiu. <b>Em qualidade, não</b>: "
                "menos km por habitante, ônibus mais lentos e mais viagens não completadas.", cor="azul", icone="lampada")

    ui.secao("Confiabilidade", "De cada 100 viagens programadas, quantas não foram feitas")
    ui.grades([("2022", R["nao_completadas_2022"]), ("2025", R["nao_completadas_2025"])])
    ui.fonte("Ministério das Cidades, PEMOB 2023 e 2026 (viagens programadas e não realizadas)")

    ui.secao("Rede de linhas", "Habitantes por linha e frota por habitante")
    ui.kpis([
        dict(rotulo="Habitantes por linha em 2017 (530 linhas)", valor=br(R["hab_por_linha_2017"]), icone="rota", cor="marinho"),
        dict(rotulo="Habitantes por linha hoje (515 linhas)", valor=br(R["hab_por_linha_atual"]), icone="rota", cor="azul",
             delta=f"{sinal((R['hab_por_linha_atual'] / R['hab_por_linha_2017'] - 1) * 100)}%", tom="neutro", nota="vs 2017"),
        dict(rotulo="Ônibus por 100 mil hab. (2025)", valor=br(R["onibus_100mil_2025"], 1), icone="onibus", cor="aqua",
             delta=f"+{br(R['onibus_100mil_2025'] - R['onibus_100mil_2022'], 1)}", tom="bom", nota="vs 2022"),
    ])
    ui.fonte("Prefeitura de Salvador (Relatório de Atividades 2017), Integra Salvador (site, acesso nov/2026), PEMOB, IBGE")

# ----------------------------------------------------------------------------
# 3. Ônibus e metrô
# ----------------------------------------------------------------------------
with abas[2]:
    ui.secao("Ônibus e metrô", "O metrô bateu recorde, mas não explica a perda do ônibus",
             "Os dois sistemas sobem e descem juntos ao longo do ano, sinal de que muitas viagens são integradas.")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        met = base.dropna(subset=["metro_passageiros_ano"])
        fig = go.Figure(go.Bar(x=met["ano"], y=met["metro_passageiros_ano"] / 1e6,
                               marker=dict(color=[CINZA_CLARO if a in (2020, 2021) else AZUL for a in met["ano"]], cornerradius=6),
                               text=(met["metro_passageiros_ano"] / 1e6).map(lambda v: br(v, 1)), textposition="outside", cliponaxis=False,
                               hovertemplate="%{y:.1f} milhões<extra></extra>"))
        grafico(layout(fig, "Metrô: passageiros por ano", "Milhões; anos de pandemia em cinza", "milhões").update_layout(hovermode="closest"))
        ui.fonte("Cia. do Metrô da Bahia (demonstrações financeiras) e CTB; 2018, 2020–2022 e 2025 arredondados pela fonte")
    with col2:
        dq = D["decomposicao_queda"]
        fig = go.Figure(go.Waterfall(
            x=["2019", "População", "Metrô (hip. máx.)", "Outros fatores", "2024"], measure=["absolute", "relative", "relative", "relative", "total"],
            y=[R["stco_pass_dia_2019"] / 1e3] + list(-dq["passageiros_dia"] / 1e3) + [0],
            text=[br(R["stco_pass_dia_2019"] / 1e3)] + [f"−{br(v / 1e3)}" for v in dq["passageiros_dia"]] + [br(R["stco_pass_dia_2024"] / 1e3)],
            textposition="outside", cliponaxis=False,
            decreasing=dict(marker=dict(color=VERMELHO)), totals=dict(marker=dict(color=AZUL)), increasing=dict(marker=dict(color=AZUL)),
            connector=dict(line=dict(color=CINZA_CLARO, dash="dot")), hovertemplate="%{y:,.0f} mil<extra></extra>"))
        fig.update_yaxes(range=[1000, 1600])
        fig.update_xaxes(type="category")
        grafico(layout(fig, "Para onde foram 250 mil passageiros por dia", "Ônibus, 2019 → 2024, em mil passageiros/dia", "mil passageiros/dia")
                .update_layout(hovermode="closest"))
        ui.fonte("SEMOB (passageiros/dia), IBGE (população), CTB (metrô); decomposição do projeto")

    @st.fragment
    def mensal_onibus_metro():
        m = mensal.dropna(subset=["indice_metro_2024_100"])
        opcoes = list(m["data"].dt.strftime("%m/%Y"))
        periodo = st.select_slider("Meses exibidos", options=opcoes, value=(opcoes[0], opcoes[-1]), key="meses")
        ini, fim = [pd.to_datetime(x, format="%m/%Y") for x in periodo]
        mm = m[(m["data"] >= ini) & (m["data"] <= fim)]
        fig = go.Figure()
        fig.add_scatter(x=mm["data"], y=mm["indice_onibus_2024_100"], name="Ônibus urbanos (SEI-BA/IMEC)", mode="lines+markers",
                        line=dict(color=AZUL, width=3, shape="spline", smoothing=.4), marker=dict(size=6), hovertemplate="%{y:.1f}")
        fig.add_scatter(x=mm["data"], y=mm["indice_metro_2024_100"], name="Metrô (CTB)", mode="lines+markers",
                        line=dict(color=LARANJA, width=3, shape="spline", smoothing=.4), marker=dict(size=6), hovertemplate="%{y:.1f}")
        fig.add_hline(y=100, line_color=CINZA_CLARO, line_width=1)
        eixo_mes_pt(fig, mm["data"], 3 if len(mm) > 12 else 1)
        grafico(layout(fig, "Passageiros por mês", f"Índice (média de 2024 = 100); correlação entre os dois sistemas r = {br(R['corr_mensal_onibus_metro'], 2)}", "índice"),
                key="mensal")
        ui.fonte("SEI-BA, IMEC (dados SETPS); CTB, demonstrativo mensal do metrô")

    mensal_onibus_metro()

# ----------------------------------------------------------------------------
# 4. Trânsito e motorização
# ----------------------------------------------------------------------------
with abas[3]:
    ui.secao("Trânsito e motorização", "Mais carros e motos, menos velocidade para todos",
             "A frota cresceu muito mais rápido que a população, e o ônibus divide a mesma pista congestionada. Use o botão para ver a evolução ano a ano.")
    col1, col2 = st.columns([1.15, 1], gap="medium")
    with col1:
        pc = painel.pivot_table(index="municipio", columns="ano", values="motorizacao_por_mil_hab")
        ordem = pc[2025].sort_values().index.tolist()
        anos_m = list(range(2014, 2026))
        cores = [AZUL if m == SSA else "#cfcdc5" for m in ordem]

        def barras(a):
            v = pc.loc[ordem, a]
            return go.Bar(y=ordem, x=v, orientation="h", marker=dict(color=cores, cornerradius=5),
                          text=[f"<b>{br(x)}</b>" if m == SSA else br(x) for m, x in zip(ordem, v)], textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}: %{x:.0f} veículos por mil hab.<extra></extra>")

        fig = go.Figure(data=[barras(2025)], frames=[go.Frame(data=[barras(a)], name=f"m{a}") for a in anos_m])
        fig.update_xaxes(range=[0, pc.max().max() * 1.16], showgrid=True, gridcolor="#ecebe5")
        layout(fig, "Autos e motos por mil habitantes nas capitais", "Salvador em azul; 2014 a 2025", "", 520)
        fig.update_layout(hovermode="closest", margin=dict(l=6, r=40, t=74, b=118))
        botoes_animacao(fig, anos_m, "m")
        grafico(fig, key="corrida_motorizacao")
        ui.fonte("SENATRAN e IBGE; frota de dezembro de cada ano")
    with col2:
        t = D["tempo_medio_por_meio_censo2022"]
        t = t[(t["municipio"] == SSA) & (t["trabalhadores"] > 5000)].sort_values("tempo_medio_min")
        coletivos = {"Ônibus", "Trem ou metrô", "Van, perua ou assemelhados", "BRT ou ônibus de trânsito rápido"}
        fig = go.Figure(go.Bar(y=t["meio_transporte"], x=t["tempo_medio_min"], orientation="h",
                               marker=dict(color=[AZUL if x in coletivos else CINZA_CLARO for x in t["meio_transporte"]], cornerradius=5),
                               text=t["tempo_medio_min"].round(0).astype(int).astype(str) + " min", textposition="outside", cliponaxis=False,
                               customdata=t["trabalhadores"], hovertemplate="%{x:.1f} min · %{customdata:,.0f} trabalhadores<extra></extra>"))
        fig.update_xaxes(range=[0, t["tempo_medio_min"].max() * 1.4])
        grafico(layout(fig, "Tempo de casa ao trabalho por meio", "Salvador, 2022; transporte coletivo em azul", "", 520).update_layout(hovermode="closest"))
        ui.fonte("IBGE, Censo 2022, tab. 10330 (tempo estimado pelo ponto médio das faixas)")

    ui.secao("Pergunta central", "Ampliar a oferta de ônibus pioraria o trânsito?")
    ui.kpis([
        dict(rotulo="Autos adicionados (2014–2025)", valor=f"+{br(R['autos_add_2014_2025'])}", icone="carro", cor="laranja"),
        dict(rotulo="Motos adicionadas (2014–2025)", valor=f"+{br(R['motos_add_2014_2025'])}", icone="moto", cor="aqua"),
        dict(rotulo="Ônibus operacionais (2025)", valor=br(R["frota_op_2025"]), icone="onibus", cor="azul"),
        dict(rotulo="Passageiros por ônibus por dia", valor=br(R["pass_por_onibus_dia_2025"]), icone="pessoas", cor="marinho"),
    ])
    ui.nota("Não, se vier com prioridade viária",
            "Cada ônibus leva cerca de 240 passageiros pagantes por dia. O trânsito piorou pelo crescimento de quase 280 mil autos e motos, "
            "não pelos cerca de 1.840 ônibus. Mais ônibus no tráfego misto ficariam presos no mesmo congestionamento (16,5 km/h); "
            "em faixa exclusiva ou BRT andam cerca de 35% mais rápido (22,2 km/h).", cor="aqua", icone="check")
    ui.fonte("SENATRAN; Ministério das Cidades, PEMOB 2026 (velocidades declaradas pela Prefeitura)")

# ----------------------------------------------------------------------------
# 5. Salvador × capitais
# ----------------------------------------------------------------------------
with abas[4]:
    ui.secao("Salvador entre as capitais", "A capital onde mais se usa o ônibus",
             "Comparação com as 13 capitais que tinham mais de um milhão de habitantes no Censo 2022.")
    dl = D["deslocamento_capitais_censo"]
    pop22 = D["populacao_capitais"].query("ano == 2022").set_index("municipio")["populacao"]
    col1, col2 = st.columns([1, 1.05], gap="medium")
    with col1:
        fig = go.Figure()
        for nome, aneis in D["mapa"].items():
            for anel in aneis:
                xs, ys = zip(*anel)
                fig.add_scatter(x=xs, y=ys, mode="lines", fill="toself", hoverinfo="skip", showlegend=False,
                                line=dict(color="#ffffff", width=1.2), fillcolor="#e3e8ef" if nome == "Brazil" else "#f0efeb")
        dm = dl.assign(lon=dl["municipio"].map(lambda m: COORD[m][0]), lat=dl["municipio"].map(lambda m: COORD[m][1]),
                       pop=dl["municipio"].map(pop22))
        fig.add_scatter(x=dm["lon"], y=dm["lat"], mode="markers", showlegend=False,
                        marker=dict(size=np.sqrt(dm["pop"]) / 38, color=dm["pct_coletivo"], colorscale=[[0, "#cfe0f5"], [1, "#0e3a78"]],
                                    cmin=dm["pct_coletivo"].min(), cmax=dm["pct_coletivo"].max(), line=dict(color="white", width=1.5), opacity=.92,
                                    colorbar=dict(title=dict(text="% coletivo", font=dict(size=11)), thickness=10, len=.42, x=.03, xanchor="left", y=.24,
                                                  tickfont=dict(size=10), outlinewidth=0)),
                        customdata=np.stack([dm["municipio"], dm["pct_coletivo"], dm["pop"] / 1e6], axis=1),
                        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:.1f}% em transporte coletivo<br>%{customdata[2]:.2f} mi hab.<extra></extra>")
        ssa = dm[dm["municipio"] == SSA].iloc[0]
        fig.add_annotation(x=ssa["lon"], y=ssa["lat"], text=f"<b>Salvador</b><br>{br(ssa['pct_coletivo'], 1)}% coletivo", showarrow=True, arrowhead=0,
                           ax=72, ay=-12, font=dict(size=12, color=AZUL), arrowcolor=AZUL, bgcolor="rgba(255,255,255,.88)", borderpad=3)
        fig.update_xaxes(visible=False, range=[-74.5, -33])
        fig.update_yaxes(visible=False, range=[-34.5, 6.5], scaleanchor="x", scaleratio=1)
        layout(fig, "As 13 capitais do estudo", "Tamanho = população (2022); cor = % de trabalhadores no transporte coletivo", "", 540)
        fig.update_layout(hovermode="closest", margin=dict(l=0, r=0, t=74, b=0))
        grafico(fig, key="mapa_capitais")
        ui.fonte("IBGE, Censo 2022 (tab. 4709 e 10332); contornos: Natural Earth")
    with col2:
        @st.fragment
        def barras_indicador():
            opcoes = {"% em transporte coletivo": "pct_coletivo", "% de ônibus": "pct_onibus", "% de automóvel": "pct_automovel",
                      "% de moto": "pct_moto", "% a pé ou de bicicleta": "pct_ativo", "Tempo médio (min)": "tempo_medio_2022_min",
                      "% que leva mais de 1 hora": "pct_mais_1h_2022"}
            escolha = st.selectbox("Indicador do Censo 2022", list(opcoes), key="indicador")
            col = opcoes[escolha]
            dd = dl.sort_values(col)
            fig = go.Figure(go.Bar(y=dd["municipio"], x=dd[col], orientation="h",
                                   marker=dict(color=[AZUL if mu == SSA else CINZA_CLARO for mu in dd["municipio"]], cornerradius=5),
                                   text=[f"<b>{br(v, 1)}</b>" if mu == SSA else br(v, 1) for mu, v in zip(dd["municipio"], dd[col])],
                                   textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x:.1f}<extra></extra>"))
            fig.update_xaxes(range=[0, dd[col].max() * 1.18])
            grafico(layout(fig, escolha, "Trabalhadores, 2022; Salvador em azul", "", 470).update_layout(hovermode="closest"), key="barras_ind")
            ui.fonte("IBGE, Censo 2022, tab. 10330 e 10332")
        barras_indicador()

    g = D["grupos_capitais"]
    fig = go.Figure()
    x = g["pct_coletivo"]
    coef = np.polyfit(x, g["tempo_medio_2022_min"], 1)
    xx = np.linspace(x.min(), x.max(), 20)
    fig.add_scatter(x=xx, y=np.polyval(coef, xx), mode="lines", name="tendência linear", line=dict(color=CINZA, dash="dash"), hoverinfo="skip")
    for (nome, gg), cor in zip(g.groupby("grupo_nome"), [AZUL, LARANJA, AQUA]):
        fig.add_scatter(x=gg["pct_coletivo"], y=gg["tempo_medio_2022_min"], mode="markers+text", name=nome, customdata=gg["municipio"],
                        text=gg["municipio"], textposition=["middle left" if xv >= 49.5 else "top center" for xv in gg["pct_coletivo"]], cliponaxis=False,
                        marker=dict(size=[20 if m == SSA else 13 for m in gg["municipio"]], color=cor, line=dict(color="white", width=2)),
                        textfont=dict(size=11.5), hovertemplate="%{customdata}: %{x:.1f}% coletivo · %{y:.1f} min<extra></extra>")
    grafico(layout(fig, "Mais transporte coletivo, viagens mais longas", f"Grupos de capitais por k-means; Spearman ρ = {br(R['rho_coletivo_tempo'], 2)} (p < 0,001)",
                   "tempo médio casa-trabalho (min)", 460)
            .update_layout(hovermode="closest", xaxis_title="% dos trabalhadores em transporte coletivo",
                           legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", font=dict(size=11.5))))
    ui.fonte(f"IBGE, Censo 2022; regressão com densidade: R² = {br(R['ols_r2'], 2)}")

# ----------------------------------------------------------------------------
# 6. Projeções 2030
# ----------------------------------------------------------------------------
with abas[5]:
    ui.secao("Para onde vamos", "Sem mudança, 2030 terá mais carros e menos passageiros no ônibus",
             "Projeções estatísticas com as séries oficiais. Os cenários são hipóteses do projeto, não metas oficiais.")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        pm = D["projecao_motorizacao"]
        obs = base[base["ano"] >= 2014]
        fig = go.Figure()
        fig.add_scatter(x=pm["ano"], y=pm["lim_sup"], line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=pm["ano"], y=pm["lim_inf"], fill="tonexty", fillcolor="rgba(42,120,214,0.12)", line=dict(width=0), name="Intervalo 95%", hoverinfo="skip")
        fig.add_scatter(x=obs["ano"], y=obs["motorizacao_por_mil_hab"], name="Observado", mode="lines+markers", line=dict(color=AZUL, width=3), marker=dict(size=6))
        fig.add_scatter(x=pm["ano"], y=pm["linear"], name="Tendência linear", line=dict(color=AZUL, dash="dash"))
        fig.add_scatter(x=pm["ano"], y=pm["holt"], name="Holt", line=dict(color=LARANJA, dash="dash"))
        grafico(layout(fig, "Motorização projetada até 2030", f"Autos e motos por mil hab.; erro de validação (MAPE) {br(R['mape_motoriz'], 1)}%", "veículos por mil hab."))
        ui.fonte("SENATRAN e IBGE; projeção do projeto")
    with col2:
        pv = D["previsao_metro_mensal"]
        mt = D["metro_mensal"].copy()
        mt["data"] = pd.to_datetime(dict(year=mt["ano"], month=mt["mes"], day=1))
        fig = go.Figure()
        fig.add_scatter(x=mt["data"], y=mt["passageiros"] / 1e6, name="Observado (CTB)", mode="lines+markers", line=dict(color=AZUL, width=3), marker=dict(size=5))
        fig.add_scatter(x=pv["data"], y=pv["previsao_metro"] / 1e6, name="Holt-Winters", mode="lines+markers", line=dict(color=LARANJA, dash="dash"), marker=dict(size=5))
        eixo_mes_pt(fig, pd.concat([mt["data"], pv["data"]]), 6)
        grafico(layout(fig, "Metrô: previsão mensal até dez/2027", f"Milhões de passageiros por mês; MAPE de teste {br(R['mape_metro_hw'], 1)}%", "milhões/mês"))
        ui.fonte("CTB; Holt-Winters aditivo amortecido")

    ui.secao("Simulador", "Monte o seu cenário para 2030",
             "Escolha a variação anual e veja onde ônibus e metrô chegariam. Pontos de partida: ônibus 1,25 mi passageiros/dia (SEMOB, 2024) e metrô 117,5 mi/ano (CTB, 2025).")

    @st.fragment
    def simulador():
        s1, s2 = st.columns(2, gap="large")
        g_on = s1.slider("Ônibus: variação ao ano (%)", -8.0, 4.0, -3.0, 0.5, key="g_on")
        g_me = s2.slider("Metrô: variação ao ano (%)", -3.0, 6.0, 1.0, 0.5, key="g_me")
        anos_c = np.arange(2024, 2031)
        on = R["stco_pass_dia_2024"] * (1 + g_on / 100) ** (anos_c - 2024)
        me = np.where(anos_c == 2024, 117.533257e6, 117.5e6 * (1 + g_me / 100) ** (anos_c - 2025))
        v_on, v_me = (on[-1] / on[0] - 1) * 100, (me[-1] / 117.5e6 - 1) * 100
        ui.kpis([
            dict(rotulo="Ônibus em 2030 (passageiros/dia)", valor=br(on[-1] / 1e6, 2), unidade="mi", icone="onibus", cor="azul",
                 delta=f"{sinal(v_on)}%", tom="bom" if v_on > 0 else "ruim", nota="vs 2024"),
            dict(rotulo="Metrô em 2030 (passageiros/ano)", valor=br(me[-1] / 1e6, 1), unidade="mi", icone="trem", cor="aqua",
                 delta=f"{sinal(v_me)}%", tom="bom" if v_me > 0 else "ruim", nota="vs 2025"),
            dict(rotulo="População projetada em 2030", valor=br(R["pop_2030"] / 1e6, 2), unidade="mi", icone="pessoas", cor="marinho",
                 nota="tendência do IBGE"),
        ])
        cen = D["cenarios_2030"]
        fig = go.Figure()
        for nome, cor in zip(["Pessimista", "Tendencial", "Otimista"], [VERMELHO, CINZA, AQUA]):
            cc = cen[cen["cenario"] == nome]
            fig.add_scatter(x=cc["ano"], y=cc["onibus_pass_dia"] / 1e6, name=nome, line=dict(color=cor, width=1.6, dash="dot"))
        fig.add_scatter(x=anos_c, y=on / 1e6, name="Seu cenário", mode="lines+markers", line=dict(color=AZUL, width=3.5),
                        marker=dict(size=8, line=dict(color="white", width=2)))
        fig.update_yaxes(range=[0.6, 1.6])
        grafico(layout(fig, "Ônibus (STCO): passageiros por dia até 2030", "Milhões; linhas pontilhadas são os cenários do relatório", "milhões/dia", 360),
                key="sim_grafico")

    simulador()

# ----------------------------------------------------------------------------
# 7. Recomendações
# ----------------------------------------------------------------------------
with abas[6]:
    ui.secao("O que fazer", "Sete frentes de ação, cada uma com um indicador para acompanhar",
             "Recomendações para a Prefeitura (SEMOB) e o Governo do Estado (CTB), apoiadas nos resultados das análises.")
    ui.recomendacoes(D["recomendacoes"])
    ui.secao("Hipóteses testadas", "O que os dados confirmaram")
    ui.hipoteses(D["hipoteses"])

# ----------------------------------------------------------------------------
# 8. Dados e fontes
# ----------------------------------------------------------------------------
with abas[7]:
    ui.secao("Transparência", "Dados tratados e fontes oficiais",
             "Todas as tabelas usadas no painel podem ser consultadas e baixadas em CSV.")
    tabelas = {"Base anual de Salvador": "base_salvador_anual", "Base mensal de Salvador": "base_salvador_mensal",
               "Painel das capitais (2014–2025)": "painel_capitais_anual", "Deslocamento casa-trabalho (Censos)": "deslocamento_capitais_censo",
               "PEMOB das capitais": "pemob_capitais", "Valores de documentos oficiais": "fontes_documentais",
               "Dicionário de dados": "dicionario_dados"}

    @st.fragment
    def consulta():
        c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
        escolha = c1.selectbox("Tabela", list(tabelas), key="tabela")
        df = D[tabelas[escolha]]
        c2.download_button("Baixar CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{tabelas[escolha]}.csv", mime="text/csv", width="stretch")
        st.dataframe(df, width="stretch", height=380)

    consulta()
    ui.secao("Fontes", "Instituições de onde vêm os dados")
    ui.fontes_oficiais([
        ("IBGE", "Censos 2010 e 2022, Estimativas da População e IPCA (API SIDRA: tabelas 6579, 4709, 4714, 10330, 10332, 10333, 3604 e 1737)"),
        ("SENATRAN / Ministério dos Transportes", "Frota de veículos por município e tipo, dezembro de 2014 a 2025"),
        ("Ministério das Cidades", "Pesquisa Nacional de Mobilidade Urbana (PEMOB 2023 e 2026)"),
        ("SEI-BA (Governo da Bahia)", "Indicador de Movimentação Econômica de Salvador (IMEC)"),
        ("CTB e Companhia do Metrô da Bahia", "Passageiros do metrô, mensais e anuais"),
        ("Prefeitura de Salvador e ARSAL", "Tarifas, linhas, passageiros e frota do sistema de ônibus (STCO)"),
        ("Integra Salvador", "Retrato atual do sistema informado pelas concessionárias, usado só como referência"),
    ])

ui.rodape(EQUIPE, PROF, UC, LINKS)
