# ---------------------- Metadata ----------------------
#
# File name:  file_comparison.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-14
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
import ROOT


def test_histo_comparison():
    """
    Perform comparison among each histogram of the correct output file (produced by TTbarUnfold) and the output file produced by PyXSec.
    """

    file_output = "data/private/other/output_RooUnfold.root"
    file_correct = "data/private/other/output_correct.root"

    # Open ROOT files
    root_output = ROOT.TFile(file_output, "READ")
    root_correct = ROOT.TFile(file_correct, "READ")

    # Extract histograms from data
    data = {
        root_output.Get("Data"): root_correct.Get("Data"),
        root_output.Get("SignalReco"): root_correct.Get("SignalReco"),
        root_output.Get("Background"): root_correct.Get("Background"),
        root_output.Get("DataMinusBackground"): root_correct.Get("DataMinusBackground"),
        root_output.Get("SignalTruth"): root_correct.Get("SignalTruth"),
        root_output.Get("Efficiency"): root_correct.Get("Efficiency"),
        root_output.Get("Acceptance"): root_correct.Get("Acceptance"),
        root_output.Get("DataUnfolded"): root_correct.Get("DataUnfolded"),
        root_output.Get("AbsoluteDiffXs"): root_correct.Get("AbsoluteDiffXs"),
        root_output.Get("RelativeDiffXs"): root_correct.Get("RelativeDiffXs"),
        # root_output.Get("PullTestMean_abs"): root_correct.Get("PullTestMean_abs"),
        # root_output.Get("PullTestMean_rel"): root_correct.Get("PullTestMean_rel"),
        # root_output.Get("PullTestError_abs"): root_correct.Get("PullTestError_abs"),
        # root_output.Get("PullTestError_rel"): root_correct.Get("PullTestError_rel"),
        root_output.Get("Covariance_abs"): root_correct.Get("Covariance_abs"),
        root_output.Get("Covariance_rel"): root_correct.Get("Covariance_rel"),
        root_output.Get("Variance_abs"): root_correct.Get("Variance_abs"),
        root_output.Get("Variance_rel"): root_correct.Get("Variance_rel"),
        root_output.Get("Correlation_abs"): root_correct.Get("Correlation_abs"),
        root_output.Get("Correlation_rel"): root_correct.Get("Correlation_rel"),
        root_output.Get("TheoryXs_abs"): root_correct.Get("TheoryXs_abs"),
        root_output.Get("TheoryXs_rel"): root_correct.Get("TheoryXs_rel"),
    }

    for hist_output, hist_correct in data.items():
        # Check total bin number
        assert hist_output.GetNbinsX() == hist_correct.GetNbinsX()

        # Check each bin entry
        if hist_output.GetName() != "Response":
            for bin in range(1, hist_output.GetNbinsX() + 1):
                assert round(hist_output.GetBinContent(bin), 4) == round(
                    hist_correct.GetBinContent(bin), 4
                )
        else:
            for bin_x in range(1, hist_output.GetNbinsX() + 1):
                for bin_y in range(1, hist_output.GetNbinsY() + 1):
                    assert round(hist_output.GetBinContent(bin_x, bin_y), 4) == round(
                        hist_correct.GetBinContent(bin_x, bin_y), 4
                    )

    # Close files
    root_output.Close()
    root_correct.Close()
