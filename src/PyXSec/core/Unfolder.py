# ---------------------- Metadata ----------------------
#
# File name:  Unfolder.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-09
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
import ROOT

from QUnfold import QUnfoldQUBO
from QUnfold.utility import TMatrix_to_array, TH1_to_array

# Personal modules
from utils import transpose_matrix, array_to_TH1D


class Unfolder:
    """
    Class used to create an object which manages the unfolding for the Spectrum class.
    """

    def __init__(self, method, error, parameter, nToys=1000):
        """
        Set-up the unfolder for unfolding.

        Args:
            method (str): unfolding method.
            error (str): the error treatment type for unfolding.
            parameter (int): the unfolding parameter.
        """

        # Input variables
        self.method = method
        self.error = error
        self.parameter = parameter
        self.nToys = nToys

        # Histograms
        self.h_data = ROOT.TH1D()
        self.h_reco = ROOT.TH1D()
        self.h_truth = ROOT.TH1D()
        self.h_generated = ROOT.TH1D()
        self.h_response = ROOT.TH2D()
        self.h_unfolded = ROOT.TH1D()

        # Other
        self.m_unfolder = None
        self.transpose_response = False
        self.m_response = ROOT.RooUnfoldResponse()

    def set_data_histogram(self, histo):
        """
        Set the data histogram.

        Args:
            histo (TH1D): The input data histogram.
        """

        histo.Copy(self.h_data)
        self.h_data.SetName("unf_Data")
        self.h_data.SetDirectory(0)

    def set_reco_histogram(self, histo):
        """
        Set the reconstructed signal histogram.

        Args:
            histo (TH1D or None): The input histogram. If None, the internal histogram remains unchanged.

        """

        if histo is not None:
            histo.Copy(self.h_reco)
        self.h_reco.SetName("unf_SignalReco")
        self.h_reco.SetDirectory(0)

    def set_truth_histogram(self, histo):
        """
        Set the true signal histogram.

        Args:
            histo (TH1D or None): The input histogram. If None, the internal histogram remains unchanged.
        """

        if histo is not None:
            histo.Copy(self.h_truth)
        self.h_truth.SetName("unf_SignalTruth")
        self.h_truth.SetDirectory(0)

    def set_generated_histogram(self, histo):
        """
        Set the generated histogram.

        Args:
            histo (TH1D): The input histogram.
        """

        histo.Copy(self.h_generated)
        self.h_generated.SetName("unf_Generated")
        self.h_generated.SetDirectory(0)

    def set_response_histogram(self, histo, to_transpose=False):
        """
        Set the response matrix histogram.

        Args:
            histo (TH2D): The input response matrix histogram.
            to_transpose (bool, optional): Whether to transpose the response matrix. Default is False.

        """

        histo.Copy(self.h_response)
        self.h_response.SetName("unf_Response")
        self.transpose_response = to_transpose
        if self.transpose_response:
            transpose_matrix(self.h_response)
        self.h_response.SetDirectory(0)

    def do_unfold(self, keep_response=False):
        """
        Perform the unfolding.

        Args:
            keep_response (bool, optional): Whether to keep the existing response matrix. Default is False.
        """

        # Re-initialize the response if doesn't exist
        if keep_response == False:
            name = "{}_response".format(self.h_response.GetName())
            self.m_response = ROOT.RooUnfoldResponse(
                self.h_response.ProjectionX(),
                self.h_response.ProjectionY(),
                self.h_response,
                name,
                name,
            )
        self.m_response.UseOverflow(False)

        # Choose unfolding method
        if self.method == "Inversion":
            self.m_unfolder = ROOT.RooUnfoldInvert()
        elif self.method == "SVD":
            self.m_unfolder = ROOT.RooUnfoldSVD()
        elif self.method == "Bayes":
            self.m_unfolder = ROOT.RooUnfoldBayes()
            self.m_unfolder.SetSmoothing(0)
        elif self.method == "BinByBin":
            self.m_unfolder = ROOT.RooUnfoldBinByBin()
        elif self.method == "SimNeal":
            self.m_unfolder = QUnfoldQUBO(
                response=TMatrix_to_array(self.m_response.Mresponse(norm=True)),
                meas=TH1_to_array(self.h_data),
                lam=self.parameter,
            )

        if self.method != "SimNeal":
            self.m_unfolder.SetNToys(self.nToys)
            self.m_unfolder.SetRegParm(self.parameter)
            self.m_unfolder.SetVerbose(0)
            self.m_unfolder.SetResponse(self.m_response)
            self.m_unfolder.SetMeasured(self.h_data)

        # Unfolded distribution settings
        if self.error == "kNoError":
            if self.method == "SimNeal":
                h_unfolded_array = self.m_unfolder.solve_simulated_annealing(
                    num_reads=100
                )
                binning = [
                    self.h_data.GetXaxis().GetBinLowEdge(bin)
                    for bin in range(1, self.h_data.GetNbinsX() + 2)
                ]
                self.h_unfolded = array_to_TH1D(
                    bin_contents=h_unfolded_array,
                    binning=binning,
                    name=self.h_response.GetTitle(),
                    x_axis_name=self.h_data.GetXaxis().GetTitle(),
                    y_axis_name="",
                )
            else:
                self.h_unfolded = self.m_unfolder.Hunfold(self.m_unfolder.kNoError)
        elif self.error == "kCovToy":
            self.h_unfolded = self.m_unfolder.Hunfold(self.m_unfolder.kCovToys)
        self.h_unfolded.SetName("unf_Unfolded")
        self.h_unfolded.SetDirectory(0)

    def reset(self):
        """
        Reset the Unfolder object and associated histograms.
        """

        self.h_response.SetDirectory(0)
        self.m_unfolder.Reset()
        if self.method == "kBayes":
            self.unfolder.SetSmoothing(0)
        self.m_unfolder.SetVerbose(0)
