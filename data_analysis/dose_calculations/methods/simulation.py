import os
import re
import numpy as np
from pathlib import Path


def read_lis(file_path):
    """Extracts numerical values from .lis file (dose and uncertainty)."""
    with open(file_path, 'r') as file:
        content = file.read()
    matches = re.findall(r'[+-]?\d+\.\d{4}E[+-]?\d{2}', content)
    half_length = len(matches) // 2
    return ([float(match) for match in matches[:half_length]],
            [float(match) for match in matches[half_length:]])


def process_simulation(folder, A_cum):
    """
    Reads simulation dose results from .lis, applies normalisation, and returns doses + uncertainties in µSv.
    Returns:
        sim_dose (np.ndarray), sim_unc (np.ndarray)
    """

    path = Path(folder)
    study_name = path.name

    # Choose file based on folder
    if study_name == 'main_study':
        lis_file = os.path.join(folder, "run/run_25.bnn.lis")
    else:
        lis_file = os.path.join(folder, "run/run_23.bnn.lis")

    dose, unc = read_lis(lis_file)

    # Normalisation factor
    tld_vol = 0.32 * 0.32 * 0.09  # cm³
    pico_to_micro = 1e-6
    norm = A_cum / tld_vol * pico_to_micro

    # Apply normalisation to simulation
    dose = np.array(dose) * norm
    unc = np.array(unc) / 100 * dose

    return dose, unc