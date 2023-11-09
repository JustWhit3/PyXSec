# ---------------------- Metadata ----------------------
#
# File name:  Unfolder.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-09
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
import ROOT


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
        self.h_data = None
        self.h_reco = None
        self.h_truth = None
        self.h_generated = None
        self.h_response = None
        self.h_unfolded = None

        # Other
        self.m_unfolder = None

        # Choose unfolding method
        if self.method == "Inversion":
            self.m_unfolder = ROOT.RooUnfoldInvert()
        elif self.method == "SVD":
            self.m_unfolder = ROOT.RooUnfoldSVD()
        elif self.method == "Bayes":
            self.m_unfolder = ROOT.RooUnfoldBayes()
            self.m_unfolder.SetSmoothing(0)
            if self.parameter < 0:  # TODO: Maybe this can be removed
                self.parameter = 3
        elif self.method == "BinByBin":
            self.m_unfolder == ROOT.RooUnfoldBinByBin()
        self.m_unfolder.SetNToys(self.nToys)
        self.m_unfolder.SetRegParm(self.parameter)
