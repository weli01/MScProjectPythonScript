# dose_limits.py (minimal, main_study only)
from pathlib import Path
import numpy as np
from rich.console import Console
from rich.table import Table

from activity import cumulated_activity_auto          # zero-arg; uses caller globals
from methods.simulation import process_simulation     # (folder: Path, A_cum: float) -> (dose, unc)

# --- config -------------------------------------------------------------------
BASE_PATHS = {
    "tc-99m": Path("/Users/weli/Documents/pyCharm/MPH5008/tc99m"),
    "lu-177": Path("/Users/weli/Documents/pyCharm/MPH5008/lu177"),
}

WORKLOAD_PER_DAY = 14.0
DAYS_PER_YEAR    = 365.0
ANNUAL_FACTOR    = WORKLOAD_PER_DAY * DAYS_PER_YEAR  # 14 * 365

# Occupancy factors and corresponding TLD labels
# For TLDs inside room, limit does not really apply, so set to 1.0
OCCUPANCY_MAIN = [1.0, 1.0, 1.0, 0.2, 1.0, 0.05, 1.0, 1.0, 1.0, 1.0, 1.0]
TLD_LABELS_MAIN = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D', 'E1', 'E2', 'E3', 'E4']

def main():
    # --- choose source (Tc-99m or Lu-177 only) --------------------------------
    src = input("Enter source [tc-99m/lu-177]: ").strip().lower()
    if src not in ("tc-99m", "lu-177"):
        raise ValueError("Source must be 'tc-99m' or 'lu-177'.")

    # expose 'source' so cumulated_activity_auto() picks the correct isotope & same-day window
    globals()["source"] = src

    BASE_PATH = BASE_PATHS[src]
    MAIN_STUDY_FOLDER = BASE_PATH / "main_study"

    if not MAIN_STUDY_FOLDER.is_dir():
        raise FileNotFoundError(f"Missing folder: {MAIN_STUDY_FOLDER}")

    # --- activity --------------------------------------------------------------
    A_cum = cumulated_activity_auto()  # uses same-day duration in dose-limits mode

    # --- simulation doses (µSv) & uncertainties (µSv) --------------------------
    sim_dose, sim_unc = process_simulation(MAIN_STUDY_FOLDER, A_cum)
    sim_dose = np.asarray(sim_dose, dtype=float)
    sim_unc  = np.asarray(sim_unc,  dtype=float)

    n = min(sim_dose.size, sim_unc.size, len(TLD_LABELS_MAIN))
    if n == 0:
        raise RuntimeError("No TLD entries returned by simulation.")

    sim_dose, sim_unc = sim_dose[:n], sim_unc[:n]
    labels = TLD_LABELS_MAIN[:n]

    # --- occupancy (trim/pad to n) --------------------------------------------
    occ = np.asarray(OCCUPANCY_MAIN, dtype=float)
    if occ.size < n:
        occ = np.pad(occ, (0, n - occ.size), constant_values=1.0)
    else:
        occ = occ[:n]
    occ = np.clip(occ, 0.0, 1.0)

    # --- annual dose = sim × occ × 14 × 365 -----------------------------------
    scale = occ * ANNUAL_FACTOR / 1000 # µSv -> mSv
    annual   = sim_dose * scale
    annual_u = sim_unc  * scale  # treat occ/workload/365 as exact

    # --- print table -----------------------------------------------------------
    table = Table(title=f"\nAnnual dose estimate (main_study, source={src})")
    for h in ["TLD", "H*(10) / patient\n[µSv]", "Occupancy", "Annual H*(10)\n[mSv/y]"]:
        table.add_column(h, justify="center")
    for i, lab in enumerate(labels):
        if sim_dose[i] < 0.0001:
            sim_str = "<0.0001"
        else:
            sim_str = f"{sim_dose[i]:.4f} ± {sim_unc[i]:.4f}"

        if annual[i] < 0.0001:
            ann_str = "<0.0001"
        else:
            ann_str = f"{annual[i]:.4f} ± {annual_u[i]:.4f}"

        table.add_row(
            lab,
            sim_str,
            f"{occ[i]:.2f}",
            ann_str,
        )
    Console(width=120, markup=False).print(table)

if __name__ == "__main__":
    main()
