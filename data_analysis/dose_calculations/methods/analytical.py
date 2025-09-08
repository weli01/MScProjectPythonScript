import numpy as np
import math

def linear_att_coeff(mu_rho, rho):
    return mu_rho * rho

def beer_lambert_correction(A_cum, mu, x):
    return A_cum * math.exp(- mu * x)

# Distances [m]
distances = [
    3.7832209332985, # A1
    3.7861180960197, # A2
    2.6225983889604, # B1
    2.7741282422011, # B2
    3.5853801496205, # C1
    3.7878558348062, # C2
    2.3059536179589, # D
    0.74351103387945, # E1
    0.74351103387945, # E2
    1.6363707153897, # E3
    1.6363707153897  # E4
]

# Linear attenuation coefficients [m^-1]
mu_Pb = linear_att_coeff(2.3130, 11.35) * 100  # cm^-1 → m^-1
mu_Pb_glass = linear_att_coeff(1.7960, 6.22) * 100  # cm^-1 → m^-1

# Barrier thicknesses [m]
x_Pb_glass = 2.0 / 1000 # mm → m
x_Pb_wallB = 2.0 / 1000 # mm → m
x_Pb_wallC = 4.0 / 1000 # mm → m

# Equivalent dose gamma constant [mSv/h MBq]
gamma = 2.24E-5

def process_analytical(A_cum):
    """
    Returns (doses, uncertainties) for all TLDs.
    """

    A_cum_MBqh = A_cum / 3.6e9  # MBq·h

    doses = []
    for idx, d in enumerate(distances, start=1):
        corrected_A_cum = A_cum_MBqh
        if idx == 2:
            corrected_A_cum = beer_lambert_correction(corrected_A_cum, mu_Pb_glass, x_Pb_glass)
        elif idx == 4:
            corrected_A_cum = beer_lambert_correction(corrected_A_cum, mu_Pb, x_Pb_wallB)
        elif idx == 6:
            corrected_A_cum = beer_lambert_correction(corrected_A_cum, mu_Pb, x_Pb_wallC)

        H = (gamma * corrected_A_cum) / (d ** 2) * 1000 # mSv → µSv
        doses.append(H)

    doses = np.array(doses)
    unc = doses * 0.02  # 2% uncertainty from dose calibrator
    return doses, unc