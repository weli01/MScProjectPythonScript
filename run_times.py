import os
import re
from pathlib import Path
from collections import defaultdict

# ---------------- CONFIGURATION ----------------
BASE_DIR = Path("/Users/weli/Documents/fluka/Projects/MSc").expanduser().resolve()
EXCLUDE_SIMULATIONS = {"tc99m/LEHRS", "tc99m/main_study"}   # Add relative paths to exclude, e.g., {"tc99m/LEHRS"}
# ------------------------------------------------

# Regex patterns for parsing lines
CPU_TIME_RE = re.compile(r"Total\s+CPU\s+time.*:\s*([\d.Ee+-]+)\s*seconds", re.IGNORECASE)
PRIMARIES_RE = re.compile(r"Total\s+number\s+of\s+primaries\s+run:\s*([0-9]+)", re.IGNORECASE)
SUFFIX5_RE = re.compile(r"(\d{5})\.out$", re.IGNORECASE)

def parse_out(path):
    """
    Returns (cpu_seconds, primaries) using the last seen matches in the file.
    Missing values default to 0.
    """
    cpu_seconds = 0.0
    primaries = 0

    for line in path.open("r", errors="ignore"):
        if (m := CPU_TIME_RE.search(line)): cpu_seconds = float(m.group(1))
        if (m := PRIMARIES_RE.search(line)): primaries = int(m.group(1))
    return cpu_seconds, primaries

def summarise(base_dir):
    """
    For each folder containing .out files:
      - Sum all primaries,
      - Sum CPU seconds per cycle stem (4-digit stem from the filename’s last 5 digits).
    Returns list of dicts with: Simulation, Total primaries, Cycle seconds map.
    """
    results = []

    for root, _, files in os.walk(base_dir):
        folder = Path(root)

        outs = [folder / f for f in files if f.lower().endswith(".out")]
        if not outs:
            continue

        sim = str(folder.relative_to(base_dir))
        if sim in EXCLUDE_SIMULATIONS:
            continue

        total_prim = 0
        stem_seconds = defaultdict(float)

        for out in outs:
            cpu, p = parse_out(out)
            total_prim += p
            if (m := SUFFIX5_RE.search(out.name)):
                stem_seconds[m.group(1)[:4] + "*"] += cpu

        results.append({"Simulation": sim, "Primaries": total_prim, "Stems": stem_seconds})

    # Sort by simulation path
    results.sort(key=lambda r: r["Simulation"])
    return results

def format_sci(n):
    """
    Returns float in scientific notation
    """
    return f"{float(n):.2E}".replace("+", "")

def print_report(data):
    """
    Prints data in a tabular format
    """
    for d in data:
        sim = d["Simulation"]
        prim = d["Primaries"]
        stems = d["Stems"]

        print(f"{sim}\n  Total primaries: {format_sci(prim)}")

        hrs = {s: v / 3600 for s, v in sorted(stems.items(), key=lambda x: int(x[0][:4]))}
        for s, h in hrs.items():
            print(f"  - {s:<6} {h:10.2f} h")

        if "main_study" in sim.split("/"):
            chunks = [list(hrs.values())[:5],
                      list(hrs.values())[5:9],
                      list(hrs.values())[9:13]]
            print("  Averages (main_study):")
            for i, c in enumerate(chunks, 1):
                print(f"    - group {i}: {sum(c)/len(c):.2f} h (n={len(c)})" if c else f"    - group {i}: n/a")
        else:
            avg = sum(hrs.values())/len(hrs) if hrs else 0
            print(f"  Average per spawn/core: {avg:.2f} h (n={len(hrs)})")
        print()

def main():
    print_report(summarise(BASE_DIR))

if __name__ == "__main__":
    main()