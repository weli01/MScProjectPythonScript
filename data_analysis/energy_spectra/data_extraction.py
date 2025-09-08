#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse
import csv
import re
from typing import Dict, List, Tuple, Optional

# --- Paths ---
IN_ROOT  = Path("/Users/weli/Documents/pyCharm/MPH5008/")
OUT_ROOT = IN_ROOT / "data_analysis" / "energy_spectra" / "datasets"

# --- Patterns & file lists ---
DET_HEADER_RE = re.compile(r'^\s*#\s*Detector\s*n:\s*\d+\s+(\S+)', re.IGNORECASE)
FOUR_FLOATS_RE = re.compile(
    r'^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+'
    r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+'
    r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+'
    r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$'
)
MAIN_FILES = ["run/run_27_tab.lis", "run/run_28_tab.lis", "run/run_29_tab.lis"]
PRE_FILES  = ["run/run_25_tab.lis"]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract detector datasets from .lis files.")
    p.add_argument("--root", type=Path, default=IN_ROOT,
                   help=f"Input root (default: {IN_ROOT})")
    p.add_argument("--isotope", choices=["tc99m", "lu177"],
                   help="Isotope (if omitted, you’ll be prompted).")
    p.add_argument("--study", choices=["pre_study", "main_study"],
                   help="Study (required for tc99m; ignored for lu177).")
    return p.parse_args()

def prompt_isotope_and_study(cli_iso: Optional[str], cli_study: Optional[str]) -> Tuple[str, str]:
    if cli_iso in ("tc99m", "lu177"):
        isotope = cli_iso
    else:
        while True:
            choice = input("Choose isotope [tc99m/lu177]: ").strip().lower()
            if choice in ("tc99m", "lu177"):
                isotope = choice
                break
            print("Please type 'tc99m' or 'lu177'.")

    if isotope == "tc99m":
        if cli_study in ("pre_study", "main_study"):
            study = cli_study
        else:
            while True:
                s = input("Choose study for tc99m [pre_study/main_study]: ").strip().lower()
                if s in ("pre_study", "main_study"):
                    study = s
                    break
                print("Please type 'pre_study' or 'main_study'.")
    else:
        study = "main_study"
        if cli_study and cli_study != "main_study":
            print("Note: For lu177, study is fixed to 'main_study'. Ignoring '--study'.")

    return isotope, study

def expected_files_for(study: str) -> List[str]:
    return MAIN_FILES if study == "main_study" else PRE_FILES

def safe_name(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', s) if s else "unnamed"

def parse_lis_multi(fp: Path) -> Dict[str, List[Tuple[float,float,float]]]:
    """
    Parse a .lis file into multiple datasets keyed by detector name.
    Returns: {detector_name: [(E_mid, value, rel_err), ...], ...}
    """
    datasets: Dict[str, List[Tuple[float,float,float]]] = {}
    current: Optional[str] = None

    with fp.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m_header = DET_HEADER_RE.match(line)
            if m_header:
                current = m_header.group(1)
                datasets.setdefault(current, [])
                continue

            if current is None:
                continue

            m_vals = FOUR_FLOATS_RE.match(line)
            if m_vals:
                a, b, c, d = (float(m_vals.group(i)) for i in range(1, 5))
                E_mid = 0.5 * (a + b) * 1e6  # GeV -> keV
                c = c / 1e6  # per GeV -> per keV
                rel_err_fraction = d / 100.0  # d is percentage from file
                datasets[current].append((E_mid, c, rel_err_fraction))

    return datasets

def write_dataset_csv(out_path: Path, rows: List[Tuple[float,float,float]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # Only the mid-energy as first column, named E, as requested.
        w.writerow(["E", "value", "rel_err"])
        w.writerows(rows)

def main():
    args = parse_args()
    isotope, study = prompt_isotope_and_study(args.isotope, args.study)

    in_dir = args.root / isotope / study
    out_dir = OUT_ROOT / isotope / study

    files = expected_files_for(study)
    present: List[Path] = []
    missing: List[Path] = []

    for name in files:
        p = in_dir / name
        (present if p.exists() else missing).append(p)

    if not present:
        print(f"No expected files found in {in_dir}")
        for m in missing:
            print(f"Missing: {m}")
        return

    print(f"Reading from: {in_dir}")
    print(f"Writing to:   {out_dir}")

    index_rows: List[List[str]] = []

    for fp in present:
        datasets = parse_lis_multi(fp)
        if not datasets:
            print(f"Warning: no datasets detected in {fp.name}")
            continue

        run_stem = fp.stem  # e.g. 'run_27_tab'
        for det_name, rows in datasets.items():
            if not rows:
                continue
            out_fp = out_dir / f"{run_stem}__{safe_name(det_name)}.csv"
            write_dataset_csv(out_fp, rows)
            print(f"Saved {len(rows):5d} rows -> {out_fp.name}")
            index_rows.append([fp.name, det_name, str(out_fp)])

    if index_rows:
        index_fp = out_dir / "index.csv"
        with index_fp.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["source_file", "detector", "csv_path"])
            w.writerows(index_rows)
        print(f"\nIndex written: {index_fp}")
    else:
        print("No datasets were saved.")

    if missing:
        print("\nThe following expected files were not found:")
        for m in missing:
            print(f"  - {m}")



if __name__ == "__main__":
    main()
