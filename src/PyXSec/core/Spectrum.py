# ---------------------- Metadata ----------------------
#
# File name:  Spectrum.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-06
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# STD modules
import xml.etree.ElementTree as et
import sys

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

        # Histograms
        self.h_data = None
        self.h_signal_reco = None
        self.h_response = None
        self.h_generated = None
        self.h_background = None
        self.h_data_minus_bkg = None

        # Other
        self.m_output = None
        self.unfolder = None

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
            "Unfolding using \x1b[38;5;171m{0}\x1b[0m method with unfolding parameter set to \x1b[38;5;171m{1}\x1b[0m and running on \x1b[38;5;171m{2}\x1b[0m toys".format(
                self.method, self.unfolding_parameter, self.nToys
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
            self.h_background.Reset()  # dummy
            self.h_background.SetDirectory(0)

    def _initialize(self):
        """
        Initialize histograms loaded with _load_histograms() method and the Unfolder interface.
        """

        # Initial settings
        log.info("Initializing loaded histograms")
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
        staterr_arr = self.staterr.split(":")
        if len(staterr_arr) == 1 and staterr_arr[0] == "analytical":
            self.unfolder = Unfolder(self.method, "kCovToy", self.unfolding_parameter)
            self.unfolder.SetNToys(self.nToys)
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

    def compute_differential_cross_sections(self):
        pass

    def save(self):
        pass
