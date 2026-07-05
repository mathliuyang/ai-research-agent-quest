import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def graded_mesh(alpha, n_steps, T):
    r = 3.0 / (2.0 * alpha)
    n = np.arange(n_steps + 1, dtype=float)
    return T * (n / n_steps) ** r


def interp_weights(t, alpha):
    """Weights for int_0^t[n+1] (t[n+1]-s)^(alpha-1) F(s) ds.

    On [t[j], t[j+1]], F is linearly interpolated from F[j], F[j+1].
    W0[n,j] multiplies F[j] and W1[n,j] multiplies F[j+1] for target t[n+1].
    """
    n_steps = len(t) - 1
    W0 = np.zeros((n_steps, n_steps), dtype=float)
    W1 = np.zeros((n_steps, n_steps), dtype=float)
    for n in range(n_steps):
        target = t[n + 1]
        for j in range(n + 1):
            tau = t[j + 1] - t[j]
            A = target - t[j]
            B = target - t[j + 1]
            # Stable closed forms of the two linear basis integrals.
            pow_a = A**alpha
            pow_b = B**alpha if B > 0.0 else 0.0
            pow_a1 = A ** (alpha + 1.0)
            pow_b1 = B ** (alpha + 1.0) if B > 0.0 else 0.0
            common0 = (pow_a1 - pow_b1) / (alpha + 1.0)
            common1 = (pow_a - pow_b) / alpha
            W0[n, j] = (common0 - B * common1) / tau
            W1[n, j] = (A * common1 - common0) / tau
    return W0, W1


def predictor_extrap_weights(t, alpha):
    n_steps = len(t) - 1
    B0 = np.zeros(n_steps, dtype=float)
    B1 = np.zeros(n_steps, dtype=float)
    for n in range(1, n_steps):
        tau_prev = t[n] - t[n - 1]
        tau_next = t[n + 1] - t[n]
        B0[n] = -(tau_next ** (alpha + 1.0)) / (alpha * (alpha + 1.0) * tau_prev)
        B1[n] = (
            (tau_prev + tau_next) * tau_next**alpha / alpha
            - tau_next ** (alpha + 1.0) / (alpha + 1.0)
        ) / tau_prev
    return B0, B1


def compact_matrices(M, spatial_relation="compact"):
    h = 1.0 / M
    m = M - 1
    A = np.eye(m) * (10.0 / 12.0)
    for i in range(m - 1):
        A[i, i + 1] = 1.0 / 12.0
        A[i + 1, i] = 1.0 / 12.0

    D2 = np.eye(m) * (-2.0 / h**2)
    for i in range(m - 1):
        D2[i, i + 1] = 1.0 / h**2
        D2[i + 1, i] = 1.0 / h**2

    if spatial_relation == "compact":
        solve_mat = A - D2
        rhs_mat = A
    elif spatial_relation == "second_order_v":
        solve_mat = np.eye(m) - D2
        rhs_mat = np.eye(m)
    else:
        raise ValueError(f"unknown spatial_relation={spatial_relation!r}")
    solve_inv_A = np.linalg.solve(solve_mat, rhs_mat)
    return h, A, D2, solve_mat, solve_inv_A


def central_first(w, h):
    return (w[2:] - w[:-2]) / (2.0 * h)


def second_diff(w, h):
    return (w[2:] - 2.0 * w[1:-1] + w[:-2]) / h**2


def phi_compact(v_full, u_full, h):
    u_i = u_full[1:-1]
    v_i = v_full[1:-1]
    psi_uu = (u_i * central_first(u_full, h) + central_first(u_full * u_full, h)) / 3.0
    psi_vu = (v_i * central_first(u_full, h) + central_first(v_full * u_full, h)) / 3.0
    return psi_uu - 0.5 * h**2 * psi_vu


def exact_solution(x, t, alpha):
    return np.sin(np.pi * x) * (t**alpha) / math.gamma(1.0 + alpha)


def forcing(x_inner, t, u_inner, alpha, source_mode="compatible", initial_limit=False):
    base = (1.0 + np.pi**2) * np.sin(np.pi * x_inner)
    if source_mode == "compatible":
        ux_factor = np.pi * np.cos(np.pi * x_inner) * (t**alpha) / math.gamma(1.0 + alpha)
        return base + ux_factor * u_inner + np.pi**2 * u_inner
    if t == 0.0:
        if initial_limit:
            nonlinear = np.pi * np.sin(np.pi * x_inner) * np.cos(np.pi * x_inner) / (
                math.gamma(1.0 + alpha) ** 2
            )
        else:
            nonlinear = 0.0
        return base + nonlinear + np.pi**2 * u_inner
    ux_factor = np.pi * np.cos(np.pi * x_inner) / (math.gamma(1.0 + alpha) * t**alpha)
    return base + ux_factor * u_inner + np.pi**2 * u_inner


def h1_error(u_full, x, t, alpha):
    h = x[1] - x[0]
    e = u_full - exact_solution(x, t, alpha)
    l2 = h * np.sum(e[1:-1] ** 2)
    hsemi = h * np.sum(((e[1:] - e[:-1]) / h) ** 2)
    return math.sqrt(l2 + hsemi)


def solve_from_y(y, solve_inv_A):
    u = solve_inv_A @ y
    v = u - y
    return u, v


def pccd(
    alpha,
    M,
    N,
    T=1.0,
    keep_history=False,
    initial_limit=False,
    source_mode="compatible",
    spatial_relation="compact",
):
    x = np.linspace(0.0, 1.0, M + 1)
    xi = x[1:-1]
    t = graded_mesh(alpha, N, T)
    h, A, _D2, solve_mat, solve_inv_A = compact_matrices(M, spatial_relation=spatial_relation)
    W0, W1 = interp_weights(t, alpha)
    B0, B1 = predictor_extrap_weights(t, alpha)
    gamma_alpha = math.gamma(alpha)

    u_hist = np.zeros((N + 1, M + 1), dtype=float) if keep_history else None
    U = np.zeros((N + 1, M - 1), dtype=float)
    V = np.zeros((N + 1, M - 1), dtype=float)
    F = np.zeros((N + 1, M - 1), dtype=float)

    # Initial value is zero, hence v=0 and F(0)=f(x,0,0).
    F[0] = forcing(xi, 0.0, U[0], alpha, source_mode=source_mode, initial_limit=initial_limit)
    max_err = h1_error(np.zeros(M + 1), x, 0.0, alpha)

    for n in range(N):
        if n == 0:
            y_pred = (t[1] ** alpha / alpha) * F[0] / gamma_alpha
        else:
            hist = W0[n, :n] @ F[:n] + W1[n, :n] @ F[1 : n + 1]
            y_pred = (hist + B0[n] * F[n - 1] + B1[n] * F[n]) / gamma_alpha

        up_i, vp_i = solve_from_y(y_pred, solve_inv_A)
        up = np.zeros(M + 1, dtype=float)
        vp = np.zeros(M + 1, dtype=float)
        up[1:-1] = up_i
        vp[1:-1] = vp_i
        Fp = vp_i - phi_compact(vp, up, h) + forcing(xi, t[n + 1], up_i, alpha, source_mode=source_mode)

        hist = W0[n, :n] @ F[:n] + W1[n, :n] @ F[1 : n + 1]
        y_corr = (hist + W0[n, n] * F[n] + W1[n, n] * Fp) / gamma_alpha
        u_i, v_i = solve_from_y(y_corr, solve_inv_A)

        U[n + 1] = u_i
        V[n + 1] = v_i
        u_full = np.zeros(M + 1, dtype=float)
        v_full = np.zeros(M + 1, dtype=float)
        u_full[1:-1] = u_i
        v_full[1:-1] = v_i
        F[n + 1] = v_i - phi_compact(v_full, u_full, h) + forcing(
            xi, t[n + 1], u_i, alpha, source_mode=source_mode
        )
        if keep_history:
            u_hist[n + 1] = u_full
        max_err = max(max_err, h1_error(u_full, x, t[n + 1], alpha))

    return {
        "x": x,
        "t": t,
        "U": U,
        "u_full": u_hist,
        "max_h1_error": max_err,
    }


def orders(errors):
    out = [None]
    for a, b in zip(errors[:-1], errors[1:]):
        out.append(math.log(a / b, 2.0))
    return out


def make_tables():
    alphas = [0.4, 0.6, 0.8]
    Ns = [6, 12, 24, 48, 96]
    Ms = [4, 8, 16, 32, 64]

    paper_table1 = {
        0.4: [1.295e-1, 3.073e-2, 7.435e-3, 1.823e-3, 4.514e-4],
        0.6: [1.285e-1, 3.051e-2, 7.380e-3, 1.811e-3, 4.483e-4],
        0.8: [1.233e-1, 2.927e-2, 7.080e-3, 1.737e-3, 4.300e-4],
    }
    paper_table2 = {
        0.4: [6.367e-3, 4.340e-4, 2.791e-5, 1.786e-6, 1.157e-7],
        0.6: [5.813e-3, 3.958e-4, 2.542e-5, 1.607e-6, 1.016e-7],
        0.8: [4.907e-3, 3.342e-4, 2.136e-5, 1.343e-6, 8.419e-8],
    }

    lines = ["# Example 4.1 reproduction\n"]
    lines.append("## Table 1 - Temporal accuracy of PCCD (M=N)\n")
    lines.append("| alpha | N | reproduced E | reproduced order | paper E | rel. diff |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    table1_rows = []
    for alpha in alphas:
        errs = []
        for N in Ns:
            start = time.perf_counter()
            err = pccd(alpha, N, N, T=1.0)["max_h1_error"]
            elapsed = time.perf_counter() - start
            errs.append(err)
            table1_rows.append((alpha, N, err, elapsed))
        ords = orders(errs)
        for (alpha2, N, err, elapsed), order, paper in zip(table1_rows[-len(Ns):], ords, paper_table1[alpha]):
            diff = abs(err - paper) / paper
            order_txt = "--" if order is None else f"{order:.3f}"
            lines.append(f"| {alpha2:.1f} | {N} | {err:.3e} | {order_txt} | {paper:.3e} | {diff:.2%} |")

    lines.append("\n## Table 2 - Spatial accuracy of PCCD (N=2000)\n")
    lines.append("| alpha | M | reproduced E | reproduced order | paper E | rel. diff |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    table2_rows = []
    for alpha in alphas:
        errs = []
        alpha_rows = []
        for M in Ms:
            start = time.perf_counter()
            err = pccd(alpha, M, 2000, T=1.0)["max_h1_error"]
            elapsed = time.perf_counter() - start
            errs.append(err)
            alpha_rows.append((alpha, M, err, elapsed))
            table2_rows.append((alpha, M, err, elapsed))
        ords = orders(errs)
        for (alpha2, M, err, elapsed), order, paper in zip(alpha_rows, ords, paper_table2[alpha]):
            diff = abs(err - paper) / paper
            order_txt = "--" if order is None else f"{order:.3f}"
            lines.append(f"| {alpha2:.1f} | {M} | {err:.3e} | {order_txt} | {paper:.3e} | {diff:.2%} |")

    lines.append("\n## Diagnostic - Table 1 with a second-order spatial relation\n")
    lines.append(
        "This is not the PCCD compact scheme. It is included because it reproduces "
        "the magnitude and second-order behavior of the paper's Table 1 much more closely."
    )
    lines.append("\n| alpha | N | diagnostic E | diagnostic order | paper Table 1 E | rel. diff |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    for alpha in alphas:
        errs = []
        alpha_rows = []
        for N in Ns:
            err = pccd(alpha, N, N, T=1.0, spatial_relation="second_order_v")["max_h1_error"]
            errs.append(err)
            alpha_rows.append((alpha, N, err))
        ords = orders(errs)
        for (alpha2, N, err), order, paper in zip(alpha_rows, ords, paper_table1[alpha]):
            diff = abs(err - paper) / paper
            order_txt = "--" if order is None else f"{order:.3f}"
            lines.append(f"| {alpha2:.1f} | {N} | {err:.3e} | {order_txt} | {paper:.3e} | {diff:.2%} |")

    (OUT / "example_4_1_tables.md").write_text("\n".join(lines), encoding="utf-8")
    return table1_rows, table2_rows


def make_figure():
    alpha = 0.5
    M = 128
    N = 800
    sol = pccd(alpha, M, N, T=10.0, keep_history=True)
    x = sol["x"]
    t = sol["t"]
    U = sol["u_full"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True)
    X, Tm = np.meshgrid(x, t)
    im = axes[0].pcolormesh(X, Tm, U, shading="auto", cmap="viridis")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("t")
    axes[0].set_title("Top view")
    fig.colorbar(im, ax=axes[0], label="u(x,t)")

    for target in [2, 4, 6, 8, 10]:
        idx = int(np.argmin(np.abs(t - target)))
        axes[1].plot(x, U[idx], label=f"t={target}")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("u(x,t)")
    axes[1].set_title("Profiles")
    axes[1].legend(frameon=False)
    axes[1].grid(True, alpha=0.25)

    png = OUT / "example_4_1_figure_1.png"
    pdf = OUT / "example_4_1_figure_1.pdf"
    fig.savefig(png, dpi=220)
    fig.savefig(pdf)
    plt.close(fig)
    return sol["max_h1_error"]


def main():
    start = time.perf_counter()
    make_tables()
    fig_err = make_figure()
    elapsed = time.perf_counter() - start
    summary = (
        "Example 4.1 reproduction finished.\n"
        f"Long-time run max H1 error against exact solution: {fig_err:.3e}\n"
        f"Elapsed seconds: {elapsed:.2f}\n"
    )
    (OUT / "example_4_1_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
