"""Estilo único dos gráficos do projeto (paleta acessível validada para daltonismo).

Regras: cores categóricas em ordem fixa (nunca cicladas), um único eixo Y por gráfico,
linhas de 2 px, grade discreta, e Salvador sempre na cor de destaque (azul).
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

AZUL, LARANJA, AQUA, AMARELO, MAGENTA, VERDE, VIOLETA, VERMELHO = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
CINZA = "#898781"          # séries de contexto (outras capitais) e textos secundários
CINZA_CLARO = "#c3c2b7"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
SUPERFICIE = "#fcfcfb"
GRADE = "#e1e0d9"
DESTAQUE = AZUL            # Salvador

mpl.rcParams.update({
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.labelcolor": TINTA_2, "axes.edgecolor": CINZA_CLARO,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRADE,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
    "lines.linewidth": 2, "lines.markersize": 6, "legend.frameon": False, "figure.dpi": 110,
    "axes.prop_cycle": mpl.cycler(color=[AZUL, LARANJA, AQUA, AMARELO, MAGENTA, VERDE, VIOLETA, VERMELHO]),
})


def fonte(ax, texto):
    """Escreve a fonte dos dados no rodapé do gráfico."""
    ax.annotate(f"Fonte: {texto}", xy=(0, -0.16), xycoords="axes fraction", fontsize=8, color=CINZA, ha="left", va="top")


def salvar(fig, caminho):
    """Grava a figura em PNG (usada nos relatórios) e, dentro do Jupyter/Colab, mostra o PNG na tela."""
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    try:
        from IPython import get_ipython
        from IPython.display import Image, display
        if get_ipython() is not None:
            display(Image(filename=str(caminho), width=900))
    except ImportError:
        pass


def br(v, casas=1):
    """Formata número no padrão brasileiro (1.234,5)."""
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def eixo_br(ax, eixo="y", casas=0):
    """Aplica o formato brasileiro aos rótulos numéricos de um eixo."""
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda v, _: br(v, casas))
    (ax.yaxis if eixo == "y" else ax.xaxis).set_major_formatter(fmt)


def eixo_mes(ax, meses_marca=(1, 4, 7, 10)):
    """Datas no eixo X como 'jan/24'."""
    import matplotlib.dates as mdates
    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=list(meses_marca)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    ax.xaxis.set_major_formatter(__import__("matplotlib.ticker", fromlist=["FuncFormatter"]).FuncFormatter(
        lambda v, _: f"{meses[mdates.num2date(v).month - 1]}/{mdates.num2date(v).strftime('%y')}"))
