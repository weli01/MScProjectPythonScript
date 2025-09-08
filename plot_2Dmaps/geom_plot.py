import matplotlib.pyplot as plt

def load_geom(filepath):
    """
    Parse a FLUKA/FLAIR geometry .dat file (PLOTGEOM export) and return polylines.

    Each .dat file represents a slice:
      - x=... → ZY plane (returns (z, y))
      - y=... → ZX plane (returns (z, x))
      - z=... → XY plane (returns (x, y))

    Returns
    -------
    polylines : list of list of (float, float)
        Each polyline is a list of 2D coordinates in cm for plotting.
    """
    import os
    plane = os.path.basename(filepath).lower()[0]  # 'x', 'y', or 'z'
    polylines = []
    current_poly = []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            # Blank line → end of polyline
            if line == "":
                if len(current_poly) >= 2:
                    polylines.append(current_poly)
                current_poly = []
                continue

            # Skip comments
            if line.startswith("#"):
                continue

            # Parse coordinates
            parts = line.split()
            if len(parts) == 5:
                u, v, x, y, z = map(float, parts)

                if plane == "y":      # ZX
                    current_poly.append((z, x))
                elif plane == "x":    # ZY
                    current_poly.append((z, y))
                elif plane == "z":    # XY
                    current_poly.append((x, y))

        # Add last polyline if file doesn’t end with a blank line
        if len(current_poly) >= 2:
            polylines.append(current_poly)

    return polylines



def plot_geom(filepath=None):
    """
    Plot geometry outline.
    If filepath is given, use it.
    If filepath is None, ask user interactively.
    """
    if filepath is None:
        filepath = input("Enter path to geometry .dat file: ").strip()

    polylines = load_geom(filepath)

    plt.figure(figsize=(8, 8))
    for poly in polylines:
        zs, xs = zip(*poly)
        plt.plot(zs, xs, 'k-', linewidth=0.5)

    plt.xlabel("z [cm]")
    plt.ylabel("x [cm]")
    plt.title("FLUKA Geometry Outline")
    plt.axis("equal")
    plt.grid(False)
    plt.show()

    return polylines


# If run directly from terminal: ask for file and plot
if __name__ == "__main__":
    plot_geom()
