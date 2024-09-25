"""DP Creator II makes it easier to get started with Differential Privacy."""

import os
from pathlib import Path
from argparse import ArgumentParser
import json

import shiny


__version__ = "0.0.1"


def get_parser():
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use during development for increased logging "
        "and auto-reload after code changes",
    )
    return parser


def main():  # pragma: no cover
    parser = get_parser()
    args = parser.parse_args()

    os.chdir(Path(__file__).parent)  # run_app() depends on the CWD.

    # Just setting variables in a plain python module doesn't work:
    # The new thread started for the server doesn't see changes.
    Path("config.json").write_text(
        json.dumps(
            {
                "csv_path": str(args.csv_path),
                "unit_of_privacy": args.unit_of_privacy,
            }
        )
    )

    run_app_kwargs = (
        {}
        if not args.debug
        else {
            "reload": True,
            "log_level": "debug",
        }
    )
    shiny.run_app(launch_browser=True, **run_app_kwargs)
