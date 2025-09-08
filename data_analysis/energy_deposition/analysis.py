# analyse_runs.py
import re
from pathlib import Path

import numpy as np
import pandas as pd

# -----------------------------
# Paths (fixed run folder)
# -----------------------------
SCRIPT_DIR   = Path(__file__).resolve().parent
RUN_FOLDER   = Path()  # Leave empty; will be set from plot.py
HIERARCHY_CSV = SCRIPT_DIR / "region_hierarchy.csv"
OUTPUT_CSV    = SCRIPT_DIR / "energy_by_region.csv"

# Placeholder for missing hierarchy labels (use "" if you prefer blanks)
MISSING_LABEL = "Unspecified"

# -----------------------------
# File listing / parsing helpers
# -----------------------------
RUN_FILE_RX = re.compile(r"^run_\d{5}\.out$")

def list_run_files(folder):
    """Return sorted run_XXXXX.out files from folder."""
    return sorted(p for p in folder.glob("run_*.out") if RUN_FILE_RX.match(p.name))

def find_em_energy_start(lines):
    """Return index of first data line after EM-ENRGY header, else None."""
    for i, line in enumerate(lines):
        if ("EM-ENRGY" in line) and ("Density" in line) and ("Region" in line):
            return i + 4
    return None

def parse_em_energy_rows(lines, start_idx, tokens_per_row=7):
    """Parse EM-ENRGY rows into (region_names, energy_keV) until token count changes."""
    names, vals = [], []
    for line in lines[start_idx:]:
        parts = line.strip().split()
        if len(parts) != tokens_per_row:
            break
        names.append(parts[1])
        vals.append(float(parts[-1].replace("D", "E")) * 1e6)  # GeV -> keV
    return names, vals

def extract_energy_from_file(file_path):
    """Extract per-region EM-ENRGY (keV) from one .out file."""
    lines = file_path.read_text(errors="ignore").splitlines()
    start = find_em_energy_start(lines)
    return parse_em_energy_rows(lines, start)

def load_all_files(folder_path):
    """Collect energy vectors from all runs -> (region_names, matrix[n_runs, n_regions])."""
    files = list_run_files(folder_path)
    region_names_ref, all_energy = [], []
    for f in files:
        names, values = extract_energy_from_file(f)
        if not values:
            continue
        if not region_names_ref:
            region_names_ref = names
        all_energy.append(values)
    return region_names_ref, np.asarray(all_energy, dtype=float)

# -----------------------------
# Stats / hierarchy / output
# -----------------------------
def compute_mean_and_error(data):
    """Return (mean, percentage_error) across runs."""
    mean = np.mean(data, axis=0)
    if data.shape[0] > 1:
        sem = np.std(data, axis=0, ddof=1) / np.sqrt(data.shape[0])
    else:
        sem = np.zeros_like(mean)
    with np.errstate(divide="ignore", invalid="ignore"):
        per_err = np.where(mean > 0, (sem / mean) * 100.0, 0.0)
    return mean, per_err

def load_hierarchy():
    """Load hierarchy mapping; preserve CSV order for sorting."""
    df = pd.read_csv(HIERARCHY_CSV, dtype=str).fillna("")
    df["__order__"] = np.arange(len(df))
    return df

def build_results_dataframe(region_names, mean_keV, perc_err, hdf):
    """Merge results with hierarchy, compute % of total, fill missing labels."""
    df = pd.DataFrame({
        "Region": region_names,
        "Mean Energy [keV]": mean_keV,
        "Percentage Error": perc_err,
    })
    total = df["Mean Energy [keV]"].sum()
    df["Percentage of Total"] = (df["Mean Energy [keV]"] / total * 100.0) if total > 0 else 0.0

    merged = pd.merge(hdf, df, on="Region", how="right")

    # Ensure grouping columns are never NaN so downstream plots don’t drop groups
    for col in ["Level1", "Level2", "Level3"]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(MISSING_LABEL)

    merged["__order__"] = merged["__order__"].fillna(1e9)
    merged = merged.sort_values(["__order__", "Region"]).reset_index(drop=True)
    return merged.drop(columns="__order__")

def save_region_table(df):
    """Write the tidy per-region table."""
    cols = [
        "Region",
        "Mean Energy [keV]",
        "Percentage Error",
        "Percentage of Total",
        "Level1", "Level2", "Level3",
    ]
    df.to_csv(OUTPUT_CSV, index=False, columns=cols)
    return OUTPUT_CSV

# -----------------------------
# Main function
# -----------------------------
def run():
    region_names, energy_data = load_all_files(RUN_FOLDER)
    mean_energy, error_percent = compute_mean_and_error(energy_data)
    hdf = load_hierarchy()
    results = build_results_dataframe(region_names, mean_energy, error_percent, hdf)

    print("\nEnergy distribution by region (merged with hierarchy):")
    print(results[[
        "Region", "Mean Energy [keV]", "Percentage Error", "Percentage of Total",
        "Level1", "Level2", "Level3"
    ]])

    total_energy = results["Mean Energy [keV]"].sum()
    print(f"\nTotal energy across all regions: {total_energy:.6e} keV")

    out_csv = save_region_table(results)
    print(f"\nResults saved to: {out_csv}")
    return out_csv