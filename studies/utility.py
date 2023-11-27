# ---------------------- Metadata ----------------------
#
# File name:  comparisons.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-27
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
import numpy as np
from scipy.stats import chisquare


def compute_chi2(observed, expected, covariance_matrix):
    residuals = observed - expected
    inv_covariance_matrix = np.linalg.inv(covariance_matrix)
    chi2 = np.dot(residuals.T, np.dot(inv_covariance_matrix, residuals))
    return chi2


def compute_triangular_discriminator(observed, expected):
    numerator = (observed - expected) ** 2
    denominator = observed + expected
    triangular_discriminator = 0.5 * np.trapz(numerator / denominator) * 10**3
    return triangular_discriminator


def compute_chi2_nocov(unfolded, truth):
    null_indices = truth == 0
    truth[null_indices] += 1
    unfolded[null_indices] += 1

    chi2, _ = chisquare(
        unfolded,
        np.sum(unfolded) / np.sum(truth) * truth,
    )
    dof = len(unfolded) - 1
    chi2_dof = chi2 / dof

    return chi2_dof
