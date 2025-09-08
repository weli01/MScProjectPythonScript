import os
import sys
sys.path.append("/Users/weli/Documents/pyCharm/MPH5008/data_analysis/dose_calculations")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap, LogNorm
from matplotlib.ticker import LogLocator, LogFormatterMathtext, FixedLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

from usrbin_decode import decode_usrbin
from geom_plot import load_geom
from activity import cumulated_activity_Bq_s, HALF_LIFE_S, duration_seconds

plt.rcParams.update({'font.family': 'Trebuchet MS'})

# --- Helpers ---
def detect_run_type(bnn_file):
    """Determine run type from .bnn filename."""
    fname = os.path.basename(bnn_file).lower()
    if "21" in fname:
        return "pho_flu"
    elif "22" in fname:
        return "ele_flu"
    elif "23" in fname:
        return "amb_dose"
    else:
        raise ValueError(f"Unknown run type for file {bnn_file}")


def detect_isotope(bnn_file):
    """Detect isotope (tc99m or lu177) from bnn_file path."""
    path_lower = bnn_file.lower()
    if "tc99m" in path_lower:
        return "tc99m"
    elif "lu177" in path_lower:
        return "lu177"
    else:
        raise ValueError(f"Unknown isotope in path {bnn_file}")


def average_projection(array, x_edges, y_edges, z_edges, plane, coord, width, run_type):
    """Average a 3D USRBIN array into a 2D projection/slice, within ±width/2 slab."""
    half = width / 2

    if plane == "x":
        centres = 0.5 * (x_edges[:-1] + x_edges[1:])
        mask = (centres >= coord - half) & (centres <= coord + half)
        slice_avg = np.mean(array[mask, :, :], axis=0)
        extent = [z_edges[0], z_edges[-1], y_edges[0], y_edges[-1]]
        axis_labels = ("Z [cm]", "Y [cm]")

    elif plane == "y":
        centres = 0.5 * (y_edges[:-1] + y_edges[1:])
        mask = (centres >= coord - half) & (centres <= coord + half)
        slice_avg = np.mean(array[:, mask, :], axis=1)
        extent = [z_edges[0], z_edges[-1], x_edges[0], x_edges[-1]]
        axis_labels = ("Z [cm]", "X [cm]")

    elif plane == "z":
        centres = 0.5 * (z_edges[:-1] + z_edges[1:])
        mask = (centres >= coord - half) & (centres <= coord + half)
        slice_avg = np.mean(array[:, :, mask], axis=2).T
        extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
        axis_labels = ("X [cm]", "Y [cm]")

    else:
        raise ValueError("plane must be 'x', 'y', or 'z'")

    return slice_avg, extent, axis_labels


def detect_plane_from_filename(filename):
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    plane, coord = name.split("_", 1)
    return plane.lower(), float(coord)


def style_fancy_log_colorbar(cbar, label):
    decades = [0.01, 0.1, 1, 10, 100]
    cbar.set_ticks(decades)
    cbar.set_ticklabels([str(t) for t in decades])
    cbar.ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=range(2, 10)))
    cbar.ax.yaxis.set_ticklabels([], minor=True)
    cbar.set_label(label, fontweight="bold")


def style_value_colorbar(cbar, label):
    major_locator = LogLocator(base=10.0, subs=[1.0])
    cbar.ax.yaxis.set_major_locator(major_locator)

    vmin, vmax = cbar.mappable.norm.vmin, cbar.mappable.norm.vmax
    decades = np.floor(np.log10(vmin)), np.ceil(np.log10(vmax))
    minor_ticks = []
    for exp in range(int(decades[0]), int(decades[1]) + 1):
        for sub in range(2, 10):
            minor_ticks.append(sub * 10**exp)

    cbar.ax.yaxis.set_minor_locator(FixedLocator(minor_ticks))
    cbar.ax.yaxis.set_ticklabels([], minor=True)

    cbar.ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    cbar.set_label(label, fontweight="bold")


def add_axis_padding(ax, extent, pad=20):
    x0, x1 = extent[0], extent[1]
    y0, y1 = extent[2], extent[3]
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_ylim(y0 - pad, y1 + pad)


# --- Main ---
def main(bnn_file, dat_files, out_dir="plots", width=20):
    run_type = detect_run_type(bnn_file)
    isotope = detect_isotope(bnn_file)

    x_edges, y_edges, z_edges, values, errors = decode_usrbin(bnn_file)

    # Output directory
    out_base = os.path.join(out_dir, isotope, run_type)
    out_values = os.path.join(out_base, "values")
    out_errors = os.path.join(out_base, "errors")
    os.makedirs(out_values, exist_ok=True)
    os.makedirs(out_errors, exist_ok=True)

    # --- Colormaps ---
    magma_inv_hex = [
        "#ffffff", "#fefeef", "#fdfdde", "#fcfac9", "#fae99c",
        "#f9d86e", "#f7c750", "#f5b555", "#f3a35b", "#e98f64",
        "#d47873", "#bf6083", "#a74f88", "#8c4286", "#703584",
        "#5f2e7c", "#512972", "#432468", "#341f5d", "#241a53"
    ]
    fluka_hex = [
        "#ffffff", "#f0f0f0", "#e0e0e0", "#d7d1d8", "#dcc3d8", "#e1b5e5", "#e6a7eb", "#eb9af2", "#f18cf9", "#e970f8",
        "#e057f7", "#d74df7", "#c849f7", "#ba46f7", "#aa42ee", "#9a3cdf", "#8a36d0", "#612fce", "#312acd", "#0f29d1",
        "#112ce0", "#1330ef", "#1a41f6", "#2f72f7", "#45a2f8", "#4eb6f9", "#55c6fa", "#5ad0f4", "#56c7cf", "#52bea9",
        "#53c189", "#5ad073", "#6adf56", "#6fe853", "#8bf04c", "#aaf74c", "#bef84d", "#d1f94e", "#e1fa50", "#eefb51",
        "#fbfb52", "#fdf14f", "#fbe24a", "#f8d346", "#f6bd40", "#f3a639", "#f18832", "#ee6229", "#ed4424", "#e33e22",
        "#d4391f", "#c6351c", "#b73019", "#a72b16", "#972613", "#87210f", "#761b0c", "#571206", "#2e0602", "#000000"
    ]

    fluka_cmap = ListedColormap(fluka_hex, name="fluka")
    magma_inv_cmap = ListedColormap(magma_inv_hex, name="magma_inv")

    # --- Scaling ---
    if run_type == "amb_dose":
        if isotope == "tc99m":
            dur_s = duration_seconds("08:00", "08:30", strict_positive=True)  # example
            A_cum = cumulated_activity_Bq_s(500.0, "tc-99m", dur_s)
            factor = A_cum * 14 * 365 * 1e-9  # → mSv
            unit_label = "Annual H*(10) [mSv·year$^{-1}$]"
        elif isotope == "lu177":
            factor = 1e-9
            unit_label = "H*(10) [mSv·particle$^{-1}$]"
        else:
            raise ValueError(f"Unsupported isotope for amb_dose: {isotope}")
    else:  # fluence
        factor = 1.0
        if run_type == "pho_flu":
            unit_label = "Photon fluence [cm$^{-2}$·particle$^{-1}$]"
        elif run_type == "ele_flu":
            unit_label = "Electron fluence [cm$^{-2}$·particle$^{-1}$]"

    valid_vals = values[(values > 0) & np.isfinite(values)] * factor

    if run_type == "amb_dose" and isotope != "lu177":
        # Tc-99m (or any non-Lu-177 dose): enforce floor
        threshold = 1e-9
        global_vmin = max(threshold, np.nanmin(valid_vals))
    else:
        # Lu-177 dose and all fluence runs: free range
        global_vmin = np.nanmin(valid_vals)

    global_vmax = np.nanmax(valid_vals)

    for dat_file in dat_files:
        plane, coord = detect_plane_from_filename(dat_file)
        print(f"Processing {dat_file} (plane {plane}, coord {coord} cm, run={run_type}, isotope={isotope})")

        slice_vals, extent, (xlabel, ylabel) = average_projection(
            values, x_edges, y_edges, z_edges, plane, coord, width, run_type
        )
        slice_errs, _, _ = average_projection(
            errors, x_edges, y_edges, z_edges, plane, coord, width, run_type
        )

        # ----- Values plot -----
        data_vals = np.where(slice_vals > 0, slice_vals, np.nan) * factor
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(
            data_vals, origin="lower", extent=extent, aspect="equal",
            cmap=fluka_cmap, norm=LogNorm(vmin=global_vmin, vmax=global_vmax)
        )
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cbar = plt.colorbar(im, cax=cax)
        style_value_colorbar(cbar, unit_label)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if run_type == "amb_dose":
            title_base = "Ambient dose equivalent"
        elif run_type == "pho_flu":
            title_base = "Photon fluence"
        elif run_type == "ele_flu":
            title_base = "Electron fluence"
        ax.set_title(f"{title_base} - Value (plane: {plane.upper()} = {int(coord)} cm)", fontweight="bold")

        # Overlay geometry
        polylines = load_geom(dat_file)
        for poly in polylines:
            coords = np.array(poly)
            ax.plot(coords[:, 0], coords[:, 1], "k-", linewidth=0.5, zorder=5)

        # Contours only for dose values
        if run_type == "amb_dose" and isotope == "tc99m":
            contour_levels = [0.25, 1, 6, 20]
            contour_colors = ["#FF00A1", "#6C6CFF", "#4480DE", "#2CCAEA"]
            contour_styles = [(0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1, 1, 1))]
            ax.contour(
                data_vals, levels=contour_levels, colors=contour_colors,
                linewidths=0.7, linestyles=contour_styles, origin="lower", extent=extent, zorder=10
            )
            loc, anchor = "upper left", (0.0, 1.0)
            leg = ax.legend(
                [plt.Line2D([0], [0], color=c, lw=0.7, linestyle=ls) for c, ls in zip(contour_colors, contour_styles)],
                [f"{lv:g} mSv" for lv in contour_levels],
                title="Dose contours", loc=loc, bbox_to_anchor=anchor,
                fontsize="small", frameon=True, facecolor="white"
            )
            leg.set_zorder(20)

        add_axis_padding(ax, extent, pad=20)
        out_name = f"{plane}_{coord:+.0f}cm.png"
        fig.savefig(os.path.join(out_values, out_name), dpi=600, bbox_inches="tight")
        plt.close(fig)

        # ----- Errors plot -----
        data_errs = slice_errs * 100
        data_errs[data_errs <= 0] = np.nan
        bounds = np.logspace(-2, 2, 21)
        norm = BoundaryNorm(boundaries=bounds, ncolors=magma_inv_cmap.N)

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(
            data_errs, origin="lower", extent=extent, aspect="equal",
            cmap=magma_inv_cmap, norm=norm, interpolation="nearest"
        )
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cbar = plt.colorbar(im, cax=cax)
        style_fancy_log_colorbar(cbar, "Relative error [%]")

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if run_type == "amb_dose":
            title_base = "Ambient dose equivalent"
        elif run_type == "pho_flu":
            title_base = "Photon fluence"
        elif run_type == "ele_flu":
            title_base = "Electron fluence"
        ax.set_title(f"{title_base} - Uncertainty (plane: {plane.upper()} = {int(coord)} cm)", fontweight="bold")

        # Overlay geometry
        for poly in polylines:
            coords = np.array(poly)
            ax.plot(coords[:, 0], coords[:, 1], "k-", linewidth=0.5, zorder=5)


        contour_levels = [0.1, 1, 10]
        contour_colors = ["violet", "darkviolet", "magenta"]
        contour_styles = ["-", "--", ":"]
        ax.contour(
            data_errs, levels=contour_levels, colors=contour_colors,
            linewidths=0.7, linestyles=contour_styles, origin="lower", extent=extent, zorder=10
        )
        leg = ax.legend(
            [plt.Line2D([0], [0], color=c, lw=0.7, linestyle=ls) for c, ls in zip(contour_colors, contour_styles)],
            [f"{lv:g} %" for lv in contour_levels],
            title="Error contours", loc="upper left", bbox_to_anchor=(0.0, 1.0),
            fontsize="small", frameon=True, facecolor="white"
        )
        leg.set_zorder(20)

        add_axis_padding(ax, extent, pad=20)
        out_name = f"{plane}_{coord:+.0f}cm.png"
        fig.savefig(os.path.join(out_errors, out_name), dpi=600, bbox_inches="tight")
        plt.close(fig)

        print(f"Saved values -> {os.path.join(out_values, out_name)}")
        print(f"Saved errors -> {os.path.join(out_errors, out_name)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        bnn_file = input("Enter path to USRBIN .bnn file: ").strip()
    else:
        bnn_file = sys.argv[1]

    # Fixed geometry path
    geom_path = "/Users/weli/Documents/fluka/Projects/MSc/tc99m/main_study"

    dat_files = sorted([
        os.path.join(geom_path, f) for f in os.listdir(geom_path) if f.lower().endswith(".dat")
    ])
    dat_files = [f for f in dat_files if os.path.basename(f).lower().startswith(("x_", "y_", "z_"))]

    if not dat_files:
        raise FileNotFoundError(f"No x_*.dat, y_*.dat, or z_*.dat files found in {geom_path}")

    main(bnn_file, dat_files)
