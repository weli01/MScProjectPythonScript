import statistics
import numpy as np
import pandas as pd
from pathlib import Path


def read_csv(file_path):
    """Reads TLD dose values from CSV file and returns a pandas Series."""
    data = pd.read_csv(file_path, encoding='latin1')
    column_index = data.columns.get_loc('MeasuredDose [µSv]:')
    return pd.Series(
        [data.iloc[row, column_index] for row in range(1, len(data), 3)
         if not pd.isna(data.iloc[row, column_index])]
    )


def process_experimental(folder):
    """
    Reads experimental TLD doses from CSV, applies correction factors,
    and returns mean + std dev per triplet of TLDs.
    Returns:
        exp_dose_mean (np.ndarray), exp_dose_unc (np.ndarray)
    """
    # Read experimental doses
    study_type = Path(folder).name  # ensures we get just "main_study" or "pre_study"

    if study_type == "main_study":
        H = read_csv("/Users/weli/Documents/pyCharm/MPH5008/data_analysis/dose_calculations/TLD_readouts/readout_main.csv")
    elif study_type == "pre_study":
        H = read_csv("/Users/Weli/Documents/pyCharm/MPH5008/data_analysis/dose_calculations/TLD_readouts/readout_pre.csv")
    # Correction factors
    k_E = 1 / 0.8601
    k_d = 0.7183

    # Mean & std dev per triplet of TLDs
    H_mean = np.array([
        statistics.mean(H[i:i + 3])
        for i in range(0, len(H), 3)
    ])
    H_unc = np.array([
        statistics.stdev(H[i:i + 3])
        for i in range(0, len(H), 3)
    ])

    # Apply correction factors
    H_mean *= k_E * k_d

    return H_mean, H_unc