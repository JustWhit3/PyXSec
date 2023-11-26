# ---------------------- Metadata ----------------------
#
# File name:  comparisons.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-26
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# TODO: i chi2 vanno calcolati con le covarianze
# TODO: gira con dati veri
# TODO: ratio plot

# STD modules
import argparse as ap
import os

# Data science modules
import uproot
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare
import math


def compute_chi2(unfolded, truth):
    # Trick for chi2 convergence
    null_indices = truth == 0
    truth[null_indices] += 1
    unfolded[null_indices] += 1

    # Compute chi2
    chi2, _ = chisquare(
        unfolded,
        np.sum(unfolded) / np.sum(truth) * truth,
    )
    dof = len(unfolded) - 1
    chi2_dof = chi2 / dof

    return chi2_dof


def plot_hist(qunfold, roounfold, theory):
    # Plot QUnfold data
    qunfold_val = qunfold.to_numpy()[0]
    qunfold_err = qunfold.variances()
    binning = qunfold.to_numpy()[1]
    bin_midpoints = 0.5 * (binning[:-1] + binning[1:])
    chi2_val = compute_chi2(qunfold.to_numpy()[0], theory.to_numpy()[0])
    expo = math.floor(math.log10(abs(chi2_val))) - 2
    chi2 = round(chi2_val, -expo)
    label = rf"SimNeal ($\chi^2 = {chi2}$)"

    plt.errorbar(
        y=qunfold_val,
        x=bin_midpoints,
        yerr=qunfold_err,
        ms=5,
        fmt="o",
        color="g",
        label=label,
    )

    # Plot RooUnfold data
    roounfold_val = roounfold.to_numpy()[0]
    roounfold_err = roounfold.variances()
    binning = roounfold.to_numpy()[1]

    chi2_val = compute_chi2(roounfold.to_numpy()[0], theory.to_numpy()[0])
    expo = math.floor(math.log10(abs(chi2_val))) - 2
    chi2 = round(chi2_val, -expo)
    label = rf"IBU ($\chi^2 = {chi2}$)"

    plt.errorbar(
        y=roounfold_val,
        x=bin_midpoints,
        yerr=roounfold_err,
        ms=5,
        fmt="v",
        color="r",
        label=label,
    )

    # Plot theory data
    theory_val = theory.to_numpy()[0]
    steps = np.append(theory_val, [theory_val[-1]])
    plt.step(binning, steps, label="Theory", where="post")

    # Plot settings
    var_name = "{}".format(qunfold.title).replace("(particle)", "").replace("#", "\\")
    plt.xlabel(
        r"${}$".format(var_name),
        loc="right",
    )
    if "Relative" in qunfold.name:
        plt.ylabel(r"$1 / \sigma \cdot d\sigma / d{}$".format(var_name), loc="top")
    elif "Absolute" in qunfold.name:
        plt.ylabel(r"$d\sigma / d{}$".format(var_name), loc="top")
    plt.title(qunfold.name)
    plt.xlim(binning[0], binning[-1])
    plt.ylim(0, plt.ylim()[1])
    plt.legend(loc="upper right")

    # Save
    plt.tight_layout()
    plt.savefig("studies/img/AbsoluteDiffXs.png")


def main():
    # Initial message
    print("RooUnfold file: {}".format(args.roounfold))
    print("QUnfold file: {}".format(args.qunfold))

    # Create output dirs
    if not os.path.exists("studies/img"):
        os.makedirs("studies/img")

    # Read QUnfold information
    file_QUnfold = uproot.open(args.qunfold)
    abs_Xs_QUnfold = file_QUnfold["AbsoluteDiffXs"]
    abs_theory = file_QUnfold["TheoryXs_abs"]

    # Read RooUnfold information
    file_RooUnfold = uproot.open(args.roounfold)
    abs_Xs_RooUnfold = file_RooUnfold["AbsoluteDiffXs"]

    # Plot stuff
    plot_hist(abs_Xs_QUnfold, abs_Xs_RooUnfold, abs_theory)


if __name__ == "__main__":
    # Parser settings
    parser = ap.ArgumentParser(description="Parsing input arguments.")
    parser.add_argument(
        "-q",
        "--qunfold",
        default="",
        help="Input root file with QUnfold results.",
    )
    parser.add_argument(
        "-r",
        "--roounfold",
        default="",
        help="Input root file with RooUnfold results.",
    )
    args = parser.parse_args()

    # Main part
    main()
