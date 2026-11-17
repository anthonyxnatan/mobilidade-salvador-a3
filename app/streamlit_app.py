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

# ----------------------------------------------------------------------------
# Configuração e dados
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Mobilidade em Salvador", layout="wide")

DADOS = Path(__file__).resolve().parent.parent / "data" / "processed"
AZUL, LARANJA, AQUA, VERMELHO = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
CINZA, CINZA_CLARO, TINTA_2 = "#898781", "#c3c2b7", "#52514e"
SSA = "Salvador"


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
    return d


D = carregar()
R = D["R"]
base, mensal, painel = D["base_salvador_anual"], D["base_salvador_mensal"], D["painel_capitais_anual"]


def br(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def layout(fig, titulo, y="", altura=380):
    fig.update_layout(title=dict(text=titulo, x=0, font=dict(size=15)), height=altura, separators=",.",
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10),
                      legend=dict(orientation="h", y=-0.18), hovermode="x unified", yaxis_title=y,
                      font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif"))
    fig.update_xaxes(showgrid=False, linecolor=CINZA_CLARO)
    fig.update_yaxes(gridcolor="#e1e0d9", zeroline=False)
    return fig


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def eixo_mes_pt(fig, datas, passo=3):
    """Rótulos de mês em português (o Plotly usa inglês por padrão)."""
    datas = pd.Series(pd.to_datetime(datas)).drop_duplicates().sort_values()
    marcas = [d for d in datas if (d.month - 1) % passo == 0]
    fig.update_xaxes(tickvals=marcas, ticktext=[f"{MESES[d.month - 1]}/{d.strftime('%y')}" for d in marcas])
    fig.update_xaxes(hoverformat="%m/%Y")
    return fig


def fonte(txt):
    st.caption(f"Fonte: {txt}")


# ----------------------------------------------------------------------------
# Barra lateral
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Mobilidade em Salvador")
    st.markdown("Transporte público e a dinâmica da população, 2010–2025")
    st.divider()
    capitais_todas = sorted(painel["municipio"].unique())
    padrao = [SSA, "Recife", "Fortaleza", "Belo Horizonte", "Rio de Janeiro", "Curitiba"]
    sel_cap = st.multiselect("Capitais para comparar", capitais_todas, default=padrao)
    if SSA not in sel_cap:
        sel_cap = [SSA] + sel_cap
    anos = st.slider("Período (séries anuais)", 2010, 2025, (2014, 2025))
    st.divider()
    st.caption("Projeto A3, UC Análise de Dados e Big Data · UNIFACS · Prof. Eduardo Sidney da Silva Xavier")
    st.caption("Anthony Natan S. Pereira · Caio Branco Marques · Clara Gil M. de A. Santiago · "
               "Fernanda Santos da Silva · Lukas Carneiro Rocha")

st.title("Salvador encolheu, o carro cresceu e o ônibus ficou mais lento")
st.markdown("Painel interativo do projeto A3. Todos os dados vêm de fontes oficiais "
            "(IBGE, SENATRAN, Ministério das Cidades, SEI-BA, CTB, Prefeitura de Salvador).")

abas = st.tabs(["Resumo", "População e oferta", "Ônibus e metrô", "Trânsito e motorização",
                "Salvador × capitais", "Projeções 2030", "Recomendações", "Dados e fontes"])

# ----------------------------------------------------------------------------
# 1. Resumo
# ----------------------------------------------------------------------------
with abas[0]:
    c = st.columns(5)
    c[0].metric("População (Censo 2022)", help="Variação entre os Censos 2010 e 2022", value=f"{br(R['pop_2022'] / 1e6, 2)} mi", delta=f"{br(R['var_pop_2010_2022_pct'], 1)}%", delta_color="off")
    c[1].metric("Veículos por mil hab. (2025)", help="Autos + motos por mil habitantes; variação desde 2014", value=br(R["motorizacao_2025"]), delta=
                f"+{br((R['motorizacao_2025'] / R['motorizacao_2014'] - 1) * 100)}%", delta_color="inverse")
    c[2].metric("Ônibus: passageiros/dia (2024)", help="SEMOB; variação desde 2019", value=f"{br(R['stco_pass_dia_2024'] / 1e6, 2)} mi", delta=
                f"{br(R['var_pass_dia_2019_2024_pct'], 1)}%")
    c[3].metric("Ônibus: velocidade no pico", help="Tráfego misto, PEMOB; variação 2022 → 2025", value=f"{br(R['vel_2025'], 1)} km/h", delta=f"{br(R['var_vel_pct'], 0)}%")
    c[4].metric("Metrô: passageiros (2025)", "117,5 mi", "recorde, igual a 2024", delta_color="off")

    b = base[(base["ano"] >= max(anos[0], 2014)) & (base["ano"] <= anos[1])]
    fig = go.Figure()
    for col, nome, cor in [("populacao", "População", CINZA), ("autos", "Automóveis e utilitários", LARANJA), ("motos", "Motos", AQUA)]:
        fig.add_scatter(x=b["ano"], y=b[col] / b[col].iloc[0] * 100, name=nome, mode="lines+markers", line=dict(color=cor, width=2.5),
                        hovertemplate="%{y:.1f}")
    fig.add_hline(y=100, line_color=CINZA_CLARO, line_width=1)
    st.plotly_chart(layout(fig, f"Menos gente, muito mais veículos (índice {b['ano'].iloc[0]} = 100)", "índice"), width="stretch")
    fonte("SENATRAN (frota em dezembro) e IBGE (população compatibilizada)")

    st.markdown("#### O que os dados mostram")
    st.markdown(f"""
- **A população não cresceu: caiu.** Salvador perdeu **{br(-R['var_pop_2010_2022_pct'], 1)}%** dos moradores entre os Censos 2010 e 2022 e segue em queda.
- **Os veículos cresceram muito.** Desde 2014, **+{br(R['var_autos_2014_2025_pct'])}% de autos** e **+{br(R['var_motos_2014_2025_pct'])}% de motos**.
- **O ônibus perdeu {br(-R['var_pass_dia_2019_2024_pct'])}% dos passageiros** entre 2019 e 2024. A queda da população explica só
  **{br(R['ef_pop_pct'])}%** dessa perda; o metrô, no máximo, **{br(R['ef_metro_pct'])}%**.
- **O ônibus ficou mais lento e menos confiável.** A velocidade no pico caiu de {br(R['vel_2022'], 1)} para {br(R['vel_2025'], 1)} km/h, e as viagens não completadas subiram de {br(R['nao_completadas_2022'], 0)}% para {br(R['nao_completadas_2025'], 1)}%.
- **Quem depende do ônibus perde tempo.** A viagem casa-trabalho de ônibus leva **{br(R['tempo_onibus_min'])} min**, contra **{br(R['tempo_auto_min'])} min** de carro (Censo 2022).
""")

# ----------------------------------------------------------------------------
# 2. População e oferta
# ----------------------------------------------------------------------------
with abas[1]:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        p = D["populacao_capitais"]
        p = p[(p["municipio"] == SSA) & (p["ano"] <= 2026)]
        fig = go.Figure()
        fig.add_scatter(x=p["ano"], y=p["populacao"], name="Série compatibilizada (usada)", line=dict(color=AZUL, width=2.5),
                        hovertemplate="%{y:,.0f}")
        q = p.dropna(subset=["pop_estimativa_oficial"])
        fig.add_scatter(x=q["ano"], y=q["pop_estimativa_oficial"], name="Estimativa oficial publicada", mode="lines+markers",
                        line=dict(color=CINZA, dash="dot"), hovertemplate="%{y:,.0f}")
        fig.update_yaxes(tickformat=",.0f")
        st.plotly_chart(layout(fig, "População de Salvador: a série oficial muda de base em 2022 e 2024", "habitantes"),
                        width="stretch")
        fonte("IBGE, Censos 2010/2022 e Estimativas (tab. 6579 e 4709); compatibilização do projeto")
    with col2:
        st.markdown("#### A oferta acompanhou a população?")
        o = D["oferta_indicadores"].copy()
        o["2022"] = o["2022"].map(lambda v: br(v, 1))
        o["2025"] = o["2025"].map(lambda v: br(v, 1))
        o["variação_%"] = o["variação_%"].map(lambda v: f"{'+' if v > 0 else ''}{br(v, 1)}%")
        st.dataframe(o, hide_index=True, width="stretch")
        fonte("Ministério das Cidades, PEMOB 2023 e 2026 (anos-base 2022 e 2025); IBGE")
        st.info("**Em quantidade, sim**: ônibus por habitante até subiu, porque a população caiu. **Em qualidade, não**: "
                "menos km por habitante, ônibus mais lentos e mais viagens não completadas.")
    st.markdown("#### Habitantes por linha de ônibus")
    c1, c2, c3 = st.columns(3)
    c1.metric("2017 (530 linhas)", br(R["hab_por_linha_2017"]))
    c2.metric("Atual (515 linhas, Integra)", br(R["hab_por_linha_atual"]), f"{br((R['hab_por_linha_atual'] / R['hab_por_linha_2017'] - 1) * 100, 1)}%",
              delta_color="off")
    c3.metric("Ônibus por 100 mil hab. (2025)", br(R["onibus_100mil_2025"], 1), f"+{br(R['onibus_100mil_2025'] - R['onibus_100mil_2022'], 1)} vs 2022",
              delta_color="off")
    fonte("Prefeitura de Salvador (Relatório de Atividades 2017), Integra Salvador (site, acesso nov/2026), PEMOB, IBGE")

# ----------------------------------------------------------------------------
# 3. Ônibus e metrô
# ----------------------------------------------------------------------------
with abas[2]:
    col1, col2 = st.columns(2)
    with col1:
        met = base.dropna(subset=["metro_passageiros_ano"])
        fig = go.Figure(go.Bar(x=met["ano"], y=met["metro_passageiros_ano"] / 1e6, marker_color=[CINZA_CLARO if a in (2020, 2021) else AZUL for a in met["ano"]],
                               text=(met["metro_passageiros_ano"] / 1e6).map(lambda v: br(v, 1)), textposition="outside", cliponaxis=False, hovertemplate="%{y:.1f} milhões"))
        st.plotly_chart(layout(fig, "Metrô: passageiros por ano (milhões)", "milhões"), width="stretch")
        fonte("Cia. do Metrô da Bahia (demonstrações financeiras) e CTB; anos de pandemia em cinza; 2018, 2020–2022 e 2025 arredondados pela fonte")
    with col2:
        dq = D["decomposicao_queda"]
        fig = go.Figure(go.Waterfall(
            x=["2019", "População", "Metrô (hip. máx.)", "Outros fatores", "2024"], measure=["absolute", "relative", "relative", "relative", "total"],
            y=[R["stco_pass_dia_2019"] / 1e3] + list(-dq["passageiros_dia"] / 1e3) + [0],
            decreasing=dict(marker=dict(color=VERMELHO)), totals=dict(marker=dict(color=AZUL)), connector=dict(line=dict(color=CINZA_CLARO)),
            hovertemplate="%{y:,.0f} mil"))
        fig.update_yaxes(range=[1000, 1550])
        fig.update_xaxes(type="category")
        st.plotly_chart(layout(fig, "Ônibus: para onde foram 250 mil passageiros/dia (2019 → 2024)?", "mil passageiros/dia"), width="stretch")
        fonte("SEMOB (passageiros/dia), IBGE (população), CTB (metrô); decomposição do projeto")

    m = mensal.dropna(subset=["indice_metro_2024_100"])
    periodo = st.select_slider("Meses exibidos", options=list(m["data"].dt.strftime("%m/%Y")),
                               value=(m["data"].dt.strftime("%m/%Y").iloc[0], m["data"].dt.strftime("%m/%Y").iloc[-1]))
    ini, fim = [pd.to_datetime(x, format="%m/%Y") for x in periodo]
    mm = m[(m["data"] >= ini) & (m["data"] <= fim)]
    fig = go.Figure()
    fig.add_scatter(x=mm["data"], y=mm["indice_onibus_2024_100"], name="Ônibus urbanos (SEI-BA/IMEC)", mode="lines+markers", line=dict(color=AZUL),
                    hovertemplate="%{y:.1f}")
    fig.add_scatter(x=mm["data"], y=mm["indice_metro_2024_100"], name="Metrô (CTB)", mode="lines+markers", line=dict(color=LARANJA), hovertemplate="%{y:.1f}")
    fig.add_hline(y=100, line_color=CINZA_CLARO, line_width=1)
    eixo_mes_pt(fig, mm["data"], 3 if len(mm) > 12 else 1)
    st.plotly_chart(layout(fig, f"Passageiros por mês, índice (média de 2024 = 100), correlação r = {br(R['corr_mensal_onibus_metro'], 2)}", "índice"),
                    width="stretch")
    fonte("SEI-BA, IMEC (dados SETPS); CTB, demonstrativo mensal do metrô")

# ----------------------------------------------------------------------------
# 4. Trânsito e motorização
# ----------------------------------------------------------------------------
with abas[3]:
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        pc = painel[(painel["municipio"].isin(sel_cap)) & (painel["ano"].between(*anos))]
        for mu, g in pc.groupby("municipio"):
            fig.add_scatter(x=g["ano"], y=g["motorizacao_por_mil_hab"], name=mu, mode="lines",
                            line=dict(color=AZUL if mu == SSA else CINZA_CLARO, width=3 if mu == SSA else 1.5),
                            hovertemplate=f"{mu}: " + "%{y:.0f}<extra></extra>")
        st.plotly_chart(layout(fig, "Autos + motos por mil habitantes (Salvador em azul)", "veículos por mil hab.").update_layout(hovermode="closest"),
                        width="stretch")
        fonte("SENATRAN e IBGE; frota de dezembro de cada ano")
    with col2:
        t = D["tempo_medio_por_meio_censo2022"]
        t = t[(t["municipio"] == SSA) & (t["trabalhadores"] > 5000)].sort_values("tempo_medio_min")
        coletivos = {"Ônibus", "Trem ou metrô", "Van, perua ou assemelhados", "BRT ou ônibus de trânsito rápido"}
        fig = go.Figure(go.Bar(y=t["meio_transporte"], x=t["tempo_medio_min"], orientation="h",
                               marker_color=[AZUL if x in coletivos else CINZA_CLARO for x in t["meio_transporte"]],
                               text=t["tempo_medio_min"].round(0).astype(int).astype(str) + " min", textposition="outside", cliponaxis=False,
                               customdata=t["trabalhadores"], hovertemplate="%{x:.1f} min · %{customdata:,.0f} trabalhadores<extra></extra>"))
        fig.update_xaxes(range=[0, t["tempo_medio_min"].max() * 1.18])
        st.plotly_chart(layout(fig, "Salvador: tempo médio de casa ao trabalho por meio (2022)", "").update_layout(hovermode="closest"),
                        width="stretch")
        fonte("IBGE, Censo 2022, tab. 10330 (tempo estimado pelo ponto médio das faixas)")
    st.markdown("#### Ampliar a oferta de ônibus pioraria o trânsito?")
    c = st.columns(4)
    c[0].metric("Autos adicionados (2014–2025)", f"+{br(R['autos_add_2014_2025'])}")
    c[1].metric("Motos adicionadas (2014–2025)", f"+{br(R['motos_add_2014_2025'])}")
    c[2].metric("Ônibus operacionais (2025)", br(R["frota_op_2025"]))
    c[3].metric("Passageiros por ônibus/dia (2025)", br(R["pass_por_onibus_dia_2025"]))
    st.success("**Não, se vier com prioridade viária.** Cada ônibus leva ~240 passageiros pagantes por dia; o trânsito piorou "
               "pelo crescimento de quase 280 mil autos e motos, não pelos ~1.840 ônibus. Mais ônibus no tráfego misto ficariam presos no "
               "mesmo congestionamento (16,5 km/h); em faixa exclusiva/BRT andam ~35% mais rápido (22,2 km/h).")
    fonte("SENATRAN; Ministério das Cidades, PEMOB 2026 (velocidades declaradas pela Prefeitura)")

# ----------------------------------------------------------------------------
# 5. Salvador × capitais
# ----------------------------------------------------------------------------
with abas[4]:
    dl = D["deslocamento_capitais_censo"]
    col1, col2 = st.columns(2)
    with col1:
        opcoes = {"% em transporte coletivo": "pct_coletivo", "% de ônibus": "pct_onibus", "% de automóvel": "pct_automovel",
                  "% de moto": "pct_moto", "% a pé ou de bicicleta": "pct_ativo", "tempo médio (min)": "tempo_medio_2022_min",
                  "% que leva mais de 1 hora": "pct_mais_1h_2022"}
        escolha = st.selectbox("Indicador do Censo 2022", list(opcoes))
        col = opcoes[escolha]
        dd = dl[dl["municipio"].isin(sel_cap)].sort_values(col)
        fig = go.Figure(go.Bar(y=dd["municipio"], x=dd[col], orientation="h", marker_color=[AZUL if mu == SSA else CINZA_CLARO for mu in dd["municipio"]],
                               text=dd[col].map(lambda v: br(v, 1)), textposition="outside", cliponaxis=False, hovertemplate="%{x:.1f}<extra></extra>"))
        fig.update_xaxes(range=[0, dd[col].max() * 1.15])
        st.plotly_chart(layout(fig, f"{escolha}, trabalhadores (2022)", "").update_layout(hovermode="closest"), width="stretch")
        fonte("IBGE, Censo 2022, tab. 10330 e 10332")
    with col2:
        g = D["grupos_capitais"]
        fig = go.Figure()
        for (nome, gg), cor in zip(g.groupby("grupo_nome"), [AZUL, LARANJA, AQUA]):
            fig.add_scatter(x=gg["pct_coletivo"], y=gg["tempo_medio_2022_min"], mode="markers+text", name=nome, customdata=gg["municipio"],
                            text=[m if m in sel_cap else "" for m in gg["municipio"]], textposition="top center", cliponaxis=False, marker=dict(size=12, color=cor, line=dict(color="white", width=2)),
                            hovertemplate="%{customdata}: %{x:.1f}% coletivo · %{y:.1f} min<extra></extra>")
        x = g["pct_coletivo"]
        coef = np.polyfit(x, g["tempo_medio_2022_min"], 1)
        xx = np.linspace(x.min(), x.max(), 20)
        fig.add_scatter(x=xx, y=np.polyval(coef, xx), mode="lines", name="tendência linear", line=dict(color=CINZA, dash="dash"), hoverinfo="skip")
        st.plotly_chart(layout(fig, "Mais coletivo, viagens mais longas (grupos k-means)", "tempo médio casa-trabalho (min)", 430)
                        .update_layout(hovermode="closest", xaxis_title="% dos trabalhadores em transporte coletivo"), width="stretch")
        fonte(f"IBGE, Censo 2022; Spearman ρ = {br(R['rho_coletivo_tempo'], 2)} (p < 0,001); regressão com densidade: R² = {br(R['ols_r2'], 2)}")

# ----------------------------------------------------------------------------
# 6. Projeções 2030
# ----------------------------------------------------------------------------
with abas[5]:
    col1, col2 = st.columns(2)
    with col1:
        pm = D["projecao_motorizacao"]
        obs = base[base["ano"] >= 2014]
        fig = go.Figure()
        fig.add_scatter(x=obs["ano"], y=obs["motorizacao_por_mil_hab"], name="Observado", mode="lines+markers", line=dict(color=AZUL))
        fig.add_scatter(x=pm["ano"], y=pm["lim_sup"], line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=pm["ano"], y=pm["lim_inf"], fill="tonexty", fillcolor="rgba(42,120,214,0.12)", line=dict(width=0), name="Intervalo 95%", hoverinfo="skip")
        fig.add_scatter(x=pm["ano"], y=pm["linear"], name="Tendência linear", line=dict(color=AZUL, dash="dash"))
        fig.add_scatter(x=pm["ano"], y=pm["holt"], name="Holt", line=dict(color=LARANJA, dash="dash"))
        st.plotly_chart(layout(fig, "Motorização projetada até 2030", "autos + motos por mil hab."), width="stretch")
        fonte(f"Projeção do projeto (MAPE de validação = {br(R['mape_motoriz'], 1)}%)")
    with col2:
        pv = D["previsao_metro_mensal"]
        mt = D["metro_mensal"]
        mt["data"] = pd.to_datetime(dict(year=mt["ano"], month=mt["mes"], day=1))
        fig = go.Figure()
        fig.add_scatter(x=mt["data"], y=mt["passageiros"] / 1e6, name="Observado (CTB)", mode="lines+markers", line=dict(color=AZUL))
        fig.add_scatter(x=pv["data"], y=pv["previsao_metro"] / 1e6, name="Holt-Winters", mode="lines+markers", line=dict(color=LARANJA, dash="dash"))
        eixo_mes_pt(fig, pd.concat([mt["data"], pv["data"]]), 6)
        st.plotly_chart(layout(fig, "Metrô: previsão mensal até dez/2027 (milhões)", "milhões/mês"), width="stretch")
        fonte(f"CTB; Holt-Winters aditivo amortecido (MAPE de teste = {br(R['mape_metro_hw'], 1)}%)")

    st.markdown("#### Simulador de cenários para 2030")
    st.caption("Escolha a variação anual e veja onde ônibus e metrô chegariam. Pontos de partida: ônibus 1,25 mi passageiros/dia (SEMOB, 2024) e metrô 117,5 mi/ano (CTB, 2025).")
    s1, s2 = st.columns(2)
    g_on = s1.slider("Ônibus: variação ao ano (%)", -8.0, 4.0, -3.0, 0.5)
    g_me = s2.slider("Metrô: variação ao ano (%)", -3.0, 6.0, 1.0, 0.5)
    anos_c = np.arange(2024, 2031)
    on = R["stco_pass_dia_2024"] * (1 + g_on / 100) ** (anos_c - 2024)
    me = np.where(anos_c == 2024, 117.533257e6, 117.5e6 * (1 + g_me / 100) ** (anos_c - 2025))
    k = st.columns(3)
    k[0].metric("Ônibus em 2030 (passageiros/dia)", f"{br(on[-1] / 1e6, 2)} mi", f"{br((on[-1] / on[0] - 1) * 100, 1)}% vs 2024")
    k[1].metric("Metrô em 2030 (passageiros/ano)", f"{br(me[-1] / 1e6, 1)} mi", f"{br((me[-1] / 117.5e6 - 1) * 100, 1)}% vs 2025")
    k[2].metric("População projetada em 2030", f"{br(R['pop_2030'] / 1e6, 2)} mi", "tendência do IBGE", delta_color="off")
    cen = D["cenarios_2030"]
    fig = go.Figure()
    for nome, cor in zip(["Pessimista", "Tendencial", "Otimista"], [VERMELHO, CINZA, AQUA]):
        cc = cen[cen["cenario"] == nome]
        fig.add_scatter(x=cc["ano"], y=cc["onibus_pass_dia"] / 1e6, name=nome, line=dict(color=cor, width=1.5, dash="dot"))
    fig.add_scatter(x=anos_c, y=on / 1e6, name="Seu cenário", line=dict(color=AZUL, width=3))
    st.plotly_chart(layout(fig, "Ônibus (STCO): passageiros por dia até 2030 (milhões)", "milhões/dia", 340), width="stretch")

# ----------------------------------------------------------------------------
# 7. Recomendações
# ----------------------------------------------------------------------------
with abas[6]:
    st.markdown("### O que fazer: recomendações para a Prefeitura (SEMOB) e o Governo do Estado (CTB)")
    for r in D["recomendacoes"].itertuples():
        with st.expander(r[1], expanded=r.Index == 0):
            st.markdown(f"**Evidência:** {r[2]}\n\n**Ação:** {r[3]}\n\n**Indicador para acompanhar:** {r[4]}")
    st.markdown("### Hipóteses testadas")
    st.table(D["hipoteses"].set_index("id"))

# ----------------------------------------------------------------------------
# 8. Dados e fontes
# ----------------------------------------------------------------------------
with abas[7]:
    tabelas = {"Base anual de Salvador": "base_salvador_anual", "Base mensal de Salvador": "base_salvador_mensal",
               "Painel das capitais (2014–2025)": "painel_capitais_anual", "Deslocamento casa-trabalho (Censos)": "deslocamento_capitais_censo",
               "PEMOB das capitais": "pemob_capitais", "Valores de documentos oficiais": "fontes_documentais",
               "Dicionário de dados": "dicionario_dados"}
    escolha = st.selectbox("Tabela", list(tabelas))
    df = D[tabelas[escolha]]
    st.dataframe(df, width="stretch", height=380)
    st.download_button("Baixar CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{tabelas[escolha]}.csv", mime="text/csv")
    st.markdown("""
#### Fontes oficiais usadas
- **IBGE**: Censos 2010 e 2022, Estimativas da População, IPCA (API SIDRA: tabelas 6579, 4709, 4714, 10330, 10332, 10333, 3604, 1737)
- **SENATRAN / Ministério dos Transportes**: frota de veículos por município e tipo (dezembro de 2014 a 2025)
- **Ministério das Cidades**: Pesquisa Nacional de Mobilidade Urbana (PEMOB 2023 e 2026)
- **SEI-BA (Governo da Bahia)**: Indicador de Movimentação Econômica de Salvador (IMEC)
- **CTB (Governo da Bahia)** e **Companhia do Metrô da Bahia**: passageiros do metrô
- **Prefeitura de Salvador (SEMOB, Casa Civil)** e **ARSAL**: tarifas, linhas, passageiros e frota do STCO
- **Integra Salvador** (concessionárias): retrato atual do sistema, usado só como referência
""")
