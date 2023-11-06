# ---------------------- Metadata ----------------------
#
# File name:  Spectrum.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-06
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

import xml.etree.ElementTree as ET


class Spectrum:
    def __init__(self, config):

        # Initialize variables
        self.config = config

        # Prepare inputs
        self._configure()
        self._load_histograms()
        self._initialize()

    def _configure(self):

        # Initialize XML parser
        tree = ET.parse(self.config)
        root = tree.getroot()

        # Read information from config
        try_parse = (
            lambda elem: root.find(elem).attrib if root.find(elem) is not None else {}
        )
        self.br = try_parse("br")["value"]
        self.lumi = try_parse("lumi")["value"]
        
        self.sig_path = try_parse("sig")["file"]
        self.data_path = try_parse("data")["file"]
        self.res_path = try_parse("res")["file"]
        self.gen_path = try_parse("gen")["file"]

    def _load_histograms(self):
        pass

    def _initialize(self):
        pass

    def compute_differential_cross_sections(self):
        pass

    def save(self, output):
        pass
