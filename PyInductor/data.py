from __future__ import division
import numpy as np
from scipy.interpolate import interp2d


MATERIALS = {}
MATERIALS['Cu, annealed'] = {'rho': 17.241e-9, 'rho_t0': 20, 'temp_coeff_rho': 0.00393,
                             'mu_r': 0.99999044, 'temp_coeff_expan': 16.6e-6}
MATERIALS['Cu, hard-drawn'] = {'rho': 17.71e-9, 'rho_t0': 20, 'temp_coeff_rho': 0.00382,
                               'mu_r': 0.99999044, 'temp_coeff_expan': 16.6e-6}
MATERIALS['Ag'] = {'rho': 15.9e-9, 'rho_t0': 20, 'temp_coeff_rho': 0.0038,
                   'mu_r': 0.9999738, 'temp_coeff_expan': 14.2e-6}
MATERIALS['Al'] = {'rho': 28.24e-9, 'rho_t0': 20, 'temp_coeff_rho': 0.0039,
                   'mu_r': 1.00002212, 'temp_coeff_expan': 22.2e-6}
MATERIALS['Pt'] = {'rho': 100e-9, 'rho_t0': 20, 'temp_coeff_rho': 0.003,
                   'mu_r': 1.0002617, 'temp_coeff_expan': 9.0e-6}
MATERIALS['Zn'] = {'rho': 58 - 9, 'rho_t0': 20, 'temp_coeff_rho': 0.0037,
                   'mu_r': 0.9999844, 'temp_coeff_expan': 29.7e-6}


INF_D_S = 20

MEDHURST_L_D = np.array([0, 0.2, 0.4, 0.6, 0.8, 1, 2, 4, 6, 8, 10, INF_D_S])
MEDHURST_D_S = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

# x-axis: length/diam, y-axis: d/s
MEDHURST_MATRIX = np.array([
    [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.000, 1.00, 1.000],
    [1.02, 1.02, 1.03, 1.03, 1.03, 1.03, 1.04, 1.04, 1.04, 1.040, 1.04, 1.050],
    [1.07, 1.08, 1.08, 1.10, 1.10, 1.10, 1.13, 1.15, 1.16, 1.165, 1.17, 1.190],
    [1.16, 1.19, 1.21, 1.22, 1.23, 1.24, 1.28, 1.32, 1.34, 1.340, 1.35, 1.395],
    [1.20, 1.29, 1.33, 1.38, 1.42, 1.45, 1.50, 1.54, 1.56, 1.570, 1.58, 1.650],
    [1.44, 1.48, 1.54, 1.60, 1.64, 1.67, 1.74, 1.78, 1.80, 1.810, 1.83, 1.930],
    [1.74, 1.77, 1.83, 1.89, 1.92, 1.94, 1.98, 2.01, 2.03, 2.080, 2.10, 2.220],
    [2.12, 2.20, 2.28, 2.38, 2.44, 2.47, 2.32, 2.27, 2.29, 2.340, 2.27, 2.510],
    [2.74, 2.83, 2.97, 3.10, 3.20, 3.17, 2.74, 2.60, 2.60, 2.620, 2.65, 2.815],
    [3.73, 3.84, 3.99, 4.11, 4.17, 4.10, 3.36, 3.05, 2.92, 2.900, 2.93, 3.110],
    [5.31, 5.45, 5.65, 5.80, 5.80, 5.55, 4.10, 3.54, 3.31, 3.200, 3.23, 3.410]
])

proximity_factor = interp2d(MEDHURST_L_D, MEDHURST_D_S, MEDHURST_MATRIX)

__all__ = ['proximity_factor', 'MATERIALS']
