import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
import analysis
import matplotlib.ticker as mticker

plt.rcParams.update({'font.family': 'Trebuchet MS'})

SCRIPT_DIR = Path(__file__).resolve().parent

# Ask user for isotope
iso = input("Select isotope [tc99m/lu177]: ").strip().lower()
while iso not in {"tc99m", "lu177"}:
    print("Invalid input. Please type 'tc99m' or 'lu177'.")
    iso = input("Select isotope [tc99m/lu177]: ").strip().lower()


# Update paths for analysis and plots
analysis.RUN_FOLDER = Path(f"/Users/weli/Documents/pyCharm/MPH5008/data/{iso}/main_study/run")
results_dir = SCRIPT_DIR / "results" / iso
results_dir.mkdir(parents=True, exist_ok=True)
analysis.OUTPUT_CSV = results_dir / "energy_by_region.csv"

analysis.run() # <-- THIS LINE ENSURES CSV IS GENERATED

# ---------- helpers ----------
def format_percentage(p):
    """Return percentage string with special formatting for 0% and <0.01%."""
    return "0%" if p == 0 else ("<0.01%" if p < 0.01 else f"{p:.2f}%")

def tint_series(base_hex, n, start=0.8, end=1.0):
    """Return n colour tints from a base colour, fading towards white."""
    base = np.array(mcolors.to_rgb(base_hex))
    white = np.array([1.0, 1.0, 1.0])
    ts = np.linspace(start, end, max(n, 1)+1)
    return [mcolors.to_hex((1 - t) * white + t * base) for t in ts]

def summarise(df, by):
    """Group by 'by' column(s) and return summed energy and percentage totals."""
    return df.groupby(by, as_index=False, dropna=False).agg(
        Total_Energy_keV=('Mean_Energy_[keV]', 'sum'),
        Percentage_of_Total=('Percentage_of_Total', 'sum')
    )

def barh_simple(df, y, title, colour_map_or_seq=None, figsize=(6, 3), save_path=None):
    """Plot a simple horizontal bar chart with percentage labels."""
    df = df.sort_values('Percentage_of_Total', ascending=True)
    if isinstance(colour_map_or_seq, dict):
        colours = df[y].map(colour_map_or_seq).tolist()
    elif isinstance(colour_map_or_seq, (list, tuple)):
        colours = list(colour_map_or_seq)
    else:
        colours = None

    fig, ax = plt.subplots(figsize=figsize)
    ax.barh(df[y], df['Total_Energy_keV'], color=colours, edgecolor='none')

    for i, (e, p) in enumerate(zip(df['Total_Energy_keV'], df['Percentage_of_Total'])):
        ax.text(e * 1.01 if e > 0.1 else 1, i, format_percentage(p), va='center', fontsize=9)

    ax.set_xlabel('Total Energy [keV]')
    ax.set_title(title, weight='bold')
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax.grid(axis='x', which='major', linestyle='--', linewidth=0.8, alpha=0.4)
    ax.grid(axis='x', which='minor', linestyle=':', linewidth=0.5, alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, format="pdf", bbox_inches="tight")
    plt.show()
    plt.close(fig)

def grouped_bar_plot(df, query, base_colour, title, save_path=None,
                     unit_col='Region', group_by=None, levels=None,
                     intra_bar_step=0.9, gap_lvl1=0.8, gap_lvl2=0.4):
    """Plot a grouped horizontal bar chart (single- or multi-level grouping)."""
    if levels is None:
        levels = [group_by]
    sub = df.query(query).copy()

    keys = [unit_col] + levels
    agg = (sub.groupby(keys, as_index=False)
              .agg(Total_Energy_keV=('Mean_Energy_[keV]', 'sum'),
                   Percentage_of_Total=('Percentage_of_Total', 'sum'))
              .sort_values(levels + ['Total_Energy_keV'])
              .reset_index(drop=True))

    y_pos, labels, spans_lvl1, spans_lvl2 = [], [], [], []
    y = 0.0
    for l1, g1 in agg.groupby(levels[0], sort=True):
        start1 = y
        if len(levels) >= 2:
            for l2, g2 in g1.groupby(levels[1], sort=False):
                start2 = y
                for _, r in g2.iterrows():
                    y_pos.append(y); labels.append(r[unit_col]); y += intra_bar_step
                spans_lvl2.append((l2, start2, y - intra_bar_step))
                y += gap_lvl2
            y -= gap_lvl2
        else:
            for _, r in g1.iterrows():
                y_pos.append(y); labels.append(r[unit_col]); y += intra_bar_step
        spans_lvl1.append((l1, start1, y - intra_bar_step))
        y += gap_lvl1

    shades = tint_series(base_colour, len(spans_lvl1), start=0.4, end=1.0)
    colour_map_lvl1 = {name: shade for (name, *_), shade in zip(spans_lvl1, shades)}
    colours = agg[levels[0]].map(colour_map_lvl1).tolist()

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh(y_pos, agg['Total_Energy_keV'].to_numpy(), color=colours, edgecolor='none')

    for yp, e, p in zip(y_pos, agg['Total_Energy_keV'], agg['Percentage_of_Total']):
        ax.text(e * 1.01 if e > 0.1 else (0.2 if len(levels) == 1 else 0.07),
                yp, format_percentage(p), va='center', fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    xmin, xmax = ax.get_xlim()

    for i, (name, y0, y1) in enumerate(spans_lvl1):
        if i > 0:
            ax.plot([-xmax / (5 if len(levels) == 1 else 4.3),
                     xmax if len(levels) == 1 else 0],
                    [y0 - 1.25 * (gap_lvl1 if len(levels) == 1 else 0.7)] * 2,
                    color='0.85', lw=0.5, clip_on=False)
        ax.text(-xmax / (6 if len(levels) == 1 else 5), (y0 + y1) / 2, str(name),
                ha='right', va='center', fontsize=(11 if len(levels) == 1 else 10),
                color='0.35', weight='bold', rotation=90)

    if len(levels) >= 2:
        prev_end = None
        for (name, y0, y1) in spans_lvl2:
            if prev_end is not None and y0 > prev_end:
                ax.plot([-xmax / 6, xmax],
                        [y0 - 1.25 * (gap_lvl1 if len(levels) == 1 else 0.7)] * 2,
                        color='0.85', lw=0.5, clip_on=False)
            ax.text(-xmax / 7, (y0 + y1) / 2, '' if name == 'na' else str(name),
                    ha='right', va='center', fontsize=9, color='0.35', rotation=90)
            prev_end = y1 + gap_lvl2

    ax.set_xlim(0, xmax)
    ax.set_xlabel('Total Energy [keV]')
    ax.set_title(title, weight='bold')
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax.grid(axis='x', which='major', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.grid(axis='x', which='minor', linestyle=':', linewidth=0.7, alpha=0.35)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.margins(y=0.01)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, format="pdf", bbox_inches="tight")
    plt.show()
    plt.close(fig)

# ============================== CALLS ==============================
df = pd.read_csv(analysis.OUTPUT_CSV)
df.columns = df.columns.str.strip().str.replace(" ", "_")
default_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]

# --- Add mapping for isotope labels ---
isotope_labels = {
    "tc99m": r"$^{99\mathrm{m}}$Tc",
    "lu177": r"$^{177}$Lu",
}

iso_label = isotope_labels[iso]  # pick the right one based on input

# PLOT 1
group1_sum = summarise(df, 'Level1')
barh_simple(
    group1_sum.rename(columns={'Level1': 'Level_(Level_1)'}),
    y='Level_(Level_1)',
    title=f'Energy deposition within phantom, scanner, facility and TLDs - {iso_label}',
    colour_map_or_seq={
        'Phantom':  default_cycle[0],
        'Scanner':  default_cycle[1],
        'Facility': default_cycle[2],
        'TLDs':     default_cycle[3],
    },
    save_path=results_dir / "plot1_all_grouped.pdf"
)

# PLOT 2
phantom_sum = summarise(df.query('Level1 == "Phantom"'), 'Level2')
barh_simple(
    phantom_sum.rename(columns={'Level2': 'Phantom_Component'}),
    y='Phantom_Component',
    title=f'Energy deposition within phantom components - {iso_label}',
    colour_map_or_seq=tint_series(default_cycle[0], len(phantom_sum), start=0.4, end=1.0),
    save_path=results_dir / "plot2_phantom.pdf"
)

# PLOT 3
grouped_bar_plot(
    df, 'Level1 == "Scanner"',
    group_by='Level2', unit_col='Region',
    base_colour=default_cycle[1],
    title=f'Energy deposition within scanner components - {iso_label}',
    save_path=results_dir / "plot3_scanner.pdf",
    intra_bar_step=0.85, gap_lvl1=0.6, gap_lvl2=0.0
)

# PLOT 4
grouped_bar_plot(
    df, 'Level1 == "Facility"',
    levels=['Level2', 'Level3'], unit_col='Region',
    base_colour=default_cycle[2],
    title=f'Energy deposition within facility components - {iso_label}',
    save_path=results_dir / "plot4_facility.pdf",
    intra_bar_step=0.9, gap_lvl1=0.9, gap_lvl2=0.5
)