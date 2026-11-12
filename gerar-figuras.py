"""Figuras do artigo a partir de resultados preservados; sem simular ou enviar jobs.

Executar depois de reavaliar.py para restaurar a versão editorial do gráfico.
Saídas exclusivamente em figuras/: PDFs vetoriais, PNGs e manifesto de fontes.
"""
import base64
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figuras"
BLUE = "#205778"
GRAY = "#687179"
OCHRE = "#A47735"
INK = "#252A2E"
GRID = "#E2E5E7"
VARIANTS = (
    ("original", "Original", GRAY, "o", "-"),
    ("cancelado", "Cancelamento", OCHRE, "s", "--"),
    ("gray_cancelado", "Gray + cancelamento", BLUE, "^", "-"),
)
SOURCE_FILES = (
    "revisao/resumo.csv", "revisao/probabilidades.csv", "revisao/protocolo.json", "revisao/validacao.json",
    "dados/ibm-result.json", "dados/ibm.json", "dados/entrada.json",
)


def decimal(value, digits=2):
    return f"{value:.{digits}f}".replace(".", ",")


def wilson(successes, trials):
    """Intervalo marginal de Wilson, 95%, sem correção simultânea."""
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / denominator
    return center - half, center + half


def read_csv(relative):
    with (ROOT / relative).open(newline="") as handle:
        return list(csv.DictReader(handle))


def style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIXGeneral"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.edgecolor": GRAY,
        "axes.linewidth": .6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.major.width": .6,
        "ytick.major.width": .6,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })


def save(fig, name):
    # Fixed physical dimensions: no bbox_inches='tight' rescaling at export.
    fig.savefig(FIGURES / f"{name}.pdf", metadata={"Title": name, "Creator": "gerar-figuras.py"})
    fig.savefig(FIGURES / f"{name}.png", dpi=300)
    fig.savefig(FIGURES / f"{name}-96dpi.png", dpi=96)
    dimensions = {"width_inches": float(fig.get_figwidth()), "height_inches": float(fig.get_figheight())}
    plt.close(fig)
    return dimensions


def noise_plot():
    summaries = read_csv("revisao/resumo.csv")
    probabilities = read_csv("revisao/probabilidades.csv")
    protocol = json.loads((ROOT / "revisao/protocolo.json").read_text())
    levels = sorted(float(value) for value in protocol["noise_levels"])
    assert len(set(levels)) == len(levels) and levels[0] == 0
    assert len(summaries) == len(VARIANTS) * len(levels)
    assert len(probabilities) == 4 * len(summaries)
    series = {}
    for variant, *_ in VARIANTS:
        values = []
        for noise in levels:
            raw = [row for row in probabilities if row["variant"] == variant and float(row["noise"]) == noise]
            assert {int(row["target"]) for row in raw} == {0, 1, 2, 3} and len(raw) == 4
            matches = [row for row in summaries if row["variant"] == variant and float(row["noise"]) == noise]
            assert len(matches) == 1
            p_min = min(float(row["p"]) for row in raw)
            assert math.isclose(p_min, float(matches[0]["p_min"]), abs_tol=1e-12)
            assert -.000000001 <= p_min <= 1.000000001
            values.append(p_min)
        assert math.isclose(values[0], 1, abs_tol=1e-12)
        series[variant] = values

    validation = json.loads((ROOT / "revisao/validacao.json").read_text())
    baseline = validation["classical_mean_promised_one"]
    assert math.isclose(baseline, 2.25)
    threshold = 100 * (2 / baseline)
    assert math.isclose(threshold / 100, validation["threshold_restart_protocol"])
    fig, ax = plt.subplots(figsize=(6.95, 3.45))
    fig.subplots_adjust(left=.115, right=.975, bottom=.19, top=.84)
    ax.set_axisbelow(True)
    for variant, label, color, marker, linestyle in VARIANTS:
        ax.plot(levels[1:], 100 * np.asarray(series[variant][1:]), color=color,
                linewidth=1.55, linestyle=linestyle, marker=marker,
                markersize=4.5, markerfacecolor="white", markeredgewidth=1.1,
                label=label, zorder=3)
    ax.axhline(threshold, color=INK, linewidth=.85, linestyle=(0, (4, 3)), zorder=1)
    ax.set_xscale("log")
    ticks = [.001, .003, .01, .03, .1]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="x", which="minor", length=2, width=.4, color=GRID)
    ax.set(xlim=(.00085, .118), ylim=(0, 105), yticks=[0, 25, 50, 75, 100],
           xlabel=r"Despolarização por porta CX, $\lambda$ (escala logarítmica)",
           ylabel="Menor probabilidade de acerto\nentre os quatro alvos (%)")
    ax.legend(loc="lower left", bbox_to_anchor=(-.005, 1.035), ncol=3,
              frameon=False, fontsize=9.5, handlelength=2.3, columnspacing=1.8, borderaxespad=0)
    dimensions = save(fig, "revisao-ruido")
    return {**dimensions, "threshold_percent": threshold, "simulation": "density_matrix_exact_probabilities",
            "confidence_intervals": False, "ideal_separate_from_log_axis": True,
            "primary_lambda": .003,
            "primary_p_min": {v: series[v][levels.index(.003)] for v, *_ in VARIANTS}}


def hardware_plot():
    meta = json.loads((ROOT / "dados/ibm.json").read_text())
    raw = json.loads((ROOT / "dados/ibm-result.json").read_text())
    register = raw["data"][0]["results"]["registro"]
    assert meta["id"] == "dbn7m95t7fqc73aj2l80", "Este gráfico é somente da execução histórica."
    assert register["shape"] == [2048, 2] and register["dtype"] == "bool"
    packed = np.frombuffer(base64.b64decode(register["data"], validate=True), dtype=np.uint8)
    assert packed.size == 512
    bits = np.unpackbits(packed).reshape(2048, 2)
    counts = dict(Counter("".join(map(str, pair)) for pair in bits))
    assert counts == meta["counts"] == {"00": 236, "01": 331, "10": 384, "11": 1097}
    assert hashlib.sha256((ROOT / "dados/entrada.json").read_bytes()).hexdigest() == meta["input_sha256"]
    entry = json.loads((ROOT / "dados/entrada.json").read_text())
    targets = [row["index"] for row in entry["records"] if row["rdv"] != row["bu_test"]]
    assert targets == [1]
    trials = sum(counts.values())
    positions = ["00", "01", "10", "11"]
    proportions = np.array([counts[key] / trials for key in positions])
    intervals = np.array([wilson(counts[key], trials) for key in positions])
    y = 100 * proportions
    yerr = 100 * np.stack([proportions - intervals[:, 0], intervals[:, 1] - proportions])

    fig, ax = plt.subplots(figsize=(3.4, 2.8))
    fig.subplots_adjust(left=.17, right=.97, bottom=.20, top=.85)
    ax.set_axisbelow(True)
    x = np.arange(4)
    ax.bar(x, y, width=.55, color=[GRAY, BLUE, GRAY, OCHRE], zorder=2)
    ax.errorbar(x, y, yerr=yerr, fmt="none", ecolor=INK, elinewidth=.8,
                capsize=2.5, capthick=.8, zorder=4)
    for index, value in enumerate(y):
        ax.text(index, 100 * intervals[index, 1] + .4, decimal(value) + "%",
                ha="center", va="bottom", fontsize=9,
                bbox={"facecolor": "white", "edgecolor": "none", "pad": .4})
    ax.axhline(25, color=GRAY, linewidth=.85, linestyle=(0, (4, 3)), zorder=1)
    ax.text(-.44, 26.2, "Escolha uniforme: 25%", ha="left", va="bottom", fontsize=8.5,
            color=GRAY, bbox={"facecolor": "white", "edgecolor": "none", "pad": .5})
    ax.set(xticks=x, xticklabels=["00", "01 (alvo)", "10", "11"],
           xlim=(-.55, 3.55), ylim=(0, 64), yticks=[0, 20, 40, 60],
           xlabel="Índice medido", ylabel="Frequência observada (%)")
    ax.text(0, 1.075, "IBM · 6 nov. 2026 · 2.048 medições", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=9.5)
    dimensions = save(fig, "ibm-anterior")
    return {**dimensions, "job": meta["id"], "shots": trials, "counts": counts,
            "target": "01", "confidence_intervals": "marginal Wilson 95%, not simultaneous",
            "wilson95": {key: intervals[i].tolist() for i, key in enumerate(positions)},
            "ideal_not_plotted_as_observations": True}


def main():
    FIGURES.mkdir(exist_ok=True)
    style()
    results = {"revisao-ruido": noise_plot(), "ibm-anterior": hardware_plot()}
    results["source_sha256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                for name in SOURCE_FILES}
    (FIGURES / "manifesto-figuras.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print("Geradas figuras/revisao-ruido e figuras/ibm-anterior em PDF e PNG.")


if __name__ == "__main__":
    main()
