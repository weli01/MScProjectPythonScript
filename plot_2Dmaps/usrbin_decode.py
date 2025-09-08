import numpy as np
import struct


def read_fortran_record(f):
    """Read one Fortran sequential record and return its payload as bytes."""
    nbytes_raw = f.read(4)
    if not nbytes_raw:
        return None
    nbytes = struct.unpack("i", nbytes_raw)[0]
    payload = f.read(nbytes)
    f.read(4)  # trailing length
    return payload


def decode_usrbin(filepath):
    """
    Decode a FLUKA USRBIN binary (.bnn) file (Cartesian mesh).

    Returns
    -------
    x_edges : np.ndarray
        Bin edges along x (length nx+1)
    y_edges : np.ndarray
        Bin edges along y (length ny+1)
    z_edges : np.ndarray
        Bin edges along z (length nz+1)
    values : np.ndarray
        3D array (nx, ny, nz) with scored values (e.g. GeV/cm^3 per primary)
    errors : np.ndarray
        3D array (nx, ny, nz) with relative 1-sigma errors
    """

    with open(filepath, "rb") as f:
        # Record 1: title (ignore)
        _ = read_fortran_record(f)

        # Record 2: parameters
        rec2 = read_fortran_record(f)
        # first 10 bytes = USRBIN name
        payload = rec2[10:]
        ints = np.frombuffer(payload, dtype=np.int32)
        floats = np.frombuffer(payload, dtype=np.float32)

        nx = ints[5]
        ny = ints[9]
        nz = ints[13]

        xlow, xhigh = floats[3], floats[4]
        ylow, yhigh = floats[7], floats[8]
        zlow, zhigh = floats[11], floats[12]

        # Record 3: values
        rec3 = read_fortran_record(f)
        values = np.frombuffer(rec3, dtype=np.float32, count=nx * ny * nz)
        values = values.reshape((nz, ny, nx)).transpose(2, 1, 0)

        # Record 4: small statistics block (ignore)
        _ = read_fortran_record(f)

        # Record 5: errors
        rec5 = read_fortran_record(f)
        errors = np.frombuffer(rec5, dtype=np.float32, count=nx * ny * nz)
        errors = errors.reshape((nz, ny, nx)).transpose(2, 1, 0)

    # Build bin edges
    x_edges = np.linspace(xlow, xhigh, nx + 1)
    y_edges = np.linspace(ylow, yhigh, ny + 1)
    z_edges = np.linspace(zlow, zhigh, nz + 1)

    return x_edges, y_edges, z_edges, values, errors


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        filepath = input("Enter path to USRBIN .bnn file: ").strip()
    else:
        filepath = sys.argv[1]

    x, y, z, vals, errs = decode_usrbin(filepath)
    print(f"Decoded {filepath}")
    print(f"Mesh shape: {vals.shape} (nx, ny, nz)")
    print(f"x range: {x[0]} → {x[-1]} cm")
    print(f"y range: {y[0]} → {y[-1]} cm")
    print(f"z range: {z[0]} → {z[-1]} cm")
