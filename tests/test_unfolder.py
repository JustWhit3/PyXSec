import pytest
import ROOT
from core import Unfolder


@pytest.fixture
def create_unfolder_instance():
    """
    Fixture to create an instance of Unfolder for testing.

    Returns:
        Unfolder: An instance of the Unfolder class with default parameters.
    """
    return Unfolder(method="Inversion", error="kNoError", parameter=1, nToys=1000)


def test_initialization(create_unfolder_instance):
    """
    Test the initialization of the Unfolder class.

    Args:
        create_unfolder_instance: Fixture to create an Unfolder instance.
    """
    unfolder = create_unfolder_instance
    assert isinstance(unfolder, Unfolder)
    assert unfolder.method == "Inversion"
    assert unfolder.error == "kNoError"
    assert unfolder.parameter == 1
    assert unfolder.nToys == 1000


def test_set_data_histogram(create_unfolder_instance):
    """
    Test the set_data_histogram method of the Unfolder class.

    Args:
        create_unfolder_instance: Fixture to create an Unfolder instance.

    """
    unfolder = create_unfolder_instance
    histogram = ROOT.TH1D("test_data", "Test Data Histogram", 100, 0, 1)
    unfolder.set_data_histogram(histogram)
    assert unfolder.h_data.GetName() == "unf_Data"


def test_set_response_histogram(create_unfolder_instance):
    """
    Test the set_response_histogram method of the Unfolder class.

    Args:
        create_unfolder_instance: Fixture to create an Unfolder instance.

    """
    unfolder = create_unfolder_instance
    histogram = ROOT.TH2D(
        "test_response", "Test Response Histogram", 100, 0, 1, 100, 0, 1
    )
    unfolder.set_response_histogram(histogram)
    assert unfolder.h_response.GetName() == "unf_Response"


def test_do_unfold(create_unfolder_instance):
    """
    Test the do_unfold method of the Unfolder class.

    Args:
        create_unfolder_instance: Fixture to create an Unfolder instance.

    """
    unfolder = create_unfolder_instance
    data_histogram = ROOT.TH1D("test_data", "Test Data Histogram", 100, 0, 1)
    reco_histogram = ROOT.TH1D("test_reco", "Test Reco Histogram", 100, 0, 1)
    truth_histogram = ROOT.TH1D("test_truth", "Test Truth Histogram", 100, 0, 1)
    generated_histogram = ROOT.TH1D(
        "test_generated", "Test Generated Histogram", 100, 0, 1
    )
    response_histogram = ROOT.TH2D(
        "test_response", "Test Response Histogram", 100, 0, 1, 100, 0, 1
    )

    unfolder.set_data_histogram(data_histogram)
    unfolder.set_response_histogram(response_histogram)

    unfolder.do_unfold()
    assert unfolder.h_unfolded.GetName() == "unf_Unfolded"
