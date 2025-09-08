import numpy as np
import matplotlib.pyplot as plt
import sys
from usrbin_decode import decode_usrbin
from geom_plot import load_geom   # overlay support


def plot_usrbin_slice(
    filepath,
    axis="y",
    index=None,
    log=True,
    cmap="viridis",
    geom_file=None,
):
    """
    Plot a 2D slice from a FLUKA USRBIN file (decoded with usrbin_decode),
    optionally overlaying geometry outlines.

    Parameters
    ----------
    filepath : str
        Path to .bnn file
    axis : {"x", "y", "z"}, optional
        Which axis to slice along (default: "y")
    index : int or None
        Slice index along that axis. If None, take the middle slice.
    log : bool, optional
        Plot log10 of the values instead of raw values (default True)
    cmap : str, optional
        Matplotlib colormap
    geom_file : str or None
        If provided, overlay geometry outlines from this .dat file
    """
    x_edges, y_edges, z_edges, values, errors = decode_usrbin(filepath)

    nx, ny, nz = values.shape

    if axis == "x":
        if index is None:
            index = nx // 2
        data = values[index, :, :]
        extent = [z_edges[0], z_edges[-1], y_edges[0], y_edges[-1]]
        xlabel, ylabel = "z [cm]", "y [cm]"

    elif axis == "y":
        if index is None:
            index = ny // 2
        data = values[:, index, :]
        extent = [z_edges[0], z_edges[-1], x_edges[0], x_edges[-1]]
        xlabel, ylabel = "z [cm]", "x [cm]"

    elif axis == "z":
        if index is None:
            index = nz // 2
        data = values[:, :, index]
        extent = [y_edges[0], y_edges[-1], x_edges[0], x_edges[-1]]
        xlabel, ylabel = "y [cm]", "x [cm]"

    else:
        raise ValueError("axis must be 'x', 'y', or 'z'")

    # Log scale by default
    if log:
        data = np.where(data > 0, np.log10(data), np.nan)

    plt.figure(figsize=(8, 6))
    plt.imshow(
        data,
        origin="lower",
        extent=extent,
        aspect="auto",
        cmap=cmap,
    )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    cb_label = "log10(Value [GeV/cm³ per primary])" if log else "Value [GeV/cm³ per primary]"
    plt.colorbar(label=cb_label)
    plt.title(f"USRBIN slice: {axis}={index} ({filepath})")

    # Overlay geometry if requested
    if geom_file is not None:
        polylines = load_geom(geom_file)
        for poly in polylines:
            coords = np.array(poly)
            # coords are stored as (z, x) in load_geom
            zs, xs = coords[:, 0], coords[:, 1]
            plt.plot(zs, xs, "k-", linewidth=0.5)

    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        filepath = input("Enter path to USRBIN .bnn file: ").strip()
    else:
        filepath = sys.argv[1]

    # Optional geom overlay (2nd argument)
    geom_file = sys.argv[2] if len(sys.argv) > 2 else None

    plot_usrbin_slice(filepath, axis="y", index=None, log=True, geom_file=geom_file)
