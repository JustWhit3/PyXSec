# ---------------------- Metadata ----------------------
#
# File name:  Spectrum.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-06
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# STD modules
import xml.etree.ElementTree as et

# Data science modules
import ROOT as r

# Personal modules
from utils import get_custom_logger

# Logger settings
log = get_custom_logger(__name__)


class Spectrum:
    """
    Class used to construct a spectrum object to unfold input data.
    """

    def __init__(self, config):
        """
        Constructor of the Spectrum class. Parse input data and create histograms.

        Args:
            config (str): XML configuration file.
        """

        # Initialize variables
        self.config = config
        self.ignore_background = False
        self.use_default_regularization = False

        # Initialize histograms
        self.h_data = r.TH1D()

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
        try_parse = (
            lambda elem: root.find(elem).attrib if root.find(elem) is not None else {}
        )
        self.br = float(try_parse("br")["value"])
        self.lumi = float(try_parse("lumi")["value"])

        # Read file paths
        self.input_sig_path = try_parse("sig")["file"]
        self.input_data_path = try_parse("data")["file"]
        self.input_res_path = try_parse("res")["file"]
        self.input_gen_path = try_parse("gen")["file"]

        # Read background information
        self.input_bkg_path = try_parse("bkg")["file"]
        self.input_bkg_histo = try_parse("bkg")["hpath"]
        if self.input_bkg_path == "" or self.input_bkg_histo == "":
            log.warning(
                "Background path or histogram is empty, we will not subtract the background"
            )
            self.ignore_background = True
        else:
            log.info("Background path: {}".format(self.bkg_path))

        # Read histogram paths
        self.histo_reco_path = try_parse("sig")["hpath"]
        self.histo_data_path = try_parse("data")["hpath"]
        self.histo_res_path = try_parse("res")["hpath"]
        self.histo_gen_path = try_parse("gen")["hpath"]

        # Read unfolding information
        self.method = try_parse("unfolding")["method"]
        self.unfolding_parameter = int(try_parse("unfolding")["regularization"])
        if self.unfolding_parameter < 0:
            self.use_default_regularization = True
        self.nToys = int(try_parse("unfolding")["ntoys"])

        # Print unfolding information
        log.info(
            "Unfolding using \x1b[38;5;171m{0}\x1b[0m method with unfolding parameter set to \x1b[38;5;171m{1}\x1b[0m and running on \x1b[38;5;171m{2}\x1b[0m toys".format(
                self.method, self.unfolding_parameter, self.nToys
            )
        )
        log.info(
            "Using \x1b[38;5;171m{0}\x1b[0m branching ratio and \x1b[38;5;171m{1}\x1b[0m fb^-1 integrated luminosity".format(
                self.br, self.lumi
            )
        )

    def _load_histograms(self):
        log.info("Opening data file: {}".format(self.input_data_path))

    def _initialize(self):
        pass

    def compute_differential_cross_sections(self):
        pass

        # if self.unfolding_parameter < 0:
        #    if self.method == "Bayes":
        #        self.unfolding_parameter = 4
        #    elif self.method == "SVD":
        #        self.unfolding_parameter = self.h_data.GetNbinsX() / 2
        #        if self.unfolding_parameter < 2:
        #            self.unfolding_parameter = 2

    def save(self, output):
        pass
