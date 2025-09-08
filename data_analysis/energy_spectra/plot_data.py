#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LogFormatterMathtext, NullFormatter
from matplotlib import colors as mcolors

plt.rcParams.update({'font.family': 'Trebuchet MS'})

DATA_ROOT  = Path("/Users/weli/Documents/pyCharm/MPH5008/data_analysis/energy_spectra/datasets")
PLOTS_ROOT = DATA_ROOT.parent / "plots" / "results"

# ---------- helpers ----------
def _parse_detector_from_filename(fp: Path) -> str:
    """Extract detector name from filename."""
    name = fp.stem
    return name.split("__", 1)[1] if "__" in name else name

def _load_csv(fp: Path):
    """Load FLUKA spectrum CSV (E [GeV], value, rel_err)."""
    E, y, r = [], [], []
    with fp.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        _ = next(reader, None)  # skip header
        for row in reader:
            if len(row) < 3:
                continue
            try:
                E.append(float(row[0]))
                y.append(float(row[1]) * 1e6)  # convert GeV → keV
                r.append(float(row[2]))
            except ValueError:
                continue
    return np.asarray(E), np.asarray(y), np.asarray(r)

def _collect_datasets(isotope: str, study: str):
    """Collect all detector spectra for isotope/study."""
    in_dir = DATA_ROOT / isotope / study
    out = {}
    for fp in sorted(in_dir.glob("*.csv")):
        if fp.name == "index.csv":
            continue
        det = _parse_detector_from_filename(fp)
        out[det] = (*_load_csv(fp), fp)
    return out

def format_axes(ax, title):
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.set_xlabel(r"$E$ [keV]")
    ax.set_ylabel(r"$\frac{\mathrm{d}\Phi}{\mathrm{d}E}$  (cm$^{-2}$ keV$^{-1}$ particle $^{-1}$)")
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10.0))
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=range(2, 10), numticks=100))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(which="major", linestyle="-", alpha=0.25)
    ax.grid(which="minor", linestyle=(0, (1, 3)), alpha=0.25)
    for spine in ax.spines.values():
        spine.set_alpha(0.6)

# Base colours (for photons)
BASE_COLOURS = {
    "airRflu": "#1f77b4",  # blue (Air photons)
    "ptmWflu": "#d62728",  # red  (Phantom photons)
}

def _lighter_colour(colour, factor=0.5):
    """Lighten a given colour by mixing with white."""
    c = np.array(mcolors.to_rgb(colour))
    white = np.array([1, 1, 1])
    return tuple((1-factor) * white + factor * c)

def _isotope_label(isotope: str) -> str:
    """Return LaTeX-style label for isotope."""
    if isotope.lower() == "tc99m":
        return r"$^{99\mathrm{m}}$Tc"
    elif isotope.lower() == "lu177":
        return r"$^{177}$Lu"
    else:
        return isotope

# ---------- main plotting ----------
def plot_main_study(isotope: str):
    study = "main_study"
    ds = _collect_datasets(isotope, study)
    PLOTS_ROOT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    label = _isotope_label(isotope)
    format_axes(ax, f"{label} — Photon & electron fluence-energy spectra")

    # Families + markers
    TARGETS = {
        "ptmWflu": "Phantom",
        "airRflu": "Air",
    }
    MARKERS = {
        ("ptmWflu", "P"): "+",   # Phantom photons → circle
        ("ptmWflu", "E"): "x",   # Phantom electrons → X
        ("airRflu", "P"): "<",   # Air photons → square
        ("airRflu", "E"): ">",   # Air electrons → triangle
    }

    plotted = []

    for det_name, (E, y, r, fp) in ds.items():
        if not fp.stem.startswith(("run_27_", "run_28_", "run_29_")):
            continue
        if not det_name.endswith(("P", "E")):
            continue

        family = det_name[:-1]  # "ptmWflu" or "airRflu"
        kind   = det_name[-1]   # "P" or "E"

        if family not in TARGETS:
            continue

        friendly_name = TARGETS[family]
        base_colour   = BASE_COLOURS[family]
        marker        = MARKERS[(family, kind)]
        part_label    = "photons" if kind == "P" else "electrons"

        # Use lighter shade for electrons
        plot_colour = base_colour if kind == "P" else _lighter_colour(base_colour, factor=0.5)

        mask = y > 0
        yerr_abs = np.abs(y) * np.abs(r)

        handle = ax.errorbar(
            E[mask], y[mask], yerr=yerr_abs[mask],
            fmt=marker, ms=5, lw=1.0, ls="-",
            mfc="none", mec=plot_colour, mew=0.5, # hollow markers
            color=plot_colour, ecolor=plot_colour,
            elinewidth=0.8, capsize=2.0,
            label=f"{friendly_name} — {part_label}",
        )
        plotted.append((friendly_name, part_label, handle))

    # enforce legend order
    order = [
        ("Phantom", "photons"),
        ("Phantom", "electrons"),
        ("Air", "photons"),
        ("Air", "electrons"),
    ]
    handles, labels = [], []
    for fam, part in order:
        for (f, p, h) in plotted:
            if f == fam and p == part:
                handles.append(h)
                labels.append(f"{fam} — {part}")

    ax.legend(
        handles, labels,
        frameon=True, fancybox=True,
        loc="upper right", ncol=1
    )

    out_path = PLOTS_ROOT / f"{isotope}_main_study_spectra_phantom_air.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.show()
    print(f"Saved: {out_path}")

# ---------- run ----------
if __name__ == "__main__":
    plot_main_study("tc99m")
    plot_main_study("lu177")
