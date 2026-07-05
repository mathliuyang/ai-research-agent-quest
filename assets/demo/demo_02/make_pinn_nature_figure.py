from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"

mpl.rcParams.update(
    {
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.75,
        "xtick.major.width": 0.65,
        "ytick.major.width": 0.65,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


PALETTE = {
    "blue_main": "#0F4D92",
    "blue_secondary": "#3775BA",
    "teal": "#42949E",
    "violet": "#9A4D8E",
    "red_strong": "#B64342",
    "neutral_light": "#CFCECE",
    "neutral_mid": "#767676",
    "neutral_dark": "#4D4D4D",
    "neutral_black": "#272727",
    "gold": "#D8A31A",
}


ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)


def add_panel_label(ax, label, x=-0.13, y=1.04):
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="left",
        va="bottom",
        color=PALETTE["neutral_black"],
    )


def style_axis(ax, grid=True):
    if grid:
        ax.grid(axis="y", color="#E8E8E8", lw=0.5, zorder=0)
    ax.tick_params(labelsize=6.5)
    ax.xaxis.label.set_size(7)
    ax.yaxis.label.set_size(7)


def load_data():
    solution = pd.read_csv(ROOT / "pinn_ode_solution_data.csv")
    loss = pd.read_csv(ROOT / "pinn_training_loss_history.csv")
    metrics = pd.read_csv(ROOT / "pinn_epoch_metrics.csv")
    return solution, loss, metrics


def make_figure(solution, loss, metrics):
    final = loss.iloc[-1]
    max_abs_err = solution["absolute_error"].max()
    mean_abs_res = solution["pde_residual"].abs().mean()

    fig = plt.figure(figsize=(7.2, 5.15))
    gs = GridSpec(
        2,
        3,
        figure=fig,
        width_ratios=[1.35, 1.0, 1.0],
        height_ratios=[1.25, 1.0],
        wspace=0.58,
        hspace=0.48,
    )

    ax_a = fig.add_subplot(gs[0, 0:2])
    ax_b = fig.add_subplot(gs[0, 2])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    ax_e = fig.add_subplot(gs[1, 2])

    # a: hero panel, PINN solution against analytical solution and noisy data.
    obs = solution[solution["data_type"] == "observation"]
    ax_a.plot(
        solution["x"],
        solution["u_exact"],
        color=PALETTE["neutral_black"],
        lw=1.8,
        label="Analytical solution",
        zorder=4,
    )
    ax_a.plot(
        solution["x"],
        solution["u_pinn_pred"],
        color=PALETTE["blue_main"],
        lw=1.55,
        label="PINN prediction",
        zorder=5,
    )
    ax_a.scatter(
        obs["x"],
        obs["u_observed_noisy"],
        s=10,
        color=PALETTE["teal"],
        edgecolor="white",
        linewidth=0.35,
        alpha=0.72,
        label="Noisy observations",
        zorder=6,
    )
    ax_a.fill_between(
        solution["x"],
        solution["u_exact"] - solution["absolute_error"],
        solution["u_exact"] + solution["absolute_error"],
        color=PALETTE["blue_secondary"],
        alpha=0.13,
        linewidth=0,
        label="Error envelope",
        zorder=1,
    )
    ax_a.set_xlabel("Domain coordinate, x")
    ax_a.set_ylabel("Solution, u(x)")
    ax_a.set_xlim(solution["x"].min(), solution["x"].max())
    ax_a.set_ylim(-0.035, 1.08)
    ax_a.text(
        0.975,
        0.54,
        f"final relative L2 = {final['relative_l2_error']:.3g}\nmax |error| = {max_abs_err:.3g}",
        transform=ax_a.transAxes,
        ha="right",
        va="top",
        fontsize=6.5,
        color=PALETTE["neutral_dark"],
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.5},
    )
    add_panel_label(ax_a, "a", x=-0.075)
    style_axis(ax_a)
    ax_a.legend(
        loc="upper right",
        bbox_to_anchor=(0.985, 0.985),
        fontsize=5.9,
        handlelength=1.65,
        labelspacing=0.58,
        borderaxespad=0.15,
        handletextpad=0.65,
    )

    # b: loss decomposition during training.
    loss_cols = [
        ("total_loss", "total", PALETTE["neutral_black"], 1.8),
        ("pde_loss", "PDE", PALETTE["blue_main"], 1.25),
        ("initial_condition_loss", "IC", PALETTE["red_strong"], 1.1),
        ("data_loss", "data", PALETTE["teal"], 1.1),
    ]
    for col, label, color, lw in loss_cols:
        ax_b.plot(loss["epoch"], loss[col], color=color, lw=lw, label=label)
    ax_b.set_yscale("log")
    ax_b.set_xlabel("Epoch")
    ax_b.set_ylabel("Loss")
    ax_b.set_xlim(0, loss["epoch"].max())
    add_panel_label(ax_b, "b")
    style_axis(ax_b)
    ax_b.legend(fontsize=6.1, loc="upper right", handlelength=1.4)

    # c: validation metrics.
    ax_c.plot(
        loss["epoch"],
        loss["relative_l2_error"],
        color=PALETTE["violet"],
        lw=1.45,
        label="Relative L2",
    )
    ax_c.set_xlabel("Epoch")
    ax_c.set_ylabel("Relative L2 error", color=PALETTE["violet"])
    ax_c.tick_params(axis="y", labelcolor=PALETTE["violet"])
    ax_c.set_xlim(0, loss["epoch"].max())
    ax_c2 = ax_c.twinx()
    ax_c2.plot(
        loss["epoch"],
        np.sqrt(loss["validation_mse"]),
        color=PALETTE["gold"],
        lw=1.25,
        label="Validation RMSE",
    )
    ax_c2.set_ylabel("")
    ax_c2.tick_params(axis="y", labelcolor=PALETTE["gold"], labelsize=6.5)
    ax_c2.spines["top"].set_visible(False)
    ax_c2.spines["right"].set_linewidth(0.75)
    add_panel_label(ax_c, "c")
    style_axis(ax_c)
    lines = [
        Line2D([0], [0], color=PALETTE["violet"], lw=1.45, label="Relative L2"),
        Line2D([0], [0], color=PALETTE["gold"], lw=1.25, label="Validation RMSE"),
    ]
    ax_c.legend(handles=lines, fontsize=6.1, loc="upper right", handlelength=1.4)

    # d: residual along the domain.
    ax_d.axhline(0, color=PALETTE["neutral_mid"], lw=0.75, linestyle="--", zorder=1)
    ax_d.plot(
        solution["x"],
        solution["pde_residual"],
        color=PALETTE["blue_main"],
        lw=1.25,
        zorder=3,
    )
    ax_d.fill_between(
        solution["x"],
        0,
        solution["pde_residual"],
        color=PALETTE["blue_secondary"],
        alpha=0.18,
        linewidth=0,
        zorder=2,
    )
    ax_d.set_xlabel("Domain coordinate, x")
    ax_d.set_ylabel("PDE residual")
    ax_d.set_xlim(solution["x"].min(), solution["x"].max())
    ymax = np.percentile(np.abs(solution["pde_residual"]), 99) * 1.45
    ax_d.set_ylim(-ymax, ymax)
    ax_d.text(
        0.04,
        0.92,
        f"mean |residual| = {mean_abs_res:.3g}",
        transform=ax_d.transAxes,
        fontsize=6.3,
        ha="left",
        va="top",
        color=PALETTE["neutral_dark"],
    )
    add_panel_label(ax_d, "d")
    style_axis(ax_d)

    # e: checkpoint metric summary, compact endpoint evidence.
    ax_e.plot(
        metrics["epoch"],
        metrics["rmse_solution"],
        "-o",
        color=PALETTE["blue_main"],
        lw=1.25,
        ms=3.2,
        label="RMSE",
    )
    ax_e.plot(
        metrics["epoch"],
        metrics["mean_abs_pde_residual"],
        "-o",
        color=PALETTE["teal"],
        lw=1.25,
        ms=3.2,
        label="Mean |residual|",
    )
    ax_e.set_yscale("log")
    ax_e.set_xlabel("Epoch")
    ax_e.set_ylabel("Checkpoint metric")
    ax_e.set_xlim(0, metrics["epoch"].max())
    add_panel_label(ax_e, "e")
    style_axis(ax_e)
    ax_e.legend(fontsize=6.1, loc="upper right", handlelength=1.4)

    fig.suptitle(
        "PINN solution of a first-order ODE with physics-constrained convergence",
        x=0.5,
        y=0.985,
        fontsize=8.5,
        fontweight="bold",
    )
    fig.text(
        0.012,
        0.012,
        "ODE: du/dx + u = 0, u(0) = 1. Source data: solution, training loss and epoch metric CSV files.",
        fontsize=5.9,
        color=PALETTE["neutral_mid"],
    )
    return fig


def save_outputs(fig):
    base = FIG_DIR / "fig1_pinn_ode_nature"
    saved = []
    for ext, kwargs in {
        "svg": {},
        "pdf": {},
        "tiff": {"dpi": 600},
        "png": {"dpi": 300},
    }.items():
        out = base.with_suffix(f".{ext}")
        fig.savefig(out, bbox_inches="tight", **kwargs)
        saved.append(out)
    plt.close(fig)
    return saved


def write_qa_note(solution, loss, saved):
    final = loss.iloc[-1]
    note = f"""Core conclusion:
The PINN recovers the analytical ODE solution while reducing physics, initial-condition and data losses to a low-error converged state.

Figure archetype:
Quantitative grid with a hero solution panel.

Target journal/output:
Nature-family double-column style; editable SVG and PDF plus high-resolution TIFF/PNG preview.

Backend:
Python only, matplotlib.

Final size:
7.2 x 5.15 inches before tight bounding box export.

Panel map:
a: analytical solution, noisy observations and PINN prediction.
b: total, PDE, initial-condition and data loss trajectories.
c: validation RMSE and relative L2 convergence.
d: PDE residual over the computational domain.
e: checkpoint-level RMSE and residual metrics.

Source data:
pinn_ode_solution_data.csv, pinn_training_loss_history.csv, pinn_epoch_metrics.csv.

Key checks:
solution rows = {len(solution)}
loss rows = {len(loss)}
final total loss = {final['total_loss']:.6g}
final relative L2 error = {final['relative_l2_error']:.6g}
max absolute solution error = {solution['absolute_error'].max():.6g}
mean absolute PDE residual = {solution['pde_residual'].abs().mean():.6g}

Exported files:
{chr(10).join(str(p.name) for p in saved)}

Reviewer risk:
This is simulated single-run data; a formal manuscript should add random-seed or cross-run uncertainty if claiming optimizer robustness.
"""
    qa_path = FIG_DIR / "fig1_pinn_ode_nature_QA.txt"
    qa_path.write_text(note, encoding="utf-8")
    return qa_path


def main():
    solution, loss, metrics = load_data()
    fig = make_figure(solution, loss, metrics)
    saved = save_outputs(fig)
    qa_path = write_qa_note(solution, loss, saved)
    print("Saved figure outputs:")
    for path in saved:
        print(path)
    print("QA note:")
    print(qa_path)


if __name__ == "__main__":
    main()
