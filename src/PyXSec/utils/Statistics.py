# ---------------------- Metadata ----------------------
#
# File name:  Statistics.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-08
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
import ROOT


def transpose_matrix(h2):
    """
    Transpose a matrix represented as a ROOT.TH2.

    Args:
        h2 (ROOT.TH2): The bidimensional histogram to transpose.
    """

    hTemp = h2.Clone()
    hTemp.SetDirectory(0)

    for i in range(1, h2.GetNbinsX() + 1):
        for j in range(1, h2.GetNbinsY() + 1):
            hTemp.SetBinContent(j, i, h2.GetBinContent(i, j))

    hTemp.GetXaxis().SetTitle(h2.GetYaxis().GetTitle())
    hTemp.GetYaxis().SetTitle(h2.GetXaxis().GetTitle())

    h2.Reset()
    h2.Add(hTemp)


def divide_by_bin_width(histo):
    """
    Divide histogram entries by bin width.

    Args:
        histo (ROOT.TH1/TH2): input histogram for bin width division.
    """

    if isinstance(histo, ROOT.TH1):
        for i in range(1, histo.GetNbinsX() + 1):
            width = histo.GetBinWidth(i)
            content = histo.GetBinContent(i)
            error = histo.GetBinError(i)
            histo.SetBinContent(i, content / width)
            histo.SetBinError(i, error / width)
    elif isinstance(histo, ROOT.TH2):
        for i in range(1, histo.GetNbinsX() + 1):
            widthX = histo.GetXaxis().GetBinWidth(i)
            for j in range(1, histo.GetNbinsY() + 1):
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
