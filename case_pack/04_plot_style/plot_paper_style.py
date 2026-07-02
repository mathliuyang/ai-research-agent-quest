from pathlib import Path
import csv

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "solver_convergence.csv"
OUT = ROOT / "outputs"

STYLE = {
    "PINN": {"column": "pinn", "color": "#2364AA", "marker": "o", "linestyle": "-", "label": "PINN"},
    "FCM-PINN": {"column": "fcm_pinn", "color": "#D7263D", "marker": "s", "linestyle": "-", "label": "FCM-PINN"},
    "Baseline": {"column": "baseline", "color": "#111111", "marker": "^", "linestyle": "--", "label": "Baseline"},
}


def read_rows():
    with DATA.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["step"] = int(row["step"])
        for key in ["pinn", "fcm_pinn", "baseline"]:
            row[key] = float(row[key])
    return rows


def main():
    rows = read_rows()
    OUT.mkdir(exist_ok=True)

    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 10,
        "axes.linewidth": 1.4,
        "xtick.major.width": 1.2,
        "ytick.major.width": 1.2,
    })

    fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=180)
    x = [row["step"] for row in rows]
    for cfg in STYLE.values():
        y = [row[cfg["column"]] for row in rows]
        ax.plot(
            x, y,
            color=cfg["color"],
            marker=cfg["marker"],
            linestyle=cfg["linestyle"],
            linewidth=2.2,
            markersize=5,
            markeredgecolor="white",
            markeredgewidth=0.8,
            label=cfg["label"],
        )

    ax.set_xlabel("Training step")
    ax.set_ylabel("Relative error")
    ax.set_yscale("log")
    ax.grid(True, which="major", linestyle=":", linewidth=0.8, alpha=0.65)
    ax.legend(loc="upper right", frameon=True, edgecolor="black")
    fig.tight_layout()
    fig.savefig(OUT / "paper_style_plot.png", bbox_inches="tight")
    fig.savefig(OUT / "paper_style_plot.pdf", bbox_inches="tight")
    print("Wrote outputs/paper_style_plot.png")
    print("Wrote outputs/paper_style_plot.pdf")


if __name__ == "__main__":
    main()
