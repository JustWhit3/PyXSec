# ---------------------- Metadata ----------------------
#
# File name:  processing.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-16
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Simulated process: gg -> tt~ -> l l~ nu nu~ b b~

# TODO: introdurre bias?
# TODO: barre di errore

# STD libraries
import argparse as ap
from tqdm import tqdm
from array import array

# Data science modules
import uproot
import awkward as ak
import ROOT


def get_lep_pT_at_particle_level(event):
    lepton_mask = (abs(event["Particle.PID"]) == 11) | (abs(event["Particle.PID"]) == 13)
    sorted_leptons_pT = ak.argsort(event["Particle.PT"][lepton_mask], axis=-1, ascending=False)
    leading_lepton_pT = event["Particle.PT"][lepton_mask][sorted_leptons_pT[0]]
    subleading_lepton_pT = event["Particle.PT"][lepton_mask][sorted_leptons_pT[1]]

    return leading_lepton_pT, subleading_lepton_pT


def get_trees_info(reco_file, particle_file):
    # Read ROOT file and trees
    file_reco = uproot.open(reco_file)
    tree_reco = file_reco["Delphes"]
    reco_info = tree_reco.arrays(["Jet.Flavor", "Jet.PT", "Electron.PT", "Muon.PT"])

    reco_pT_lep1_list = []
    reco_pT_lep2_list = []

    file_particle = uproot.open(particle_file)
    tree_particle = file_particle["LHEF"]
    particle_level = tree_particle["Particle"]
    particle_info = particle_level.arrays(["Particle.PT", "Particle.PID"])

    particle_pT_lep1_list = []
    particle_pT_lep2_list = []

    # Iterate over events
    for reco_event, particle_event in tqdm(
        zip(reco_info, particle_info), total=len(reco_info), ncols=100
    ):
        # Get leading and subleading leptons pT
        if len(reco_event["Electron.PT"]) == 2 and len(reco_event["Muon.PT"]) == 0:
            # Reco
            sorted_leptons_pT = ak.argsort(reco_event["Electron.PT"], axis=-1, ascending=False)
            reco_pT_lep1_list.append(reco_event["Electron.PT"][sorted_leptons_pT[0]])
            reco_pT_lep2_list.append(reco_event["Electron.PT"][sorted_leptons_pT[1]])

            # Particle
            particle_pT_lep1, particle_pT_lep2 = get_lep_pT_at_particle_level(particle_event)
            particle_pT_lep1_list.append(particle_pT_lep1)
            particle_pT_lep2_list.append(particle_pT_lep2)

        elif len(reco_event["Muon.PT"]) == 2 and len(reco_event["Electron.PT"]) == 0:
            # Reco
            sorted_leptons_pT = ak.argsort(reco_event["Muon.PT"], axis=-1, ascending=False)
            reco_pT_lep1_list.append(reco_event["Muon.PT"][sorted_leptons_pT[0]])
            reco_pT_lep2_list.append(reco_event["Muon.PT"][sorted_leptons_pT[1]])

            # Particle
            particle_pT_lep1, particle_pT_lep2 = get_lep_pT_at_particle_level(particle_event)
            particle_pT_lep1_list.append(particle_pT_lep1)
            particle_pT_lep2_list.append(particle_pT_lep2)
        elif len(reco_event["Electron.PT"]) == 1 and len(reco_event["Muon.PT"]) == 1:
            if reco_event["Electron.PT"][0] > reco_event["Muon.PT"][0]:
                # Reco
                reco_pT_lep1_list.append(reco_event["Electron.PT"][0])
                reco_pT_lep2_list.append(reco_event["Muon.PT"][0])

                # Particle
                particle_pT_lep1, particle_pT_lep2 = get_lep_pT_at_particle_level(particle_event)
                particle_pT_lep1_list.append(particle_pT_lep1)
                particle_pT_lep2_list.append(particle_pT_lep2)
            elif reco_event["Electron.PT"][0] < reco_event["Muon.PT"][0]:
                # Reco
                reco_pT_lep1_list.append(reco_event["Muon.PT"][0])
                reco_pT_lep2_list.append(reco_event["Electron.PT"][0])

                # Particle
                particle_pT_lep1, particle_pT_lep2 = get_lep_pT_at_particle_level(particle_event)
                particle_pT_lep1_list.append(particle_pT_lep1)
                particle_pT_lep2_list.append(particle_pT_lep2)

    # Binning
    # fmt: off
    pT_lep1_binning = [28.00, 34.00, 39.00, 45.00, 52.00, 61.00, 71.00, 83.00, 97.00, 115.00, 134.00, 158.00, 188.00, 223.00, 268.00, 338.00, 400.00]
    pT_lep2_binning = [28.00, 32.00, 37.00, 44.00, 51.00, 61.00, 73.00, 88.00, 105.00, 123.00, 150.00, 182.00, 223.00, 268.00, 338.00, 400.00]

    # Save information into particle tree
    reco_tree = {
        "pT_lep1": [ak.from_iter(reco_pT_lep1_list), pT_lep1_binning],
        "pT_lep2": [ak.from_iter(reco_pT_lep2_list), pT_lep2_binning],
    }

    particle_tree = {
        "pT_lep1": [ak.from_iter(particle_pT_lep1_list), pT_lep1_binning],
        "pT_lep2": [ak.from_iter(particle_pT_lep2_list), pT_lep2_binning],
    }

    return reco_tree, particle_tree


def main():
    # Create trees
    print("\nCreating particle- and reco-level trees:")
    print("- Reco file: {}".format(args.reco))
    print("- Particle file: {}".format(args.particle))
    reco_level, particle_level = get_trees_info(args.reco, args.particle)

    # Save output trees
    output = ROOT.TFile(args.output, "RECREATE")
    reco_dir = output.mkdir("reco")
    particle_dir = output.mkdir("particle")
    for h_reco, h_particle in zip(reco_level.keys(), particle_level.keys()):
        binning = reco_level[h_reco][1]
        bins = len(binning) - 1
        reco_histo = ROOT.TH1D(h_reco, h_reco, bins, array("d", binning))
        particle_name = "particle_{}".format(h_particle)
        particle_histo = ROOT.TH1D(particle_name, particle_name, bins, array("d", binning))
        x = ak.to_numpy(reco_level[h_reco][0])
        y = ak.to_numpy(particle_level[h_particle][0])
        for i in range(len(x)):
            reco_histo.Fill(x[i])
            particle_histo.Fill(y[i])
        reco_dir.cd()
        reco_histo.Write()
        particle_dir.cd()
        particle_histo.Write()

    # Create response matrices data
    print("\nCreating response matrices:")
    print("- Reco file: {}".format(args.reco_response))
    print("- Particle file: {}".format(args.particle_response))
    res_reco_level, res_particle_level = get_trees_info(args.reco_response, args.particle_response)

    # Create and save response matrices
    for h_reco, h_particle in zip(res_reco_level.keys(), res_particle_level.keys()):
        response_name = "particle_{0}_vs_{0}".format(h_reco)
        binning = reco_level[h_reco][1]
        bins = len(binning) - 1
        response = ROOT.TH2D(
            response_name, response_name, bins, array("d", binning), bins, array("d", binning)
        )
        x = ak.to_numpy(res_reco_level[h_reco][0])
        y = ak.to_numpy(res_particle_level[h_particle][0])
        for i in range(len(x)):
            response.Fill(x[i], y[i])
        response.Draw("colz")
        reco_dir.cd()
        response.Write()
    output.Close()


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
