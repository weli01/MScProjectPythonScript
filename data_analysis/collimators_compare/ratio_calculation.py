#!/usr/bin/env python3
from pathlib import Path
from math import sqrt, isfinite
from rich.console import Console
from rich.table import Table

# Fixed base directory (contains tc99m/ and lu177/)
BASE = Path("/Users/weli/Documents/pyCharm/MPH5008/data")

# ---------------- core maths ----------------
def compute_total_energy_with_uncertainty(file_path: Path):
    """
    Integrate column 3 (dPhi/dE per GeV) across each energy bin width (GeV→keV).
    Column 4 is the relative uncertainty (fraction or percent). Returns (total, sigma_total).
    """
    total = 0.0
    var_total = 0.0  # accumulate variance

    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) < 3:
                continue

            # Handle both 3-col and 4-col formats gracefully
            try:
                a = float(parts[0])          # GeV
                b = float(parts[1])          # GeV
                y = float(parts[2])          # dPhi/dE per GeV
                r = float(parts[3]) if len(parts) >= 4 else 0.0  # relative err
            except ValueError:
                continue

            # Percent or fraction? If >1, assume percent and convert.
            if r > 1.0:
                r = r / 100.0

            dE_keV = (b - a) * 1e6
            total += dE_keV * y

            sigma_i = abs(y) * abs(r)
            var_total += (dE_keV * sigma_i) ** 2

    return total, sqrt(var_total)

# --------------- discovery for one isotope ---------------
def _pairs_in_folder(folder: Path):
    """
    Yield (f21, f22) for every '*_21_tab.lis' that has a sibling '*_22_tab.lis'
    in the same folder (works for 'holes_21_tab.lis', 'run_21_tab.lis', 'solid98_21_tab.lis', etc.).
    """
    for f21 in sorted(folder.glob("*_21_tab.lis")):
        f22 = f21.with_name(f21.name.replace("_21_", "_22_", 1))
        if f22.exists():
            yield f21, f22

def find_pairs_for_isotope(isotope_root: Path):
    """
    Yield (label, f21, f22) where label is '<collimator>/<parent-folder>',
    i.e. the setting is taken from the direct parent of the .lis files.
    """
    for coll_dir in sorted(p for p in isotope_root.iterdir() if p.is_dir()):
        collimator = coll_dir.name

        # holes/
        holes_dir = coll_dir / "holes"
        if holes_dir.is_dir():
            for f21, f22 in _pairs_in_folder(holes_dir):
                setting = f21.parent.name
                yield f"{collimator}/{setting}", f21, f22

        # solid/<setting>/
        solid_root = coll_dir / "solid"
        if solid_root.is_dir():
            for setting_dir in sorted(p for p in solid_root.iterdir() if p.is_dir()):
                for f21, f22 in _pairs_in_folder(setting_dir):
                    setting = f21.parent.name
                    yield f"{collimator}/{setting}", f21, f22

# --------------- processing & printing ---------------
def process_isotope(isotope: str):
    """
    Return rows: (label, init, sig_init, trans, sig_trans, ratio, sig_ratio)
    """
    root = BASE / isotope
    if not root.is_dir():
        raise FileNotFoundError(f"Isotope folder not found: {root}")

    rows = []
    for label, f21, f22 in find_pairs_for_isotope(root):
        init, sig_i = compute_total_energy_with_uncertainty(f21)        # 21 = initial
        trans, sig_t = compute_total_energy_with_uncertainty(f22)       # 22 = transmitted

        # Ratio and its uncertainty (independent totals)
        if init != 0 and isfinite(init) and isfinite(trans):
            ratio = trans / init
            # guard against zero totals
            rel2 = 0.0
            if trans != 0:
                rel2 += (sig_t / abs(trans)) ** 2
            if init != 0:
                rel2 += (sig_i / abs(init)) ** 2
            sig_r = abs(ratio) * sqrt(rel2) if rel2 > 0 else 0.0
        else:
            ratio, sig_r = 0.0, 0.0

        rows.append((label, init, sig_i, trans, sig_t, ratio, sig_r))
    return rows

def print_energy_table(rows, isotope: str):
    console = Console()
    table = Table(title=f"\nEnergy Transmission Summary — {isotope}")
    for col in [
        "Setting",
        "Initial [keV]",
        "Transmitted [keV]",
        "Transmitted / Initial",
    ]:
        table.add_column(col, justify="center", style="bold cyan")

    for label, ini, si, tra, st, rat, sr in sorted(rows, key=lambda x: x[0]):
        table.add_row(
            label,
            f"{ini:.4f} ± {si:.4f}",
            f"{tra:.4f} ± {st:.4f}",
            f"{rat:.6f} ± {sr:.6f}",
        )

    console.print(table)

# ---------------- main ----------------
if __name__ == "__main__":
    choice = input("Which isotope? (tc99m / lu177): ").strip().lower()
    if choice not in ("tc99m", "lu177"):
        print("Invalid choice — please enter 'tc99m' or 'lu177'.")
    else:
        rows = process_isotope(choice)
        if not rows:
            print(f"No matching 21/22 _tab.lis pairs found under {choice}/.")
        else:
            print_energy_table(rows, choice)
