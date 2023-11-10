# ---------------------- Metadata ----------------------
#
# File name:  Spectrum.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-06
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Generic modules
import xml.etree.ElementTree as et
import sys
from tqdm import tqdm

# Data science modules
import ROOT

# Personal modules
from core.Unfolder import Unfolder
from utils import (
    get_custom_logger,
    try_parse_int,
    try_parse_float,
    try_parse_str,
    transpose_matrix,
    divide_by_bin_width,
    run_toy,
)

# Logger settings
log = get_custom_logger(__name__)

# Load RooUnfold
loaded_RooUnfold = ROOT.gSystem.Load("HEP_deps/RooUnfold/libRooUnfold.so")
if not loaded_RooUnfold == 0:
    log.error("RooUnfold not found!")
    sys.exit(0)


class Spectrum:
    """
    Class used to construct a spectrum object to unfold input data.
    """

    def __init__(self, config, systematic, output):
        """
        Constructor of the Spectrum class. Parse input data and create histograms.

        Args:
            config (str): XML configuration file.
            systematic (str): systematic to unfold. Default is "nominal".
            output (str): name of the output file. Default is "".
        """

        # Initialize input variables
        self.config = config
        self.syst_name = systematic
        self.output = output

        # Bool variables
        self.ignore_background = False
        self.use_default_regularization = False
        self.transpose_response = False
        self.is_initialized = False

        # String variables
        self.input_sig_path = ""
        self.input_data_path = ""
        self.input_res_path = ""
        self.input_gen_path = ""
        self.method = "Bayes"
        self.input_bkg_path = ""
        self.input_bkg_histo = ""
        self.histo_reco_path = ""
        self.histo_data_path = ""
        self.histo_res_path = ""
        self.histo_gen_path = ""
        self.staterr = ""
        self.m_toy_type = ""

        # Numeric variables
        self.reco_scale_factor = 1
        self.unfolding_parameter = -1
        self.br = 1.0
        self.do_efficiency_correction = 1
        self.do_total_cross_section = 0
        self.lumi = 0.0
        self.nToys = 10000
        self.m_nbins = 0
        self.m_bins = None
        self.m_totalXs = 0.0

        # Histograms
        self.h_data = ROOT.TH1D()
        self.h_signal_reco = ROOT.TH1D()
        self.h_signal_truth = ROOT.TH1D()
        self.h_response = ROOT.TH2D()
        self.h_generated = ROOT.TH1D()
        self.h_background = ROOT.TH1D()
        self.h_data_minus_bkg = ROOT.TH1D()
        self.h_efficiency = ROOT.TH1D()
        self.h_acceptance = ROOT.TH1D()
        self.h_data_unfolded = ROOT.TH1D()
        self.h_absXs = ROOT.TH1D()
        self.h_relXs = ROOT.TH1D()
        self.h_abs_pull_fit_mean = ROOT.TH1D()
        self.h_rel_pull_fit_mean = ROOT.TH1D()
        self.h_abs_pull_fit_error = ROOT.TH1D()
        self.h_rel_pull_fit_error = ROOT.TH1D()

        # Other
        self.m_output = None
        self.unfolder = None
        self.m_toy_tree = ROOT.TTree()

        # Prepare inputs
        self._configure()
        self._load_histograms()
        self._initialize()

    def _configure(self):
        """
        Parse all the information from input configuration file.
        """

        # Initialize XML parser
        tree = et.parse(self.config)
        root = tree.getroot()

        # Read basic quantities from config
        self.br = try_parse_float(self.br, root, "br", "value")
        self.lumi = try_parse_float(self.lumi, root, "lumi", "value")

        # Read file paths
        self.input_sig_path = try_parse_str(self.input_sig_path, root, "sig", "file")
        self.input_data_path = try_parse_str(self.input_data_path, root, "data", "file")
        self.input_res_path = try_parse_str(self.input_res_path, root, "res", "file")
        self.input_gen_path = try_parse_str(self.input_gen_path, root, "gen", "file")

        # Read background information
        self.input_bkg_path = try_parse_str(self.input_bkg_path, root, "bkg", "file")
        self.input_bkg_histo = try_parse_str(self.input_bkg_histo, root, "bkg", "hpath")
        if self.input_bkg_path == "" or self.input_bkg_histo == "":
            log.warning(
                "Background path or histogram is empty, we will not subtract the background"
            )
            self.ignore_background = True
        else:
            log.info("Background path: {}".format(self.bkg_path))

        # Read histogram paths
        self.histo_reco_path = try_parse_str(self.histo_reco_path, root, "sig", "hpath")
        self.histo_data_path = try_parse_str(
            self.histo_data_path, root, "data", "hpath"
        )
        self.histo_res_path = try_parse_str(self.histo_res_path, root, "res", "hpath")
        self.histo_gen_path = try_parse_str(self.histo_gen_path, root, "gen", "hpath")

        # Read unfolding information
        self.method = try_parse_str(self.method, root, "unfolding", "method")
        self.unfolding_parameter = try_parse_int(
            self.unfolding_parameter, root, "unfolding", "regularization"
        )
        if self.unfolding_parameter < 0:
            self.use_default_regularization = True
        self.nToys = try_parse_int(self.nToys, root, "unfolding", "ntoys")
        self.staterr = try_parse_str(self.staterr, root, "unfolding", "statErr")

        # Read other parameters
        self.do_total_cross_section = try_parse_int(
            self.do_total_cross_section, root, "do_total", "value"
        )
        self.reco_scale_factor = try_parse_float(
            self.reco_scale_factor, root, "reco_scale", "value"
        )
        self.do_efficiency_correction = try_parse_int(
            self.do_efficiency_correction, root, "do_eff", "value"
        )

        # Print unfolding information
        log.info(
            "Unfolding the \x1b[38;5;171m{0}\x1b[0m systematic".format(self.syst_name)
        )
        log.info(
            "Unfolding using \x1b[38;5;171m{0}\x1b[0m method with unfolding parameter set to \x1b[38;5;171m{1}\x1b[0m".format(
                self.method, self.unfolding_parameter
            )
        )
        log.info(
            "Using \x1b[38;5;171m{0}\x1b[0m branching ratio and \x1b[38;5;171m{1}\x1b[0m integrated luminosity".format(
                self.br, self.lumi
            )
        )

    def _load_histograms(self):
        """
        Load histograms from input data read with _configure() method.
        """

        # Load data histogram
        log.info("Loading data histogram file from: {}".format(self.input_data_path))
        f_temp = ROOT.TFile.Open(self.input_data_path)
        h_temp = None
        f_temp.cd()
        h_temp = ROOT.gDirectory.Get(self.histo_data_path)
        if self.do_total_cross_section == 0:
            self.h_data = h_temp.Clone()
        else:
            self.h_data = ROOT.TH1D("h_data", "data", 1, 0, 1)
            integral, error = 0, 0
            integral = h_temp.IntegralAndError(1, h_temp.GetNbinsX(), error)
            self.h_data.SetBinContent(1, integral)
            self.h_data.SetBinError(1, error)
        self.h_data.SetDirectory(0)
        f_temp.Close()
        self.h_data.ClearUnderflowAndOverflow()
        self.h_data.Scale(self.reco_scale_factor)
        log.info(
            "Rescaling the data by \x1b[38;5;171m{}\x1b[0m".format(
                self.reco_scale_factor
            )
        )
        self.h_data.SetName("Data_{}".format(self.syst_name))

        # Load signal-reco histogram
        log.info(
            "Loading signal-reco histogram file from: {}".format(self.input_sig_path)
        )
        f_temp = ROOT.TFile.Open(self.input_sig_path)
        f_temp.cd()
        h_temp = ROOT.gDirectory.Get(self.histo_reco_path)
        if self.do_total_cross_section == 0:
            self.h_signal_reco = h_temp.Clone()
        else:
            self.h_signal_reco = ROOT.TH1D("h_signalReco", "signalReco", 1, 0, 1)
            integral, error = 0, 0
            integral = h_temp.IntegralAndError(1, h_temp.GetNbinsX(), error)
            self.h_signal_reco.SetBinContent(1, integral)
            self.h_signal_reco.SetBinError(1, error)
        self.h_signal_reco.ClearUnderflowAndOverflow()
        self.h_signal_reco.SetDirectory(0)

        # Load response matrix
        log.info("Loading response matrix file from: {}".format(self.input_res_path))
        f_temp = ROOT.TFile.Open(self.input_res_path)
        f_temp.cd()
        h_response_temp = ROOT.gDirectory.Get(self.histo_res_path)
        if self.do_total_cross_section == 0:
            label = h_response_temp.GetXaxis().GetBinLabel(1)
            if label == "":  # this means that we are doing a 2D unfolding
                binningX = h_response_temp.GetXaxis().GetXbins().GetArray()
                binningY = h_response_temp.GetYaxis().GetXbins().GetArray()
                self.h_response = ROOT.TH2D(
                    "response_tmp",
                    "response_tmp",
                    h_response_temp.GetNbinsX(),
                    binningX,
                    h_response_temp.GetNbinsY(),
                    binningY,
                )
                for i in range(1, h_response_temp.GetNbinsY() + 1):
                    for j in range(1, h_response_temp.GetNbinsX() + 1):
                        self.h_response.SetBinContent(
                            j, i, h_response_temp.GetBinContent(j, i)
                        )
                        self.h_response.SetBinError(
                            j, i, h_response_temp.GetBinError(j, i)
                        )
            else:
                self.h_response = h_response_temp.Clone()
        else:
            self.h_response = ROOT.TH2D("response", "response", 1, 0, 1, 1, 0, 1)
            integral, error = 0, 0
            integral = h_response_temp.IntegralAndError(
                1, h_response_temp.GetNbinsX(), 1, h_response_temp.GetNbinsY(), error
            )
            self.h_response.SetBinContent(1, 1, integral)
            self.h_response.SetBinError(1, 1, error)
        self.h_response.ClearUnderflowAndOverflow()
        if self.transpose_response == True:
            transpose_matrix(self.h_response)
        self.h_response.SetDirectory(0)
        f_temp.Close()

        # Loading generated histogram
        if self.do_efficiency_correction == 1:
            log.info(
                "Loading generated histogram file from: {}".format(self.input_sig_path)
            )
            f_temp = ROOT.TFile.Open(self.input_gen_path)
            f_temp.cd()
            h_temp = f_temp.Get(self.histo_gen_path)
            if self.do_total_cross_section == 0:
                self.h_generated = h_temp.Clone()
            else:
                self.h_generated = ROOT.TH1D("generated", "generated", 1, 0, 1)
                integral, error = 0, 0
                integral = h_temp.IntegralAndError(1, h_temp.GetNbinsX(), error)
                self.h_generated.SetBinContent(1, integral)
                self.h_generated.SetBinError(1, error)
            self.h_generated.SetDirectory(0)
            f_temp.Close()
        else:
            self.h_generated = self.h_response.ProjectionY()
        self.h_generated.Scale(1.0 / self.br)
        f_temp = 0
        self.m_nbins = self.h_generated.GetNbinsX()
        self.h_generated.ClearUnderflowAndOverflow()
        self.m_bins = [
            self.h_generated.GetXaxis().GetXbins().At(i)
            for i in range(self.m_nbins + 1)
        ]

        # Loading background histogram
        if self.ignore_background == False:
            log.info("Loading background file {0}".format(self.input_bkg_path))
            f_temp = ROOT.TFile.Open(self.input_bkg_path)
            f_temp.cd()
            h_temp = f_temp.Get(self.histo_reco_path)
            if self.do_total_cross_section == 0:
                self.h_background = h_temp.Clone()
            else:
                self.h_background = ROOT.TH1D("h_allBkg", "h_allBkg", 1, 0, 1)
                integral, error = 0, 0
                integral = h_temp.IntegralAndError(1, h_temp.GetNbinsX(), error)
                self.h_background.SetBinContent(1, integral)
                self.h_background.SetBinError(1, error)
            self.h_background.ClearUnderflowAndOverflow()
            self.h_background.SetDirectory(0)
            f_temp.Close()
        else:
            self.h_background = self.h_data.Clone()
            self.h_background.Reset()
            self.h_background.SetDirectory(0)

    def _initialize(self):
        """
        Initialize histograms loaded with _load_histograms() method and the Unfolder interface.
        """

        # Initial settings
        log.info("Initializing loaded histograms...")
        if self.output == "":
            self.output = "{0}_{1}_{2}_DiffXs.root".format(
                self.syst_name, self.method, self.unfolding_parameter
            )
            log.warning(
                "Output file path not provided. Setting it to {}".format(self.output)
            )
        self.m_output = ROOT.TFile.Open(self.output, "RECREATE")
        if self.is_initialized == True:
            log.warning(
                "Initializing spectrum {0}, but it appears to be already initialized. Skipping...".format(
                    self.syst_name
                )
            )
            return

        # Data histogram
        self.h_data.SetName("Data")
        self.h_data.SetDirectory(self.m_output)

        # Signal-reco histogram
        self.h_signal_reco.SetDirectory(self.m_output)
        self.h_signal_reco.SetName("SignalReco")

        # Response histogram
        self.h_response.SetDirectory(self.m_output)
        self.h_response.SetName("Response")

        # Background histogram
        self.h_background.SetDirectory(self.m_output)
        self.h_background.SetName("Background")

        # Generated histogram
        self.h_generated.SetName("Generated")
        self.h_generated.SetDirectory(self.m_output)

        # Perform background subtraction
        log.info("Performing background subtraction...")
        self.h_data_minus_bkg = self.h_data.Clone("DataMinusBackground")
        self.h_data_minus_bkg.SetDirectory(self.m_output)
        if not self.ignore_background:
            self.h_data_minus_bkg.Add(self.h_background, -1)

        # Initialize the unfolding parameter
        if self.use_default_regularization == True:
            if self.method == "Bayes":
                self.unfolding_parameter = 4
            if self.method == "SVD":
                self.unfolding_parameter = self.h_data.GetNbinsX() // 2
                if self.unfolding_parameter < 2:
                    self.unfolding_parameter = 2

        # Initialize unfolder settings
        staterr_arr = self.staterr.split(
            ":"
        )  # TODO: qui si può rimuovere un po' di roba
        if len(staterr_arr) == 1 and staterr_arr[0] == "analytical":
            self.unfolder = Unfolder(
                self.method, "kCovToy", self.unfolding_parameter, self.nToys
            )
        else:
            self.unfolder = Unfolder(self.method, "kNoError", self.unfolding_parameter)
            if len(staterr_arr) == 1 and staterr_arr[0] == "toys":
                if self.syst_name != "MCstat":
                    self.m_toy_type = "Poisson"
                else:
                    self.m_toy_type = "Gauss"
            elif len(staterr_arr) == 2 and staterr_arr[0] == "toys":
                self.m_toy_type = staterr_arr[1]
            elif staterr_arr[0] != "none":
                raise RuntimeError("Stat err parameter badly formatted!")
            log.info(
                "Statistical uncertainty evaluated using {0} toys".format(
                    self.m_toy_type
                )
            )
        self.is_initialized = True

    def compute_differential_cross_sections(self, error="kNoError"):
        """
        Compute differential cross sections measurement using input data parsed from the XML configuration file.

        Args:
            error (str, optional): the error treatment type for unfolding. Defaults to "kNoError".
        """

        # Set dir as root
        ROOT.gDirectory.cd()  # TODO: check this

        # Signal truth histogram
        self.h_signal_truth = self.h_response.ProjectionY(
            "SignalTruth", 1, self.m_nbins
        )
        self.h_signal_truth.SetDirectory(self.m_output)

        # Evaluate the efficiency
        self.h_efficiency = self.h_response.ProjectionY("Efficiency", 1, self.m_nbins)
        self.h_efficiency.SetDirectory(self.m_output)
        self.h_efficiency.Divide(self.h_generated)

        # Evaluate the acceptance
        self.h_acceptance = self.h_response.ProjectionX("Acceptance", 1, self.m_nbins)
        self.h_acceptance.Divide(self.h_signal_reco)
        self.h_acceptance.SetDirectory(self.m_output)

        # Data - background subtraction
        h_data_minus_background_corrected = self.h_data_minus_bkg.Clone(
            "DataMinusBkgCorrected"
        )
        h_data_minus_background_corrected.SetTitle("(Data - Bkg ) x Acceptance")
        h_data_minus_background_corrected.SetDirectory(self.m_output)
        h_data_minus_background_corrected.Multiply(self.h_acceptance)

        # Set-up unfolder
        self.unfolder.set_data_histogram(h_data_minus_background_corrected)
        self.unfolder.set_reco_histogram(self.h_signal_reco)
        self.unfolder.set_truth_histogram(self.h_signal_truth)
        self.unfolder.set_generated_histogram(self.h_generated)
        self.unfolder.set_response_histogram(self.h_response)
        self.unfolder.do_unfold()

        # Create absolute cross-section
        self.h_data_unfolded = self.unfolder.h_unfolded.Clone("DataUnfolded")
        self.h_data_unfolded.SetDirectory(self.m_output)
        self.h_absXs = self.unfolder.h_unfolded.Clone()
        self.h_absXs.SetName("AbsoluteDiffXs")
        self.h_absXs.SetDirectory(self.m_output)

        # Apply efficiency correction
        self.h_absXs.Divide(self.h_efficiency)
        self.m_totalXs = self.h_absXs.Integral()
        log.info("Total cross-section (abs/eff): {}".format(self.m_totalXs))
        self.h_relXs = self.h_absXs.Clone("RelativeDiffXs")
        self.h_relXs.Scale(1.0 / self.m_totalXs)
        divide_by_bin_width(self.h_relXs)
        divide_by_bin_width(self.h_absXs)
        self.h_absXs.Scale(1 / self.lumi)

        # Uncertainty code
        self.m_nbins = self.h_absXs.GetNbinsX()
        ROOT.gDirectory.cd()
        if self.nToys > 0:

            # Variables
            h_bin_toys_data = [ROOT.TH1D() for _ in range(self.m_nbins)]
            h_bin_toys_unfold = [ROOT.TH1D() for _ in range(self.m_nbins)]
            h_bin_toys_rel = [ROOT.TH1D() for _ in range(self.m_nbins)]
            h_bin_toys_abs = [ROOT.TH1D() for _ in range(self.m_nbins)]
            h_bin_toys_rel_pull = [ROOT.TH1D() for _ in range(self.m_nbins)]
            h_bin_toys_abs_pull = [ROOT.TH1D() for _ in range(self.m_nbins)]
            func_abs = [ROOT.TF1() for _ in range(self.m_nbins)]
            func_rel = [ROOT.TF1() for _ in range(self.m_nbins)]
            func_abs_pull = [ROOT.TF1() for _ in range(self.m_nbins)]
            func_rel_pull = [ROOT.TF1() for _ in range(self.m_nbins)]
            v_branch_rel = [0.0] * self.m_nbins
            v_branch_abs = [0.0] * self.m_nbins

            h_totalXs = ROOT.TH1D(
                "totalXs", "totalXs", 100, 0.5 * self.m_totalXs, 1.5 * self.m_totalXs
            )
            h_data_smeared = ROOT.TH1D()
            h_data_smeared_corrected = ROOT.TH1D()
            h_bkg_smeared = ROOT.TH1D()
            h_efficiency_smeared = ROOT.TH1D()
            h_acceptance_smeared = ROOT.TH1D()
            h_generated_smeared = ROOT.TH1D()
            h_signal_reco_smeared = ROOT.TH1D()
            h_signal_truth_smeared = ROOT.TH1D()
            h_response_smeared = ROOT.TH2D()
            h_relXs_smeared = ROOT.TH1D()
            h_absXs_smeared = ROOT.TH1D()

            integratedXs_smeared = 0
            f_toys = ROOT.TFile()

            ROOT.gDirectory.cd()  # TODO: check this
            h_unfolded = self.unfolder.h_unfolded.Clone()
            h_unfolded.SetDirectory(0)
            self.h_abs_pull_fit_mean = h_unfolded.Clone("PullTestMean_abs")
            self.h_abs_pull_fit_mean.Reset()
            self.h_abs_pull_fit_error = h_unfolded.Clone("PullTestError_abs")
            self.h_abs_pull_fit_error.Reset()

            self.h_rel_pull_fit_mean = h_unfolded.Clone("PullTestMean_rel")
            self.h_rel_pull_fit_mean.Reset()
            self.h_rel_pull_fit_error = h_unfolded.Clone("PullTestError_rel")
            self.h_rel_pull_fit_error.Reset()

            # Allocate the histograms
            for i in range(0, self.m_nbins):

                # Compute error mean and relative error
                error = self.h_data.GetBinError(i + 1)
                rel_err = 4 * error / self.h_data_minus_bkg.GetBinContent(i + 1)

                # Relative toy bin
                mean = self.h_relXs.GetBinContent(i + 1)
                h_bin_toys_rel[i] = ROOT.TH1D(
                    f"Rel_toy_bin_{i}",
                    f"Rel_toy_bin_{i}",
                    100,
                    (1 - 1.5 * rel_err) * mean,
                    (1 + 1.5 * rel_err) * mean,
                )
                h_bin_toys_rel[i].SetDirectory(self.m_output)
                h_bin_toys_rel_pull[i] = ROOT.TH1D(
                    f"Rel_toyPull_bin_{i}", f"Rel_toyPull_bin_{i}", 100, -3, 3
                )
                h_bin_toys_rel_pull[i].SetDirectory(self.m_output)
                func_rel[i] = ROOT.TF1(
                    f"Gaus_rel_{i}",
                    "gaus(0)",
                    (1 - 1.5 * rel_err) * mean,
                    (1 + 1.5 * rel_err) * mean,
                )
                func_rel_pull[i] = ROOT.TF1(f"GausPull_rel_{i}", "gaus(0)", -3, 3)
                func_rel_pull[i].SetParameter(2, 1)

                # Absolute toy bin
                mean = self.h_absXs.GetBinContent(i + 1)
                h_bin_toys_abs[i] = ROOT.TH1D(
                    f"Abs_toy_bin_{i}",
                    f"Abs_toy_bin_{i}",
                    100,
                    (1 - 1.5 * rel_err) * mean,
                    (1 + 1.5 * rel_err) * mean,
                )
                h_bin_toys_abs[i].SetDirectory(self.m_output)
                mean = self.h_data.GetBinContent(i + 1)
                h_bin_toys_abs[i] = ROOT.TH1D(
                    f"Data_toy_bin_{i}",
                    f"Data_toy_bin_{i}",
                    100,
                    (1 - 1.5 * rel_err) * mean,
                    (1 + 1.5 * rel_err) * mean,
                )
                h_bin_toys_abs[i].SetDirectory(self.m_output)
                h_bin_toys_abs_pull[i] = ROOT.TH1D(
                    f"Abs_toyPull_bin_{i}", f"Abs_toyPull_bin_{i}", 100, -3, 3
                )
                h_bin_toys_abs_pull[i].SetDirectory(self.m_output)
                func_abs[i] = ROOT.TF1(
                    f"Gaus_abs_{i}",
                    "gaus(0)",
                    (1 - 1.5 * rel_err) * mean,
                    (1 + 1.5 * rel_err) * mean,
                )
                func_abs_pull[i] = ROOT.TF1(f"GausPull_abs_{i}", "gaus(0)", -3, 3)
                func_abs_pull[i].SetParameter(2, 1)

                # Unfolded toy bin
                mean = h_unfolded.GetBinContent(i + 1)
                h_bin_toys_unfold[i] = ROOT.TH1D(
                    f"Unfolded_toy_bin_{i}",
                    f"Unfolded_toy_bin_{i}",
                    100,
                    (1 - 1.5 * rel_err) * mean,
                    (1 + 1.5 * rel_err) * mean,
                )
                h_bin_toys_unfold[i].SetDirectory(self.m_output)

            # Allocating lists for toys
            m_sx_abs = [0] * self.m_nbins
            m_sx_rel = [0] * self.m_nbins
            m_sxy_abs = [[0] * self.m_nbins for _ in range(self.m_nbins)]
            m_sxy_rel = [[0] * self.m_nbins for _ in range(self.m_nbins)]
            v_toys_abs = [[] for _ in range(self.m_nbins)]
            v_toys_rel = [[] for _ in range(self.m_nbins)]

            for i in range(self.m_nbins):
                m_sx_abs[i] = 0
                m_sx_rel[i] = 0
                m_sxy_abs[i] = [0] * self.m_nbins
                m_sxy_rel[i] = [0] * self.m_nbins
                for j in range(self.m_nbins):
                    m_sxy_abs[i][j] = 0
                    m_sxy_rel[i][j] = 0
                v_toys_abs[i] = [0] * self.nToys
                v_toys_rel[i] = [0] * self.nToys

            ROOT.gDirectory.cd()

            # Initialize smearing histograms
            h_bkg_smeared = self.h_background.Clone()
            h_response_smeared = self.h_response.Clone()
            h_generated_smeared = self.h_generated.Clone()
            h_signal_reco_smeared = self.h_signal_reco.Clone()

            h_bkg_smeared.SetDirectory(0)
            h_response_smeared.SetDirectory(0)
            h_generated_smeared.SetDirectory(0)
            h_signal_reco_smeared.SetDirectory(0)

            h_acceptance_smeared = h_response_smeared.ProjectionX(
                "h_acceptanceSmeared", 1, self.m_nbins
            )
            h_acceptance_smeared.Divide(h_signal_reco_smeared)
            h_acceptance_smeared.SetDirectory(0)

            h_signal_truth_smeared = h_response_smeared.ProjectionY(
                "h_signalTruthSmeared", 1, self.m_nbins
            )
            h_signal_truth_smeared.SetDirectory(0)

            h_efficiency_smeared = h_signal_truth_smeared.Clone("h_efficiencySmeared")
            h_efficiency_smeared.SetDirectory(0)
            h_efficiency_smeared.Divide(h_generated_smeared)

            # Add smearing
            log.info("Running on {} toys...".format(self.nToys))
            for i in range(0, self.nToys):
                self.unfolder.reset()

                # Data smearing
                h_data_smeared = self.h_data.Clone()
                h_data_smeared.SetDirectory(0)
                h_data_smeared.SetName(f"data_{i}")
                run_toy(h_data_smeared, self.m_toy_type)
                h_data_smeared_corrected = h_data_smeared.Clone()
                h_data_smeared_corrected.SetDirectory(0)
                h_data_smeared_corrected.SetName(f"data_corrected_{i}")

                # Unfolder settings
                self.unfolder.set_reco_histogram(h_signal_reco_smeared)
                self.unfolder.set_truth_histogram(h_signal_truth_smeared)
                self.unfolder.set_generated_histogram(h_generated_smeared)
                self.unfolder.set_response_histogram(h_response_smeared)
                if self.ignore_background == False:
                    h_data_smeared_corrected.Add(h_bkg_smeared, -1)
                h_data_smeared_corrected.Multiply(h_acceptance_smeared)

                # Unfold again
                self.unfolder.set_data_histogram(h_data_smeared_corrected)
                self.unfolder.do_unfold()
                h_absXs_smeared = self.unfolder.h_unfolded.Clone()
                h_absXs_smeared.SetDirectory(0)
                h_absXs_smeared.Divide(h_efficiency_smeared)
                h_absXs_smeared.Scale(1.0 / self.lumi)
                integratedXs_smeared = h_absXs_smeared.Integral()
                h_relXs_smeared.SetDirectory(0)
                h_relXs_smeared.Scale(1.0 / integratedXs_smeared)
                h_unfolded = self.unfolder.h_unfolded.Clone()
                divide_by_bin_width(h_relXs_smeared)
                divide_by_bin_width(h_absXs_smeared)

                for b in range(0, self.m_nbins):
                    value_abs, value_rel, value_data, value_unfold = (
                        h_relXs_smeared.GetBinContent(b + 1),
                        h_absXs_smeared.GetBinContent(b + 1),
                        h_data_smeared.GetBinContent(b + 1),
                        h_unfolded.GetBinContent(b + 1),
                    )

                    h_bin_toys_rel[b].Fill(value_rel)
                    v_branch_rel[b] = value_rel
                    v_toys_rel[b][i] = value_rel
                    m_sx_rel[b] += value_rel

                    h_bin_toys_abs[b].Fill(value_abs)
                    v_branch_abs[b] = value_abs
                    v_toys_abs[b][i] = value_abs
                    m_sx_abs[b] += value_abs

                    h_bin_toys_data[b].Fill(value_data)
                    h_bin_toys_unfold[b].Fill(value_unfold)

                    for j in range(0, b + 1):
                        value_rel_2 = h_relXs_smeared.GetBinContent(j + 1)
                        m_sxy_rel[b][j] += value_rel * value_rel_2
                        value_abs_2 = h_absXs_smeared.GetBinContent(j + 1)
                        m_sxy_abs[b][j] += value_abs * value_abs_2

            log.info("Setting stat errors and fitting pulls...")

    def save(self):
        pass
