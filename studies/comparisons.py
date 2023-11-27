# ---------------------- Metadata ----------------------
#
# File name:  comparisons.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-26
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# STD modules
import argparse as ap
import os

# Data science modules
import uproot
import matplotlib.pyplot as plt
import numpy as np
import math

# My modules
from utility import compute_chi2, compute_triangular_discriminator, compute_chi2_nocov

# TODO: incertezza sulla teoria?
# TODO: scrivere i generatori
# TODO: Nei dati generare con un generatore diverso. D/T generati con un generatore (Herwig), mentre S/G generati con un altro (Pythia)
# TODO: Aggiungere lo smearing a mano?


def plot_hist(qunfold, roounfold, theory, cov_qunfold, cov_roounfold):
    # Divide into subplots
    print()
    fig = plt.figure()
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    # Plot QUnfold data
    qunfold_val = qunfold.to_numpy()[0]
    qunfold_err = qunfold.variances()
    binning = qunfold.to_numpy()[1]

    bin_midpoints = 0.5 * (binning[:-1] + binning[1:])
    chi2_val = compute_chi2(qunfold.to_numpy()[0], theory.to_numpy()[0], cov_qunfold.to_numpy()[0])
    expo_chi2 = math.floor(math.log10(abs(chi2_val))) - 2
    chi2_qunfold = round(chi2_val, -expo_chi2)
    label = rf"SimNeal ($\chi^2 = {chi2_qunfold}$)"
    marker_size = 3.5

    ax1.errorbar(
        y=qunfold_val,
        x=bin_midpoints,
        yerr=qunfold_err,
        ms=marker_size,
        fmt="o",
        color="g",
        label=label,
    )

    # Plot RooUnfold data
    roounfold_val = roounfold.to_numpy()[0]
    roounfold_err = roounfold.variances()
    binning = roounfold.to_numpy()[1]

    chi2_val = compute_chi2(
        roounfold.to_numpy()[0], theory.to_numpy()[0], cov_roounfold.to_numpy()[0]
    )
    expo = math.floor(math.log10(abs(chi2_val))) - 2
    chi2_roounfold = round(chi2_val, -expo)
    label = rf"IBU ($\chi^2 = {chi2_roounfold}$)"

    ax1.errorbar(
        y=roounfold_val,
        x=bin_midpoints,
        yerr=roounfold_err,
        ms=marker_size,
        fmt="v",
        color="r",
        label=label,
    )

    # Plot theory data
    theory_val = theory.to_numpy()[0]
    steps = np.append(theory_val, [theory_val[-1]])
    ax1.step(binning, steps, where="post")
    ax1.fill_between(binning, steps, step="post", alpha=0.3, label="Truth")

    # Plot ratio theory / truth
    ax2.step(binning, steps / steps, where="post", color="tab:blue")

    # Plot ratio QUnfold to truth
    ax2.errorbar(
        y=qunfold_val / theory_val,
        x=bin_midpoints,
        yerr=qunfold_err / theory_val,
        ms=marker_size,
        fmt="o",
        color="g",
        label=label,
    )

    # Plot ratio RooUnfold to truth
    ax2.errorbar(
        y=roounfold_val / theory_val,
        x=bin_midpoints,
        yerr=roounfold_err / theory_val,
        ms=marker_size,
        fmt="v",
        color="r",
        label=label,
    )

    # Plot style settings
    ax1.tick_params(axis="x", which="both", bottom=True, top=False, direction="in")
    ax2.tick_params(axis="x", which="both", bottom=True, top=True, direction="in")
    ax1.set_xlim(binning[0], binning[-1])
    ax1.set_ylim(0, ax1.get_ylim()[1])
    ax2.set_yticks([0.70, 0.85, 1, 1.15, 1.30])
    ax2.set_yticklabels(["", "0.85", "1", "1.15", ""])
    ax1.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)

    # Plot settings
    ax2.set_ylabel("Ratio to\ntruth")
    var_name = "{}".format(qunfold.title).replace("(particle)", "").replace("#", "\\")
    ax2.set_xlabel(
        r"${}$".format(var_name),
        loc="right",
    )
    if "Relative" in qunfold.name:
        ax1.set_ylabel(r"$1 / \sigma \cdot d\sigma / d{}$".format(var_name), loc="top")
    elif "Absolute" in qunfold.name:
        ax1.set_ylabel(r"$d\sigma / d{}$".format(var_name), loc="top")
    ax1.set_title(qunfold.name)

    ax1.legend(loc="upper right")

    # Save
    plt.tight_layout()
    plt.savefig("studies/img/comparisons/AbsoluteDiffXs.png")

    # Compute Triangular Discriminator metrics
    triangular_discriminator_val = compute_triangular_discriminator(
        qunfold.to_numpy()[0], theory.to_numpy()[0]
    )
    expo_triangular_discriminator = math.floor(math.log10(abs(triangular_discriminator_val))) - 2
    triangular_discriminator_qunfold = round(
        triangular_discriminator_val, -expo_triangular_discriminator
    )

    triangular_discriminator_val = compute_triangular_discriminator(
        roounfold.to_numpy()[0], theory.to_numpy()[0]
    )
    expo_triangular_discriminator = math.floor(math.log10(abs(triangular_discriminator_val))) - 2
    triangular_discriminator_roounfold = round(
        triangular_discriminator_val, -expo_triangular_discriminator
    )

    # Compute Chi2 without covariance metric
    chi2_val = compute_chi2_nocov(qunfold.to_numpy()[0], theory.to_numpy()[0])
    expo_chi2_val = math.floor(math.log10(abs(chi2_val))) - 2
    chi2_nocov_qunfold = round(chi2_val, -expo_chi2_val)

    chi2_val = compute_chi2_nocov(roounfold.to_numpy()[0], theory.to_numpy()[0])
    expo_chi2_val = math.floor(math.log10(abs(chi2_val))) - 2
    chi2_nocov_roounfold = round(chi2_val, -expo_chi2_val)

    # Show metrics
    print(qunfold.name, ": ")
    print("- SimNeal:")
    print("--> Chi2 =", chi2_qunfold)
    print("--> Chi2 (nocov) =", chi2_nocov_qunfold)
    print("--> TriangularDiscr =", triangular_discriminator_qunfold)

    print("- IBU:")
    print("--> Chi2 =", chi2_roounfold)
    print("--> Chi2 (nocov) =", chi2_nocov_roounfold)
    print("--> TriangularDiscr =", triangular_discriminator_roounfold)


def main():
    # Initial message
    print("RooUnfold file: {}".format(args.roounfold))
    print("QUnfold file: {}".format(args.qunfold))

    # Create output dirs
    if not os.path.exists("studies/img/comparisons"):
        os.makedirs("studies/img/comparisons")

    # Read QUnfold information
    file_QUnfold = uproot.open(args.qunfold)
    abs_Xs_QUnfold = file_QUnfold["AbsoluteDiffXs"]
    abs_theory = file_QUnfold["TheoryXs_abs"]
    abs_covariance_QUnfold = file_QUnfold["Covariance_abs"]

    # Read RooUnfold information
    file_RooUnfold = uproot.open(args.roounfold)
    abs_Xs_RooUnfold = file_RooUnfold["AbsoluteDiffXs"]
    abs_covariance_RooUnfold = file_RooUnfold["Covariance_abs"]

    # Plot stuff
    plot_hist(
        abs_Xs_QUnfold,
        abs_Xs_RooUnfold,
        abs_theory,
        abs_covariance_QUnfold,
        abs_covariance_RooUnfold,
    )


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
