"""DP Creator II makes it easier to get started with Differential Privacy."""

import os
from pathlib import Path
from argparse import ArgumentParser

import shiny


__version__ = "0.0.1"


def get_arg_parser():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        help="Path to CSV containing private data",
    )
    parser.add_argument(
        "--unit",
        dest="unit_of_privacy",
        type=int,
        help="Unit of privacy: How many rows can an individual contribute?",
    )
    return parser


def main():  # pragma: no cover
    # We call parse_args() again inside the app.
    # We only call it here so "--help" is handled.
    get_arg_parser().parse_args()

    # run_app() depends on the CWD.
    os.chdir(Path(__file__).parent)

    run_app_kwargs = {
        "reload": True,
    }
    shiny.run_app(launch_browser=True, **run_app_kwargs)
