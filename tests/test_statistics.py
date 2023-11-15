# ---------------------- Metadata ----------------------
#
# File name:  test_statistics.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-14
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Testing modules
from hypothesis import given, strategies as st

# Data science modules
import ROOT

# Import the functions to be tested
from utils import transpose_matrix, divide_by_bin_width


@given(st.integers(min_value=1, max_value=10))
def test_transpose_matrix(square_size):
    """
    Test the transposition of a square matrix using the transpose_matrix function.

    Args:
        square_size (int): The size of the square matrix.
    """

    # Create the matrix
    h2 = ROOT.TH2D("", "", square_size, 0, square_size, square_size, 0, square_size)

    # Fill the matrix with random values
    for i in range(1, square_size + 1):
        for j in range(1, square_size + 1):
            h2.SetBinContent(i, j, i + j)
            h2.SetBinError(i, j, i + j / 2)

    # Transpose the matrix
    transpose_matrix(h2)

    # Check if the transposition is correct
    for i in range(1, h2.GetNbinsX() + 1):
        for j in range(1, h2.GetNbinsY() + 1):
            assert h2.GetBinContent(j, i) == i + j
            assert h2.GetBinError(j, i) == i + j / 2


@given(st.integers(min_value=1, max_value=10), st.floats(min_value=0.1, max_value=1.0))
def test_divide_by_bin_width(num_bins, error_value):
    """
    Test the divide_by_bin_width function for TH1 and TH2 histograms.

    Args:
        num_bins (int): Number of bins for the histograms.
        error_value (float): Constant error value for bin errors.
    """

    # Create a random TH1
    histo_th1 = ROOT.TH1D("histo_th1", "", num_bins, 0, num_bins)
    for i in range(1, num_bins + 1):
        content = i * 10.0  # Use a constant factor for content
        error = error_value
        histo_th1.SetBinContent(i, content)
        histo_th1.SetBinError(i, error)

    divide_by_bin_width(histo_th1)

    # Check if the division by bin width is correct for TH1
    for i in range(1, histo_th1.GetNbinsX() + 1):
        width = histo_th1.GetBinWidth(i)
        assert histo_th1.GetBinContent(i) == (i * 10.0) / width
        assert histo_th1.GetBinError(i) == error_value / width

    # Create a random TH2
    histo_th2 = ROOT.TH2D("histo_th2", "", num_bins, 0, num_bins, num_bins, 0, num_bins)
    for i in range(1, num_bins + 1):
        for j in range(1, num_bins + 1):
            content = (i + j) * 10.0  # Use a constant factor for content
            error = error_value
            histo_th2.SetBinContent(i, j, content)
            histo_th2.SetBinError(i, j, error)

    divide_by_bin_width(histo_th2)

    # Check if the division by bin width is correct for TH2
    for i in range(1, histo_th2.GetNbinsX() + 1):
        for j in range(1, histo_th2.GetNbinsY() + 1):
            widthX = histo_th2.GetXaxis().GetBinWidth(i)
            widthY = histo_th2.GetYaxis().GetBinWidth(j)
            width = widthX * widthY
            assert histo_th2.GetBinContent(i, j) == ((i + j) * 10.0) / width
            assert histo_th2.GetBinError(i, j) == error_value / width
