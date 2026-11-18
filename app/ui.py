"""Componentes visuais do painel: estilo da página, cabeçalho, cartões de indicadores e avisos.

Tudo é HTML e CSS puros (sem JavaScript), renderizados com st.html. As animações usam
apenas CSS e respeitam a preferência do sistema por menos movimento.
"""
import base64
import html
import re
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent / "assets"
MARINHO = "#0e1a33"
AZUL = "#2a78d6"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

@property --n { syntax: "<integer>"; inherits: false; initial-value: 0; }
@counter-style pad2 { system: extends decimal; pad: 2 "0"; }
@counter-style pad3 { system: extends decimal; pad: 3 "0"; }

:root {
  --marinho: #0e1a33; --marinho-2: #17284a; --azul: #2a78d6; --azul-claro: #e8f1fc;
  --laranja: #eb6834; --aqua: #1baf7a; --vermelho: #e34948; --ambar: #c98a00;
  --tinta: #0b0b0b; --tinta-2: #52514e; --cinza: #898781; --linha: #e6e4dd; --fundo: #f6f5f1;
  --cartao: #ffffff; --sombra: 0 1px 2px rgba(14,26,51,.04), 0 6px 24px rgba(14,26,51,.06);
  --sombra-alta: 0 2px 4px rgba(14,26,51,.06), 0 16px 40px rgba(14,26,51,.12);
  --curva: cubic-bezier(.16, 1, .3, 1); --fonte: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

.stApp { background: var(--fundo); font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif; color: var(--tinta); }
:is(.hero, .kpis, .secao, .fonte, .nota, .achados, .corrida, .grades, .tab-oferta, .recs, .hips, .fontes, .rodape, .lat-marca, .lat-titulo, .lat-equipe, .lat-links),
:is(.hero, .kpis, .secao, .fonte, .nota, .achados, .corrida, .grades, .tab-oferta, .recs, .hips, .fontes, .rodape, .lat-marca, .lat-titulo, .lat-equipe, .lat-links) * { font-family: var(--fonte) !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: 'Inter', system-ui, sans-serif; letter-spacing: -.02em; }
[data-testid="stHeader"] { background: transparent; height: 2.5rem; }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
[data-testid="stMainBlockContainer"], .block-container { padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1340px; }

/* ---------- barra lateral ---------- */
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--linha); }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: .4rem; }
.lat-marca { display: flex; gap: 12px; align-items: center; margin: 4px 0 18px; }
.lat-marca img { width: 46px; height: 46px; object-fit: contain; border-radius: 10px; border: 1px solid var(--linha); padding: 4px; background: #fff; }
.lat-marca b { display: block; font-size: 15px; color: var(--marinho); letter-spacing: -.01em; }
.lat-marca span { font-size: 12px; color: var(--cinza); }
.lat-titulo { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--azul); margin: 6px 0 2px; }
.lat-equipe { font-size: 12.5px; line-height: 1.65; color: var(--tinta-2); }
.lat-equipe b { color: var(--marinho); font-weight: 600; }
.lat-links a { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--marinho) !important; text-decoration: none;
  padding: 8px 10px; border-radius: 10px; border: 1px solid var(--linha); margin-bottom: 6px; transition: all .25s var(--curva); background: #fff; }
.lat-links a:hover { border-color: var(--azul); color: var(--azul) !important; transform: translateX(3px); }
.lat-links svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.8; }

/* ---------- cabeçalho ---------- */
.hero { position: relative; overflow: hidden; border-radius: 22px; color: #fff; padding: 34px 40px 0;
  background: radial-gradient(1200px 400px at 85% -20%, rgba(42,120,214,.35), transparent 60%), linear-gradient(135deg, var(--marinho) 0%, var(--marinho-2) 100%);
  box-shadow: var(--sombra-alta); animation: entra .9s var(--curva) both; }
.hero-topo { display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; position: relative; z-index: 2; }
.hero-rotulo { font-size: 11.5px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: #8fb8ee; margin-bottom: 12px; }
.hero h1 { font-size: clamp(26px, 3.2vw, 42px) !important; font-weight: 800 !important; line-height: 1.08 !important; margin: 0 0 12px !important; padding: 0 !important; color: #fff !important; max-width: 820px; }
.hero h1 em { font-style: normal; background: linear-gradient(90deg, #7fb2f0, #ffffff); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { color: #c9d6ea; font-size: 15.5px; max-width: 720px; margin: 0 0 18px; line-height: 1.55; }
.hero-logo { flex: none; background: #fff; border-radius: 16px; padding: 8px; width: 78px; height: 78px; display: grid; place-items: center; box-shadow: 0 8px 24px rgba(0,0,0,.25); }
.hero-logo img { width: 100%; height: 100%; object-fit: contain; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 6px; }
.chip { font-size: 12px; font-weight: 600; color: #dce7f7; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.06);
  padding: 5px 11px; border-radius: 999px; backdrop-filter: blur(4px); animation: entra .8s var(--curva) both; }
.chip:nth-child(2) { animation-delay: .06s } .chip:nth-child(3) { animation-delay: .12s } .chip:nth-child(4) { animation-delay: .18s }
.chip:nth-child(5) { animation-delay: .24s } .chip:nth-child(6) { animation-delay: .30s } .chip:nth-child(7) { animation-delay: .36s }
.chip i { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #45d39b; margin-right: 6px; vertical-align: 1px; box-shadow: 0 0 0 0 rgba(69,211,155,.6); animation: pulsa 2.2s infinite; }
.cidade { position: relative; height: 112px; margin: 6px -40px 0; }
.cidade svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.predios path { fill: none; stroke: rgba(143,184,238,.45); stroke-width: 1.4; }
.rua { stroke: rgba(255,255,255,.22); stroke-width: 2; stroke-dasharray: 14 12; animation: rua 1.4s linear infinite; }
.bus-anda { animation: anda 16s linear infinite; }
.bus-anda .roda { transform-box: fill-box; transform-origin: center; animation: gira .6s linear infinite; }

/* ---------- abas ---------- */
.stTabs { margin-top: 18px; }
.stTabs [role="tablist"] { gap: 4px; background: #fff; padding: 6px; border-radius: 16px; border: 1px solid var(--linha); box-shadow: var(--sombra);
  position: sticky; top: .4rem; z-index: 90; overflow-x: auto; scrollbar-width: none; border-bottom: 1px solid var(--linha) !important; }
.stTabs [role="tablist"]::-webkit-scrollbar { display: none; }
.stTabs [role="tablist"]::after, .stTabs [role="tablist"]::before { display: none !important; }
.stTabs [role="tab"] { position: relative; height: 40px; padding: 0 13px !important; margin: 0 !important; border-radius: 11px; background: transparent;
  white-space: nowrap; display: flex; align-items: center; border: 0 !important; transition: background-color .3s var(--curva); }
.stTabs [role="tab"] [data-testid="stMarkdownContainer"] { position: relative; z-index: 2; }
.stTabs [role="tab"] p { font-family: var(--fonte); font-size: 13.5px !important; font-weight: 600 !important; color: var(--tinta-2) !important; transition: color .35s var(--curva); margin: 0; }
.stTabs [role="tab"]:hover { background: #f1f5fb; }
.stTabs [role="tab"][data-selected="true"]:hover { background: transparent; }
.stTabs [role="tab"][data-selected="true"] p { color: #fff !important; }
.stTabs .react-aria-SelectionIndicator { position: absolute !important; inset: 0 !important; width: auto !important; height: auto !important; border-radius: 11px;
  background: linear-gradient(135deg, var(--marinho), #23407a) !important; box-shadow: 0 6px 16px rgba(14,26,51,.25); z-index: 1;
  transition: translate .45s var(--curva), width .45s var(--curva) !important; }
.stTabs [role="tabpanel"] { padding-top: 22px; }
.stTabs [role="tabpanel"] > div { animation: entra .6s var(--curva) both; }

/* ---------- blocos ---------- */
[data-testid="stColumn"] { animation: entra .7s var(--curva) both; }
[data-testid="stColumn"]:nth-child(2) { animation-delay: .08s } [data-testid="stColumn"]:nth-child(3) { animation-delay: .16s }
[data-testid="stColumn"]:nth-child(4) { animation-delay: .24s }
[data-testid="stPlotlyChart"] { background: var(--cartao); border: 1px solid var(--linha); border-radius: 18px; padding: 14px 16px 6px;
  box-shadow: var(--sombra); transition: box-shadow .35s var(--curva), transform .35s var(--curva); }
[data-testid="stPlotlyChart"]:hover { box-shadow: var(--sombra-alta); }
.secao { margin: 10px 0 14px; animation: entra .7s var(--curva) both; }
.secao .rot { font-size: 11.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--azul); }
.secao h3 { font-size: 23px !important; font-weight: 750 !important; color: var(--marinho) !important; margin: 4px 0 4px !important; padding: 0 !important; }
.secao p { color: var(--tinta-2); font-size: 14.5px; margin: 0; max-width: 900px; line-height: 1.55; }
.fonte { display: flex; gap: 6px; align-items: flex-start; font-size: 12px; color: var(--cinza); margin: 8px 4px 18px; line-height: 1.45; }
.fonte svg { flex: none; width: 13px; height: 13px; margin-top: 1px; stroke: currentColor; fill: none; stroke-width: 2; }

/* ---------- cartões de indicadores ---------- */
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin: 4px 0 18px; }
.kpi { position: relative; background: var(--cartao); border: 1px solid var(--linha); border-radius: 18px; padding: 18px 18px 16px; overflow: hidden;
  box-shadow: var(--sombra); transition: transform .35s var(--curva), box-shadow .35s var(--curva), border-color .35s; animation: sobe .8s var(--curva) both; }
.kpi:hover { transform: translateY(-4px); box-shadow: var(--sombra-alta); border-color: #cfdcf0; }
.kpi::after { content: ""; position: absolute; left: 0; top: 0; height: 3px; width: 100%; background: var(--cor, var(--azul)); transform-origin: left;
  animation: barra 1.2s var(--curva) .2s both; }
.kpi:nth-child(2) { animation-delay: .07s } .kpi:nth-child(3) { animation-delay: .14s } .kpi:nth-child(4) { animation-delay: .21s }
.kpi:nth-child(5) { animation-delay: .28s } .kpi:nth-child(6) { animation-delay: .35s }
.kpi-topo { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.kpi-ic { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; background: var(--fundo-ic, var(--azul-claro)); color: var(--cor, var(--azul)); flex: none; }
.kpi-ic svg { width: 19px; height: 19px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.kpi-rot { font-size: 12.5px; font-weight: 600; color: var(--tinta-2); line-height: 1.3; }
.kpi-val { font-size: 31px; font-weight: 800; color: var(--marinho); letter-spacing: -.03em; line-height: 1.05; font-variant-numeric: tabular-nums; white-space: nowrap; }
.kpi-val small { font-size: 16px; font-weight: 700; color: var(--tinta-2); margin-left: 3px; letter-spacing: 0; }
.kpi-rodape { display: flex; align-items: center; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.delta { display: inline-flex; align-items: center; gap: 3px; font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 999px; }
.delta svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 2.4; }
.delta.ruim { color: #c23634; background: #fdecec; } .delta.bom { color: #0f8a5f; background: #e5f6ef; } .delta.neutro { color: #46607f; background: #edf1f6; }
.kpi-nota { font-size: 11.5px; color: var(--cinza); }

/* números que contam até o valor */
.cn { counter-reset: n var(--n); animation: conta 1.9s var(--curva) .15s both; }
.cn::before { content: counter(n); }
.cn.c2::before { content: counter(n, pad2); }
.cn.c3::before { content: counter(n, pad3); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

/* ---------- avisos e achados ---------- */
.nota { display: flex; gap: 14px; background: var(--cartao); border: 1px solid var(--linha); border-left: 4px solid var(--cor, var(--azul)); border-radius: 14px;
  padding: 16px 18px; box-shadow: var(--sombra); margin: 4px 0 16px; animation: entra .8s var(--curva) both; }
.nota-ic { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; flex: none; background: var(--fundo-ic, var(--azul-claro)); color: var(--cor, var(--azul)); }
.nota-ic svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.nota b.t { display: block; color: var(--marinho); font-size: 15px; margin-bottom: 3px; }
.nota div.x { color: var(--tinta-2); font-size: 14px; line-height: 1.55; }
.achados { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); }
.achado { display: flex; gap: 14px; align-items: flex-start; background: var(--cartao); border: 1px solid var(--linha); border-radius: 14px; padding: 14px 16px;
  box-shadow: var(--sombra); animation: lado .8s var(--curva) both; transition: transform .3s var(--curva), border-color .3s; }
.achado:hover { transform: translateX(4px); border-color: #cfdcf0; }
.achado:nth-child(2) { animation-delay: .08s } .achado:nth-child(3) { animation-delay: .16s } .achado:nth-child(4) { animation-delay: .24s } .achado:nth-child(5) { animation-delay: .32s }
.achado .num { flex: none; width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; font-weight: 800; font-size: 13px; color: #fff; background: var(--marinho); }
.achado b.t { color: var(--marinho); font-size: 14.5px; display: block; margin-bottom: 3px; }
.achado span b { color: var(--marinho); font-weight: 700; }
.achado span { color: var(--tinta-2); font-size: 13.5px; line-height: 1.5; }

/* ---------- corrida ônibus x carro ---------- */
.corrida { background: var(--cartao); border: 1px solid var(--linha); border-radius: 18px; padding: 18px 20px; box-shadow: var(--sombra); animation: entra .8s var(--curva) both; }
.corrida h4 { margin: 0 0 2px !important; padding: 0 !important; font-size: 16px !important; color: var(--marinho) !important; font-weight: 700 !important; }
.corrida .sub { font-size: 12.5px; color: var(--cinza); margin-bottom: 14px; }
.pista { display: grid; grid-template-columns: 92px 1fr 64px; align-items: center; gap: 10px; margin: 10px 0; }
.pista .nome { font-size: 13px; font-weight: 600; color: var(--tinta-2); display: flex; align-items: center; gap: 6px; }
.pista .nome svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; }
.pista .trilho { height: 14px; background: #f0efea; border-radius: 999px; overflow: hidden; }
.pista .enche { height: 100%; width: var(--w); border-radius: 999px; background: var(--cor); transform-origin: left; animation: barra var(--d, 2s) var(--curva) .3s both; }
.pista .min { font-size: 18px; font-weight: 800; color: var(--marinho); text-align: right; font-variant-numeric: tabular-nums; }
.pista .min small { font-size: 12px; color: var(--cinza); font-weight: 600; }

/* ---------- grade de 100 viagens ---------- */
.grades { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.grade-bloco { background: var(--cartao); border: 1px solid var(--linha); border-radius: 18px; padding: 16px 18px; box-shadow: var(--sombra); }
.grade-bloco .cab { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
.grade-bloco .cab b { font-size: 14px; color: var(--marinho); }
.grade-bloco .cab span { font-size: 22px; font-weight: 800; color: var(--vermelho); }
.grade { display: grid; grid-template-columns: repeat(20, 1fr); gap: 4px; }
.grade i { aspect-ratio: 1; border-radius: 3px; background: #e4ecf7; animation: pop .5s var(--curva) both; }
.grade i.f { background: var(--vermelho); }

/* ---------- tabela de oferta ---------- */
.tab-oferta { width: 100%; border-collapse: separate; border-spacing: 0; background: var(--cartao); border: 1px solid var(--linha); border-radius: 18px; overflow: hidden; box-shadow: var(--sombra); font-size: 13.5px; }
.tab-oferta th { text-align: left; font-size: 11.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--cinza); font-weight: 700; padding: 12px 14px; background: #faf9f6; border-bottom: 1px solid var(--linha); }
.tab-oferta td { padding: 12px 14px; border-bottom: 1px solid #f0efea; color: var(--tinta); font-variant-numeric: tabular-nums; }
.tab-oferta tr:last-child td { border-bottom: 0; }
.tab-oferta tr { animation: entra .6s var(--curva) both; }
.tab-oferta tr:nth-child(2) { animation-delay: .07s } .tab-oferta tr:nth-child(3) { animation-delay: .14s } .tab-oferta tr:nth-child(4) { animation-delay: .21s }
.tab-oferta tbody tr:hover td { background: #f7f9fc; }

/* ---------- recomendações e hipóteses ---------- */
.recs { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.rec { position: relative; background: var(--cartao); border: 1px solid var(--linha); border-radius: 20px; padding: 20px 20px 18px; box-shadow: var(--sombra);
  animation: sobe .8s var(--curva) both; transition: transform .35s var(--curva), box-shadow .35s var(--curva), border-color .35s; overflow: hidden; }
.rec:hover { transform: translateY(-5px); box-shadow: var(--sombra-alta); border-color: #cfdcf0; }
.rec:nth-child(2) { animation-delay: .08s } .rec:nth-child(3) { animation-delay: .16s } .rec:nth-child(4) { animation-delay: .24s } .rec:nth-child(5) { animation-delay: .32s } .rec:nth-child(6) { animation-delay: .4s } .rec:nth-child(7) { animation-delay: .48s }
.rec .topo { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.rec .n { font-size: 11px; font-weight: 800; letter-spacing: .14em; color: var(--azul); text-transform: uppercase; }
.rec h4 { margin: 2px 0 0 !important; padding: 0 !important; font-size: 17px !important; color: var(--marinho) !important; font-weight: 750 !important; line-height: 1.25 !important; }
.rec .bloco { margin-top: 10px; }
.rec .bloco b { display: block; font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--cinza); margin-bottom: 3px; }
.rec .bloco div { font-size: 13.5px; color: var(--tinta-2); line-height: 1.5; }
.rec .meta { margin-top: 14px; display: flex; gap: 8px; align-items: flex-start; background: var(--azul-claro); color: #1d5ba8; border-radius: 12px; padding: 10px 12px; font-size: 13px; font-weight: 600; line-height: 1.45; }
.rec .meta svg { flex: none; width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 2; margin-top: 1px; }
.rec .ic-g { width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--marinho), #23407a); color: #fff; flex: none; }
.rec .ic-g svg { width: 24px; height: 24px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.hips { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.hip { background: var(--cartao); border: 1px solid var(--linha); border-radius: 16px; padding: 16px; box-shadow: var(--sombra); animation: entra .7s var(--curva) both; }
.hip:nth-child(2) { animation-delay: .07s } .hip:nth-child(3) { animation-delay: .14s } .hip:nth-child(4) { animation-delay: .21s } .hip:nth-child(5) { animation-delay: .28s } .hip:nth-child(6) { animation-delay: .35s }
.hip .id { font-size: 12px; font-weight: 800; color: var(--cinza); }
.hip .h { font-size: 14.5px; font-weight: 650; color: var(--marinho); margin: 4px 0 10px; line-height: 1.35; }
.hip .st { display: inline-block; font-size: 11.5px; font-weight: 700; padding: 3px 9px; border-radius: 999px; margin-bottom: 8px; }
.hip .st.ok { background: #e5f6ef; color: #0f8a5f; } .hip .st.parc { background: #fff4dc; color: #9a6a00; } .hip .st.fraca { background: #edf1f6; color: #46607f; } .hip .st.nao { background: #fdecec; color: #c23634; }
.hip .ev { font-size: 13px; color: var(--tinta-2); line-height: 1.5; }

/* ---------- fontes ---------- */
.fontes { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
.fnt { background: var(--cartao); border: 1px solid var(--linha); border-radius: 14px; padding: 14px 16px; box-shadow: var(--sombra); animation: entra .7s var(--curva) both; transition: border-color .3s, transform .3s var(--curva); }
.fnt:hover { border-color: #cfdcf0; transform: translateY(-2px); }
.fnt b { display: block; color: var(--marinho); font-size: 14px; margin-bottom: 4px; }
.fnt span { font-size: 12.5px; color: var(--tinta-2); line-height: 1.5; }

/* ---------- rodapé ---------- */
.rodape { margin-top: 34px; border-radius: 20px; padding: 26px 30px; color: #c9d6ea; background: linear-gradient(135deg, var(--marinho), var(--marinho-2));
  display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; font-size: 13px; line-height: 1.7; }
.rodape b { color: #fff; } .rodape .rot { font-size: 11px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: #8fb8ee; margin-bottom: 6px; }
.rodape a { color: #fff !important; text-decoration: none; border-bottom: 1px solid rgba(255,255,255,.3); }
.rodape a:hover { border-color: #fff; }

/* ---------- controles do Streamlit ---------- */
[data-testid="stSlider"] [role="slider"] { box-shadow: 0 0 0 4px rgba(42,120,214,.15); transition: box-shadow .2s; }
[data-testid="stSlider"] [role="slider"]:hover { box-shadow: 0 0 0 8px rgba(42,120,214,.18); }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid var(--linha); box-shadow: var(--sombra); }
[data-testid="stDownloadButton"] button, [data-testid="stBaseButton-secondary"] { border-radius: 10px; font-weight: 600; transition: all .25s var(--curva); }
[data-testid="stDownloadButton"] button:hover { transform: translateY(-2px); box-shadow: var(--sombra); }
[data-baseweb="select"] > div { border-radius: 10px; }
.simulador { background: var(--cartao); border: 1px solid var(--linha); border-radius: 18px; padding: 6px 4px; }

/* ---------- animação dos gráficos (Plotly) ---------- */
.js-plotly-plot .scatterlayer .js-line { stroke-dasharray: 2600; stroke-dashoffset: 2600; animation: desenha 1.8s var(--curva) .2s forwards; }
.js-plotly-plot .scatterlayer .js-line[style*="stroke-dasharray: 3px"], .js-plotly-plot .scatterlayer .js-line[style*="stroke-dasharray: 9px"],
.js-plotly-plot .scatterlayer .js-line[style*="px,"] { stroke-dasharray: none; stroke-dashoffset: 0; animation: aparece 1.2s ease .6s both; }
.js-plotly-plot .scatterlayer .points path, .js-plotly-plot .scatterlayer .textpoint { animation: aparece .6s ease 1s both; }
.js-plotly-plot .scatterlayer .js-fill { animation: aparece 1.2s ease .5s both; }
.js-plotly-plot .barlayer, .js-plotly-plot .waterfalllayer { animation: revela 1.3s var(--curva) .15s both; }

@keyframes entra { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes sobe { from { opacity: 0; transform: translateY(22px) scale(.98); } to { opacity: 1; transform: none; } }
@keyframes lado { from { opacity: 0; transform: translateX(-18px); } to { opacity: 1; transform: none; } }
@keyframes aparece { from { opacity: 0; } to { opacity: 1; } }
@keyframes barra { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes conta { from { --n: 0; } }
@keyframes pop { from { opacity: 0; transform: scale(.3); } to { opacity: 1; transform: none; } }
@keyframes desenha { to { stroke-dashoffset: 0; } }
@keyframes revela { from { clip-path: inset(0 100% 0 0); opacity: .4; } to { clip-path: inset(0 0 0 0); opacity: 1; } }
@keyframes rua { to { stroke-dashoffset: -26; } }
@keyframes anda { from { transform: translateX(-140px); } to { transform: translateX(1340px); } }
@keyframes gira { to { transform: rotate(360deg); } }
@keyframes pulsa { 0% { box-shadow: 0 0 0 0 rgba(69,211,155,.55); } 70% { box-shadow: 0 0 0 8px rgba(69,211,155,0); } 100% { box-shadow: 0 0 0 0 rgba(69,211,155,0); } }

@media (max-width: 760px) {
  .hero { padding: 24px 22px 0; } .cidade { margin: 6px -22px 0; } .hero-logo { width: 56px; height: 56px; }
  .grades, .rodape { grid-template-columns: 1fr; } .kpi-val { font-size: 27px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
  .js-plotly-plot .scatterlayer .js-line { stroke-dasharray: none; stroke-dashoffset: 0; }
}
</style>
"""

# ícones simples em traço (24 x 24)
ICONES = {
    "pessoas": '<circle cx="9" cy="7.5" r="3.2"/><path d="M2.8 20c.4-3.4 3-5.8 6.2-5.8s5.8 2.4 6.2 5.8"/><circle cx="17.2" cy="8.5" r="2.5"/><path d="M16 14.3c2.9.2 4.9 2.4 5.2 5.7"/>',
    "carro": '<path d="M3.5 16.5v-3.2l2.1-5.1c.3-.7 1-1.2 1.8-1.2h9.2c.8 0 1.5.5 1.8 1.2l2.1 5.1v3.2"/><path d="M3.5 13.3h17"/><path d="M3.5 16.5h17"/><circle cx="7.5" cy="17.2" r="1.7"/><circle cx="16.5" cy="17.2" r="1.7"/>',
    "onibus": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16"/><path d="M8 18v3M16 18v3"/><circle cx="8" cy="14.5" r=".9"/><circle cx="16" cy="14.5" r=".9"/><path d="M9 6.5h6"/>',
    "velocidade": '<path d="M3.5 17.5a8.5 8.5 0 1 1 17 0"/><path d="M12 17.5l4.2-5.4"/><circle cx="12" cy="17.5" r="1.2"/>',
    "trem": '<rect x="6" y="3" width="12" height="13.5" rx="3"/><path d="M6 10h12"/><path d="M9 20.5l-1.8-4M15 20.5l1.8-4"/><circle cx="9.5" cy="13.2" r=".8"/><circle cx="14.5" cy="13.2" r=".8"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "rota": '<circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M8.2 18H15a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h6.8"/>',
    "alerta": '<path d="M12 4l9 16H3z"/><path d="M12 10v4"/><path d="M12 17v.4"/>',
    "moto": '<circle cx="5.5" cy="16.5" r="3"/><circle cx="18.5" cy="16.5" r="3"/><path d="M5.5 16.5l4-6h5l4 6"/><path d="M13 7h3l1.5 3.5"/>',
    "check": '<circle cx="12" cy="12" r="8.5"/><path d="M8.2 12.3l2.6 2.5 5-5.2"/>',
    "grafico": '<path d="M4 20V4"/><path d="M4 20h16"/><path d="M7.5 15l3.5-4 3 2.5 5-6"/>',
    "dados": '<ellipse cx="12" cy="6" rx="7" ry="2.8"/><path d="M5 6v6c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6"/><path d="M5 12v6c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-6"/>',
    "alvo": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r=".8"/>',
    "lampada": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z"/>',
    "faixa": '<path d="M6 21L9 3M18 21L15 3"/><path d="M12 5v2.5M12 10.5V13M12 16v2.5"/>',
    "integra": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H14a4 4 0 0 1 4 4v5.5"/><path d="M15.5 13l2.5 2.5 2.5-2.5"/>',
    "escudo": '<path d="M12 3l7 3v5.5c0 4.3-3 7.9-7 9.5-4-1.6-7-5.2-7-9.5V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    "estacionar": '<rect x="4" y="3.5" width="16" height="17" rx="3.5"/><path d="M10 16.5V8h3a2.6 2.6 0 0 1 0 5.2h-3"/>',
    "moeda": '<circle cx="12" cy="12" r="8.5"/><path d="M14.8 9.2c-.5-.9-1.6-1.5-2.8-1.5-1.6 0-2.8.9-2.8 2.1 0 2.9 5.6 1.5 5.6 4.4 0 1.2-1.2 2.1-2.8 2.1-1.3 0-2.4-.6-2.9-1.6"/><path d="M12 6v1.7M12 16.3V18"/>',
    "mapa": '<path d="M3.5 6.5l5.5-2.5 6 2.5 5.5-2.5v13.5l-5.5 2.5-6-2.5-5.5 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>',
    "livro": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/>',
    "video": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9.2v5.6l4.8-2.8z"/>',
    "codigo": '<path d="M8.5 7L3.5 12l5 5M15.5 7l5 5-5 5"/>',
    "info": '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5"/><path d="M12 7.6v.4"/>',
    "seta_cima": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "seta_baixo": '<path d="M12 5v14M6 13l6 6 6-6"/>',
    "igual": '<path d="M5 9.5h14M5 14.5h14"/>',
}

CORES = {"azul": ("#2a78d6", "#e8f1fc"), "laranja": ("#eb6834", "#fdeee7"), "aqua": ("#1baf7a", "#e3f6ee"),
         "vermelho": ("#e34948", "#fdecec"), "marinho": ("#0e1a33", "#e7ebf3"), "ambar": ("#c98a00", "#fff4dc")}


def bloco(conteudo):
    """Renderiza HTML/CSS. O st.markdown mantém <style> e <svg>; tudo vai em uma linha para o Markdown não quebrar o bloco."""
    linha = re.sub(r">\s+<", "><", re.sub(r"\s*\n\s*", " ", conteudo.strip()))
    st.markdown(linha, unsafe_allow_html=True)


def ic(nome):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONES[nome]}</svg>'


def esc(t):
    return html.escape(str(t), quote=True)


def numero(texto):
    """Escreve um número formatado (ex.: '1,25', '437', '+25.346') como contadores que sobem até o valor."""
    partes = re.split(r"(\d+)", texto)
    saida = [f'<span class="sr">{esc(texto)}</span><span aria-hidden="true">']
    for i, p in enumerate(partes):
        if p.isdigit():
            anterior = partes[i - 1] if i > 0 else ""
            pad = len(p) if anterior.endswith((".", ",")) and len(p) in (2, 3) else 1
            saida.append(f'<span class="cn c{pad}" style="--n:{int(p)}"></span>')
        elif p:
            saida.append(esc(p))
    saida.append("</span>")
    return "".join(saida)


def estilo():
    bloco(CSS)


def logo_b64():
    return base64.b64encode((ASSETS / "logo_unifacs.png").read_bytes()).decode()


def cabecalho(rotulo, titulo_html, texto, chips):
    """Faixa de abertura com a cidade ao fundo e um ônibus atravessando a tela."""
    predios = ("M0 112 V70 h40 V48 h34 V70 h22 V30 h46 V70 h30 V56 h28 V70 h36 V40 h30 V20 h24 V40 h20 V70 h40 V52 h34 V70 h26 V36 h44 V70 "
               "h30 V58 h40 V70 h22 V26 h36 V70 h34 V46 h30 V70 h40 V60 h26 V70 h30 V34 h42 V70 h28 V50 h36 V70 h40 V42 h30 V70 h24 V30 h34 V70 "
               "h40 V54 h32 V70 h24 V40 h40 V70 h34 V112")
    janelas = "".join(f'<rect x="{x}" y="{y}" width="5" height="7" rx="1" fill="rgba(255,214,120,{a})"/>'
                      for x, y, a in [(108, 40, .55), (122, 52, .35), (300, 32, .45), (316, 46, .3), (488, 44, .5), (668, 36, .4),
                                      (684, 50, .25), (858, 44, .45), (1010, 40, .5), (1026, 54, .3), (1140, 50, .4)])
    onibus = ('<g class="bus-anda"><g transform="translate(0,72)">'
              '<rect x="0" y="0" width="92" height="28" rx="6" fill="#2a78d6"/>'
              '<rect x="0" y="0" width="92" height="28" rx="6" fill="url(#brilho)"/>'
              + "".join(f'<rect x="{6 + 13 * k}" y="5" width="10" height="9" rx="2" fill="#dbe9fb"/>' for k in range(6))
              + '<rect x="84" y="5" width="6" height="14" rx="2" fill="#dbe9fb"/><rect x="0" y="19" width="92" height="3" fill="#1c5fb0"/>'
              '<g class="roda"><circle cx="20" cy="29" r="5.5" fill="#0b1325"/><circle cx="20" cy="29" r="2" fill="#8a9bb8"/><path d="M20 24.5v9" stroke="#8a9bb8" stroke-width="1"/></g>'
              '<g class="roda"><circle cx="72" cy="29" r="5.5" fill="#0b1325"/><circle cx="72" cy="29" r="2" fill="#8a9bb8"/><path d="M72 24.5v9" stroke="#8a9bb8" stroke-width="1"/></g>'
              '<rect x="89" y="22" width="3" height="3" rx="1" fill="#ffd36e"/></g></g>')
    svg = (f'<svg viewBox="0 0 1200 112" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'
           '<defs><linearGradient id="brilho" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/>'
           '<stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
           f'<g class="predios"><path d="{predios}"/></g>{janelas}'
           '<line class="rua" x1="0" y1="108" x2="1200" y2="108"/>'
           f'{onibus}</svg>')
    chips_html = "".join(f'<span class="chip">{"<i></i>" if k == 0 else ""}{esc(c)}</span>' for k, c in enumerate(chips))
    bloco(f"""
<div class="hero">
  <div class="hero-topo">
    <div>
      <div class="hero-rotulo">{esc(rotulo)}</div>
      <h1>{titulo_html}</h1>
      <p>{esc(texto)}</p>
      <div class="chips">{chips_html}</div>
    </div>
    <div class="hero-logo"><img src="data:image/png;base64,{logo_b64()}" alt="UNIFACS"></div>
  </div>
  <div class="cidade">{svg}</div>
</div>""")


def secao(rotulo, titulo, texto=""):
    p = f"<p>{texto}</p>" if texto else ""
    bloco(f'<div class="secao"><div class="rot">{esc(rotulo)}</div><h3>{esc(titulo)}</h3>{p}</div>')


def fonte(txt):
    bloco(f'<div class="fonte">{ic("info")}<span>Fonte: {esc(txt)}</span></div>')


def kpis(itens):
    """itens: dicionários com rotulo, valor, unidade, icone, cor, delta, tom (bom/ruim/neutro), nota."""
    cartoes = []
    for it in itens:
        cor, fundo = CORES[it.get("cor", "azul")]
        rodape = ""
        if it.get("delta"):
            tom = it.get("tom", "neutro")
            d = it["delta"]
            seta = "seta_cima" if d.startswith("+") else "seta_baixo" if d.startswith(("-", "−")) else "igual"
            rodape += f'<span class="delta {tom}">{ic(seta)}{esc(d)}</span>'
        if it.get("nota"):
            rodape += f'<span class="kpi-nota">{esc(it["nota"])}</span>'
        un = f'<small>{esc(it["unidade"])}</small>' if it.get("unidade") else ""
        cartoes.append(f"""
<div class="kpi" style="--cor:{cor};--fundo-ic:{fundo}">
  <div class="kpi-topo"><div class="kpi-ic">{ic(it.get("icone", "grafico"))}</div><div class="kpi-rot">{esc(it["rotulo"])}</div></div>
  <div class="kpi-val">{numero(it["valor"])}{un}</div>
  <div class="kpi-rodape">{rodape}</div>
</div>""")
    bloco(f'<div class="kpis">{"".join(cartoes)}</div>')


def nota(titulo, texto_html, cor="azul", icone="lampada"):
    c, f = CORES[cor]
    bloco(f'<div class="nota" style="--cor:{c};--fundo-ic:{f}"><div class="nota-ic">{ic(icone)}</div>'
            f'<div><b class="t">{esc(titulo)}</b><div class="x">{texto_html}</div></div></div>')


def achados(itens):
    """itens: pares (título, texto em HTML)."""
    corpo = "".join(f'<div class="achado"><div class="num">{k}</div><div><b class="t">{esc(t)}</b><span>{x}</span></div></div>'
                    for k, (t, x) in enumerate(itens, 1))
    bloco(f'<div class="achados">{corpo}</div>')


def corrida(onibus_min, carro_min, titulo, sub):
    mx = max(onibus_min, carro_min)
    linhas = []
    for nome, icone, v, cor in [("Ônibus", "onibus", onibus_min, "#2a78d6"), ("Carro", "carro", carro_min, "#eb6834")]:
        w = v / mx * 100
        linhas.append(f'<div class="pista"><div class="nome">{ic(icone)}{nome}</div><div class="trilho">'
                      f'<div class="enche" style="--w:{w:.1f}%;--cor:{cor};--d:{1.2 + 1.6 * v / mx:.2f}s"></div></div>'
                      f'<div class="min">{numero(str(round(v)))}<small> min</small></div></div>')
    bloco(f'<div class="corrida"><h4>{esc(titulo)}</h4><div class="sub">{esc(sub)}</div>{"".join(linhas)}</div>')


def grades(blocos):
    """blocos: (título, percentual). Cada grade tem 100 quadrados; os pintados de vermelho são o percentual."""
    saida = []
    for titulo, pct in blocos:
        cheios = round(pct)
        quad = "".join(f'<i class="{"f" if k < cheios else ""}" style="animation-delay:{.25 + k * .012:.3f}s"></i>' for k in range(100))
        txt = f"{pct:.1f}".replace(".", ",").replace(",0", "")
        saida.append(f'<div class="grade-bloco"><div class="cab"><b>{esc(titulo)}</b><span>{txt}%</span></div><div class="grade">{quad}</div></div>')
    bloco(f'<div class="grades">{"".join(saida)}</div>')


def tabela_oferta(df, br):
    linhas = []
    for r in df.itertuples(index=False):
        var = r[3]
        bom = (var > 0) if "por 100 mil" in r[0] else (var > 0)
        tom = "bom" if bom else "ruim"
        sinal = "+" if var > 0 else ""
        linhas.append(f"<tr><td>{esc(r[0])}</td><td>{br(r[1], 1)}</td><td>{br(r[2], 1)}</td>"
                      f'<td><span class="delta {tom}">{ic("seta_cima" if var > 0 else "seta_baixo")}{sinal}{br(var, 1)}%</span></td></tr>')
    bloco('<table class="tab-oferta"><thead><tr><th>Indicador</th><th>2022</th><th>2025</th><th>Variação</th></tr></thead>'
            f'<tbody>{"".join(linhas)}</tbody></table>')


def recomendacoes(df):
    icones = ["faixa", "integra", "escudo", "estacionar", "moeda", "dados", "mapa"]
    cartoes = []
    for k, r in enumerate(df.itertuples(index=False)):
        titulo = re.sub(r"^\d+\.\s*", "", r[0])
        cartoes.append(f"""
<div class="rec">
  <div class="topo"><div class="ic-g">{ic(icones[k % len(icones)])}</div><div><div class="n">Frente {k + 1}</div><h4>{esc(titulo)}</h4></div></div>
  <div class="bloco"><b>Evidência</b><div>{esc(r[1])}</div></div>
  <div class="bloco"><b>Ação</b><div>{esc(r[2])}</div></div>
  <div class="meta">{ic("alvo")}<span>{esc(r[3])}</span></div>
</div>""")
    bloco(f'<div class="recs">{"".join(cartoes)}</div>')


def hipoteses(df):
    cartoes = []
    for r in df.itertuples(index=False):
        res = str(r[2])
        cls = "ok" if res.startswith("Confirmada") else "nao" if res.startswith("Rejeitada") else "parc" if "arcial" in res else "fraca"
        cartoes.append(f'<div class="hip"><div class="id">{esc(r[0])}</div><div class="h">{esc(r[1])}</div>'
                       f'<span class="st {cls}">{esc(res)}</span><div class="ev">{esc(r[3])}</div></div>')
    bloco(f'<div class="hips">{"".join(cartoes)}</div>')


def fontes_oficiais(itens):
    bloco('<div class="fontes">' + "".join(f'<div class="fnt"><b>{esc(t)}</b><span>{esc(x)}</span></div>' for t, x in itens) + "</div>")


def barra_lateral(equipe, prof, links):
    lk = "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{ic(i)}{esc(t)}</a>' for t, u, i in links)
    nomes = "<br>".join(esc(n) for n in equipe)
    bloco(f'''<div class="lat-marca"><img src="data:image/png;base64,{logo_b64()}" alt="UNIFACS"><div><b>Mobilidade em Salvador</b>
<span>Projeto A3 · 2010 a 2025</span></div></div>''')
    return f'''<div class="lat-titulo">Materiais</div><div class="lat-links">{lk}</div>
<div class="lat-titulo" style="margin-top:14px">Equipe</div><div class="lat-equipe"><b>{nomes}</b><br>{esc(prof)}</div>'''


def rodape(equipe, prof, uc, links):
    nomes = " · ".join(esc(n) for n in equipe)
    lk = " &nbsp;·&nbsp; ".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>' for t, u, _ in links)
    bloco(f"""
<div class="rodape">
  <div><div class="rot">Equipe</div><b>{nomes}</b><br>{esc(uc)} · Universidade Salvador (UNIFACS)<br>{esc(prof)}</div>
  <div><div class="rot">Materiais do projeto</div>{lk}<br><span style="opacity:.75">Dados de fontes oficiais: IBGE, SENATRAN, Ministério das Cidades, SEI-BA, CTB e Prefeitura de Salvador.</span></div>
</div>""")
