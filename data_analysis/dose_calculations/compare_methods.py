from pathlib import Path
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
from rich.console import Console
from rich.table import Table

from activity import cumulated_activity_auto

from methods.analytical import process_analytical          # expected to return (ana_dose, ana_unc) as arrays
from methods.experimental import process_experimental      # expected to return (exp_dose, exp_unc) as arrays
from methods.simulation import process_simulation          # expected to return (sim_dose, sim_unc) as arrays

plt.rcParams.update({'font.family': 'Trebuchet MS'})

RESULTS_BASE = Path("/Users/weli/Documents/pyCharm/MPH5008/data_analysis/dose_calculations/results")
RESULTS_BASE.mkdir(parents=True, exist_ok=True)


def compute_ratios(num_vals, num_unc, den_vals, den_unc):
    """
    Ratio R = num/den and uncertainty via error propagation:
    sigma_R = R * sqrt( (sigma_num/num)^2 + (sigma_den/den)^2 )
    """
    num_vals = np.asarray(num_vals, dtype=float)
    num_unc  = np.asarray(num_unc,  dtype=float)
    den_vals = np.asarray(den_vals, dtype=float)
    den_unc  = np.asarray(den_unc,  dtype=float)

    with np.errstate(divide='ignore', invalid='ignore'):
        R = num_vals / den_vals
        rel_num = np.where(num_vals != 0, num_unc / num_vals, np.nan)
        rel_den = np.where(den_vals != 0, den_unc / den_vals, np.nan)
        sigma_R = np.abs(R) * np.sqrt(rel_num**2 + rel_den**2)

    return R, sigma_R


def paired_t_test(x, y, label_left, label_right, out_dir: Path=RESULTS_BASE):
    """
    Runs a paired two-sided t-test on two equal-length 1D arrays.
    Saves a text file with results in RESULTS_DIR and returns p-value + filename.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    t_stat, p_val = stats.ttest_rel(x, y, nan_policy='omit')

    n     = len(x)
    mean_x = np.nanmean(x)
    mean_y = np.nanmean(y)
    var_x  = np.nanvar(x, ddof=1)
    var_y  = np.nanvar(y, ddof=1)
    corr   = np.corrcoef(x, y)[0, 1]

    report = f"""t-Test: Paired Two Sample for Means — {label_left} vs {label_right}

Observations (n)       : {n}
Mean({label_left})     : {mean_x:.6g}
Mean({label_right})    : {mean_y:.6g}
Variance({label_left}) : {var_x:.6g}
Variance({label_right}): {var_y:.6g}
Pearson correlation    : {corr:.6g}

t statistic            : {t_stat:.6g}
Two-sided p-value      : {p_val:.6g}
"""

    out_dir.mkdir(parents=True, exist_ok=True)
    fname = out_dir / f"paired_ttest_{label_left}_vs_{label_right}.txt"
    with open(fname, "w") as f:
        f.write(report)

    return p_val, str(fname)


def weighted_mean_and_unc(values, uncertainties):
    """
    Weighted mean with weights w = 1/sigma^2 and SDOM = sqrt(1/sum(w)).
    Ignores entries with non-positive or NaN uncertainties.
    """
    values = np.asarray(values, dtype=float)
    uncertainties = np.asarray(uncertainties, dtype=float)

    mask = (
            np.isfinite(values) &
            np.isfinite(uncertainties) &
            (uncertainties > 0) &
            (np.abs(values) >= 0.01)  # discard near-zero values
    )
    if not np.any(mask):
        return np.nan, np.nan

    v = values[mask]
    s = uncertainties[mask]

    w = 1.0 / (s ** 2)
    wm = np.sum(v * w) / np.sum(w)
    sdom = np.sqrt(1.0 / np.sum(w))
    return wm, sdom


def print_rich_table(tld_labels, ana, ana_u, exp, exp_u, sim, sim_u, r_ae, r_ae_u, r_se, r_se_u):
    """
    If 'ana' is None, print a two-column (Exp, Sim) table without analytical columns/ratios.
    """
    has_analytical = ana is not None

    title = "\nDose Comparison (Experimental vs Simulation)" if not has_analytical \
            else "\nDose Comparison (Analytical vs Experimental vs Simulation)"
    table = Table(title=title)

    if has_analytical:
        headers = ["TLD", "Analytical [µSv]", "Experimental [µSv]", "Simulation [µSv]", "Ana/Exp", "Sim/Exp"]
    else:
        headers = ["TLD", "Experimental [µSv]", "Simulation [µSv]", "Sim/Exp"]

    for h in headers:
        table.add_column(h, justify="center")

    for i, label in enumerate(tld_labels):
        if has_analytical:
            table.add_row(
                str(label),
                f"{ana[i]:.2f} ± {ana_u[i]:.2f}",
                f"{exp[i]:.2f} ± {exp_u[i]:.2f}",
                f"{sim[i]:.2f} ± {sim_u[i]:.2f}",
                f"{(r_ae[i] if np.isfinite(r_ae[i]) else np.nan):.2f} ± {(r_ae_u[i] if np.isfinite(r_ae_u[i]) else np.nan):.2f}",
                f"{(r_se[i] if np.isfinite(r_se[i]) else np.nan):.2f} ± {(r_se_u[i] if np.isfinite(r_se_u[i]) else np.nan):.2f}",
            )
        else:
            table.add_row(
                str(label),
                f"{exp[i]:.2f} ± {exp_u[i]:.2f}",
                f"{sim[i]:.2f} ± {sim_u[i]:.2f}",
                f"{(r_se[i] if np.isfinite(r_se[i]) else np.nan):.2f} ± {(r_se_u[i] if np.isfinite(r_se_u[i]) else np.nan):.2f}",
            )

    Console(width=120).print(table)


def plot_grouped_bars(tld_labels, ana, ana_u, exp, exp_u, sim, sim_u, out_dir: Path = RESULTS_BASE, taller: bool = False):
    """
    If 'ana' is None, draw two bars (Exp, Sim). Otherwise draw three (Ana, Exp, Sim).
    If taller=True, increase the vertical size of the plot.
    """
    has_analytical = ana is not None

    n = len(tld_labels)
    idx = np.arange(n)
    plt.rcParams.update({
        'font.size': 14,  # base font size
        'axes.titlesize': 15.5,  # title
        'axes.labelsize': 12,  # x/y labels
        'xtick.labelsize': 12,  # tick labels
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
    })

    width = 0.26
    height = 8 if taller else 5   # <-- taller figure if requested
    fig, ax = plt.subplots(figsize=(max(8, n * 0.8), height))

    if has_analytical:
        # 3 groups centred at -w, 0, +w
        positions = (-width, 0.0, +width)
        series = [
            ("Analytical", ana, ana_u, '#eba93b', positions[0]),
            ("Experimental", exp, exp_u, '#52b1c0', positions[1]),
            ("Simulation",  sim, sim_u, '#b828a7', positions[2]),
        ]
        title = 'Comparison of analytical vs experimental vs simulation methods'
    else:
        # 2 groups centred at -w/2, +w/2 (keeps the pair centred)
        positions = (-width/2, +width/2)
        series = [
            ("Experimental", exp, exp_u, '#52b1c0', positions[0]),
            ("Simulation",  sim, sim_u, '#b828a7', positions[1]),
        ]
        title = 'Comparison of experimental vs simulation methods'

    for label, vals, errs, colour, xshift in series:
        ax.bar(idx + xshift, vals, width, color=colour, edgecolor='white', linewidth=1.2,
               yerr=errs, label=label, error_kw=dict(lw=.8, capsize=5, capthick=.8))

    ax.set_xticks(idx)
    ax.set_xticklabels([str(t) for t in tld_labels])
    ax.set_xlabel('TLDs')
    ax.set_ylabel(r'$H^*(10)$ [µSv]')
    ax.set_title(title, fontweight='bold')
    ax.legend()
    ax.set_ylim(bottom=0)
    ax.set_axisbelow(True)
    if has_analytical:
        ax.yaxis.set_major_locator(tck.MultipleLocator(100))
        ax.yaxis.set_minor_locator(tck.AutoMinorLocator())
    else:
        ax.yaxis.set_minor_locator(tck.AutoMinorLocator())
    ax.grid(axis='y', which='major', color='#666666', linestyle='-', alpha=0.2)
    ax.grid(axis='y', which='minor', color='#666666', linestyle='-', alpha=0.1)

    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "compare_plot.pdf"
    plt.savefig(out_file)
    print(f"Saved plot: {out_file}")


def main():
    BASE_PATH = Path("/Users/weli/Documents/pyCharm/MPH5008/tc99m")

    while True:
        study_folder = input("Enter study name: ").strip()
        folder = BASE_PATH / study_folder

        if folder.is_dir():
            break
        else:
            print(f"Invalid folder: {folder}")

    run_dir = RESULTS_BASE / f"compare_doses_{study_folder}"
    run_dir.mkdir(parents=True, exist_ok=True)

    has_analytical = (study_folder == "main_study")

    # Calculate cumulated activity first
    A_cum = cumulated_activity_auto()

    # --- Get data from each pipeline ---
    # Analytical: returns doses and uncertainties (arrays)
    if has_analytical:
        ana_dose, ana_unc = process_analytical(A_cum)
        ana_dose = np.asarray(ana_dose, dtype=float)
        ana_unc = np.asarray(ana_unc, dtype=float)
    else:
        ana_dose = ana_unc = None

    # Experimental: returns doses and uncertainties (arrays)
    exp_dose, exp_unc = process_experimental(folder)
    exp_dose = np.asarray(exp_dose, dtype=float)
    exp_unc  = np.asarray(exp_unc,  dtype=float)

    # Simulation: returns doses and uncertainties (arrays)
    sim_dose, sim_unc = process_simulation(folder, A_cum)
    sim_dose = np.asarray(sim_dose, dtype=float)
    sim_unc  = np.asarray(sim_unc,  dtype=float)

    # --- Align lengths ---
    if has_analytical:
        n = min(len(ana_dose), len(exp_dose), len(sim_dose))
        ana_dose, ana_unc = ana_dose[:n], ana_unc[:n]
    else:
        n = min(len(exp_dose), len(sim_dose))
    exp_dose, exp_unc = exp_dose[:n], exp_unc[:n]
    sim_dose, sim_unc = sim_dose[:n], sim_unc[:n]

    # TLD labels
    if study_folder == "main_study":
        tld_labels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D', 'E1', 'E2', 'E3', 'E4'][:n]
    elif study_folder == "pre_study":
        tld_labels = [str(i + 1) for i in range(n)]

    # --- Ratios (per TLD) ---
    if has_analytical:
        r_ana_exp, r_ana_exp_unc = compute_ratios(ana_dose, ana_unc, exp_dose, exp_unc)
    else:
        r_ana_exp = r_ana_exp_unc = None
    r_sim_exp,  r_sim_exp_unc  = compute_ratios(sim_dose, sim_unc, exp_dose, exp_unc)

    # --- Weighted averages ---
    if has_analytical:
        wm_ae, wm_ae_unc = weighted_mean_and_unc(r_ana_exp, r_ana_exp_unc)
    else:
        wm_ae = wm_ae_unc = (np.nan, np.nan)
    wm_se, wm_se_unc = weighted_mean_and_unc(r_sim_exp,  r_sim_exp_unc)

    # --- Table ---
    print_rich_table(
        tld_labels,
        ana_dose, ana_unc,
        exp_dose, exp_unc,
        sim_dose, sim_unc,
        r_ana_exp, r_ana_exp_unc,
        r_sim_exp,  r_sim_exp_unc
    )

    print(f"\nWeighted mean (Sim/Experimental): {wm_se:.2f} ± {wm_se_unc:.2f}")
    if has_analytical:
        print(f"Weighted mean (Ana/Experimental): {wm_ae:.2f} ± {wm_ae_unc:.2f}")

    p_se, file_se = paired_t_test(sim_dose, exp_dose, "Simulation", "Experimental", out_dir=run_dir)
    print(f"\nPaired t-test (Sim vs Exp): p = {p_se:.4g}")

    if has_analytical:
        p_ae, file_ae = paired_t_test(ana_dose, exp_dose, "Analytical", "Experimental", out_dir=run_dir)
        print(f"Paired t-test (Ana vs Exp): p = {p_ae:.4g}")
        print(f"\nSaved reports:\n - {file_se}\n - {file_ae}")
    else:
        print(f"\nSaved reports:\n - {file_se}")

    # --- Plot ---
    plot_grouped_bars(
        tld_labels,
        ana_dose, ana_unc,
        exp_dose, exp_unc,
        sim_dose, sim_unc,
        out_dir=run_dir,
        taller=has_analytical  # taller if main_study
    )

if __name__ == "__main__":
    main()