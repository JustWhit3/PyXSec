import argparse as ap
from core.Spectrum import Spectrum


def main():
    spectrum = Spectrum(args.config, args.systematic, args.output)
    spectrum.compute_differential_cross_sections()
    spectrum.save()


if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parsing input arguments.")
    parser.add_argument(
        "-c",
        "--config",
        default="",
        help="The configuration file containing all the information about input data.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="",
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
