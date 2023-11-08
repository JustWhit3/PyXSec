#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------- Metadata ----------------------
#
# File name:  PyXSec.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-06
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

import argparse as ap
from core.Spectrum import Spectrum


def main():
    spectrum = Spectrum(args.config, args.systematic)
    spectrum.compute_differential_cross_sections()
    spectrum.save(args.output)


if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parsing input arguments.")
    parser.add_argument(
        "-c",
        "--config",
        default="",
        help="THe configuration file containing all the information about input data.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output.root",
        help="Output file of the unfolding results.",
    )
    parser.add_argument(
        "-s",
        "--systematic",
        default="nominal",
        help="Systematic to unfold.",
    )
    args = parser.parse_args()

    main()
