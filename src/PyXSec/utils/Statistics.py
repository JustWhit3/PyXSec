# ---------------------- Metadata ----------------------
#
# File name:  Statistics.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-08
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
import ROOT


def quick_clone(obj, type):
    """
    Clone the object if it is not None, otherwise return None.

    Parameters:
        obj (object): The object to clone.
        type (type): The type of object to return.

    Returns:
        object: The cloned object or None if obj is None.
    """

    return obj if obj is None else type(obj.Clone())


def transpose_matrix(h2):
    """
    Transpose a matrix represented as a ROOT.TH2.

    Parameters:
        h2 (ROOT.TH2): The bidimensional histogram to transpose.
    """

    hTemp = quick_clone(h2, ROOT.TH2)
    hTemp.SetDirectory(0)
    h2.GetXaxis().SetTitle(h2.GetYaxis().GetTitle())
    h2.GetYaxis().SetTitle(h2.GetXaxis().GetTitle())
    h2.Transpose(hTemp)


def divide_by_bin_width(histo):
    """
    Divide histogram entries by bin width.

    Args:
        histo (ROOT.TH1/TH2): input histogram for bin width division.
    """

    if isinstance(histo, ROOT.TH1):
        nbins = histo.GetNbinsX()
        for i in range(1, nbins + 1):
            width = histo.GetBinWidth(i)
            content = histo.GetBinContent(i)
            error = histo.GetBinError(i)
            histo.SetBinContent(i, content / width)
            histo.SetBinError(i, error / width)
    elif isinstance(histo, ROOT.TH2):
        nbinsX = histo.GetNbinsX()
        nbinsY = histo.GetNbinsY()
        for i in range(1, nbinsX + 1):
            widthX = histo.GetXaxis().GetBinWidth(i)
            for j in range(1, nbinsY + 1):
                widthY = histo.GetYaxis().GetBinWidth(j)
                width = widthX * widthY
                content = histo.GetBinContent(i, j)
                error = histo.GetBinError(i, j)
                histo.SetBinContent(i, j, content / width)
                histo.SetBinError(i, j, error / width)


def run_toy(histo, toy_type):
    """
    Run a toy experiment on a ROOT histogram.

    Args:
        histo (ROOT.TH1): Input histogram.
        toy_type (str): Type of toy experiment. Use "Poisson" for Poisson distribution or any other string for Gaussian smearing.
    """

    nbins = histo.GetNbinsX()
    for i in range(1, nbins + 1):
        mean = histo.GetBinContent(i)
        if toy_type == "Poisson":
            smear = ROOT.gRandom.PoissonD(mean)
        else:
            smear = ROOT.gRandom.Gaus(mean, histo.GetBinError(i))
        histo.SetBinContent(i, smear)
