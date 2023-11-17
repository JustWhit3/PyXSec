# ---------------------- Metadata ----------------------
#
# File name:  processing.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-16
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Simulated process: gg -> tt~ -> l l~ nu nu~ b b~

# TODO: parallelizza
# TODO: unità di misura
# TODO: perchè alcuni eventi hanno solo un e o solo un mu?

# STD libraries
import argparse as ap
from tqdm import tqdm
import sys

# Data science modules
import uproot
import numpy as np
import awkward as ak


def make_particle_tree():
    """
    Create the particle-level tree to be added in the output root file.

    Returns:
        dict: list of branches of the new particle-level tree.
    """

    # Read ROOT file and trees
    print("\nProcessing {} file to make particle branch...".format(args.particle))
    file = uproot.open(args.particle)
    tree = file["LHEF"]

    # Filter particle level and get useful information
    particle_level = tree["Particle"]
    particle_info = particle_level.arrays(["Particle.PT", "Particle.PID"])

    # Variables
    leading_leptons_pt_list = []
    subleading_leptons_pt_list = []

    # Iterate over events
    for event in tqdm(particle_info, ncols=100):
        lepton_mask = (abs(event["Particle.PID"]) == 11) | (
            abs(event["Particle.PID"]) == 13
        )

        # Get leading and subleading lepton pT
        sorted_leptons_pT = ak.argsort(
            event["Particle.PT"][lepton_mask], axis=-1, ascending=False
        )
        leading_lepton_pT = event["Particle.PT"][lepton_mask][sorted_leptons_pT[0]]
        leading_leptons_pt_list.append(leading_lepton_pT)
        subleading_lepton_pT = event["Particle.PT"][lepton_mask][sorted_leptons_pT[1]]
        subleading_leptons_pt_list.append(subleading_lepton_pT)

    # Save information into particle tree
    particle_tree = {
        "pT_lep1": ak.from_iter(leading_leptons_pt_list),
        "pT_lep2": ak.from_iter(subleading_leptons_pt_list),
    }

    return particle_tree


def make_reco_tree():
    """
    Create the reco-level tree to be added in the output root file.

    Returns:
        dict: list of branches of the new reco-level tree.
    """

    # Read ROOT file and trees
    print("\nProcessing {} file to make reco branch...".format(args.reco))
    file = uproot.open(args.reco)
    tree = file["Delphes"]
    reco_info = tree.arrays(["Jet.Flavor", "Jet.PT", "Electron.PT", "Muon.PT"])

    # Variables
    leading_leptons_pt_list = []
    subleading_leptons_pt_list = []

    # Iterate over events
    for event in tqdm(reco_info, ncols=100):
        # Get leading and subleading leptons pT
        if len(event["Electron.PT"]) == 2 and len(event["Muon.PT"]) == 0:
            sorted_leptons_pT = ak.argsort(
                event["Electron.PT"], axis=-1, ascending=False
            )
            leading_lepton_pT = event["Electron.PT"][sorted_leptons_pT[0]]
            leading_leptons_pt_list.append(leading_lepton_pT)
            subleading_lepton_pT = event["Electron.PT"][sorted_leptons_pT[1]]
            subleading_leptons_pt_list.append(subleading_lepton_pT)
        elif len(event["Muon.PT"]) == 2 and len(event["Electron.PT"]) == 0:
            sorted_leptons_pT = ak.argsort(event["Muon.PT"], axis=-1, ascending=False)
            leading_lepton_pT = event["Muon.PT"][sorted_leptons_pT[0]]
            leading_leptons_pt_list.append(leading_lepton_pT)
            subleading_lepton_pT = event["Muon.PT"][sorted_leptons_pT[1]]
            subleading_leptons_pt_list.append(subleading_lepton_pT)
        elif len(event["Electron.PT"]) == 1 and len(event["Muon.PT"]) == 1:
            if event["Electron.PT"][0] > event["Muon.PT"][0]:
                leading_leptons_pt_list.append(event["Electron.PT"][0])
                subleading_leptons_pt_list.append(event["Muon.PT"][0])
            elif event["Electron.PT"][0] < event["Muon.PT"][0]:
                leading_leptons_pt_list.append(event["Muon.PT"][0])
                subleading_leptons_pt_list.append(event["Electron.PT"][0])
        else:
            print("A")

    # Save information into particle tree
    reco_tree = {
        "pT_lep1": ak.from_iter(leading_leptons_pt_list),
        "pT_lep2": ak.from_iter(subleading_leptons_pt_list),
    }

    return reco_tree


def main():
    # Create trees
    reco_level = make_reco_tree()
    particle_level = make_particle_tree()

    # Save output
    output = uproot.recreate(args.output)
    output["reco"] = reco_level
    output["particle"] = particle_level


if __name__ == "__main__":
    # Parser settings
    parser = ap.ArgumentParser(description="Parsing input arguments.")
    parser.add_argument(
        "-p",
        "--particle",
        default="",
        help="Particle-level file.",
    )
    parser.add_argument(
        "-r",
        "--reco",
        default="",
        help="Reco-level file.",
    )
    parser.add_argument(
        "-pr",
        "--particle-response",
        default="",
        help="Particle-level file for response matrix.",
    )
    parser.add_argument(
        "-rr",
        "--reco-response",
        default="",
        help="Reco-level file for response matrix.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="",
        help="Output root file name.",
    )
    args = parser.parse_args()

    # Main part
    main()
