"""DP Creator II makes it easier to get started with Differential Privacy."""

from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError

import shiny


__version__ = "0.0.1"


def existing_csv(arg):
    path = Path(arg)
    if not path.exists():
        raise ArgumentTypeError(f"No such file: {arg}")
    if path.suffix != ".csv":
        raise ArgumentTypeError(f'Must have ".csv" extension: {arg}')
    return path


def get_arg_parser():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=existing_csv,
        help="Path to CSV containing private data",
    )
    parser.add_argument(
        "--contrib",
        dest="contributions",
        metavar="CONTRIB",
        type=int,
        default=1,
        help="How many rows can an individual contribute?",
    )
    return parser


def main():  # pragma: no cover
    # We call parse_args() again inside the app.
    # We only call it here so "--help" is handled,
    # and to validate inputs.
    get_arg_parser().parse_args()

    shiny.run_app(
        app="dp_creator_ii.app",
        launch_browser=True,
        reload=True,
    )
