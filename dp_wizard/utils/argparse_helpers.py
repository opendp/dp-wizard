from sys import argv
from pathlib import Path
import argparse
from typing import NamedTuple


def _existing_csv_type(arg: str) -> Path:
    path = Path(arg)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"No such file: {arg}")
    if path.suffix != ".csv":
        raise argparse.ArgumentTypeError(f'Must have ".csv" extension: {arg}')
    return path


PUBLIC_TEXT = """if you have a public data set, and are curious how
DP can be applied: The preview visualizations will use your public data."""
PRIVATE_TEXT = """if you only have a private data set, and want to
make a release from it: The preview visualizations will only use
simulated data, and apart from the headers, the private CSV is not
read until the release."""
PUBLIC_PRIVATE_TEXT = """if you have two CSVs with the same structure.
Perhaps the public CSV is older and no longer sensitive. Preview
visualizations will be made with the public data, but the release will
be made with private data."""


def _get_arg_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="DP Wizard makes it easier to get started with "
        "Differential Privacy.",
        epilog=f"""
Unless you have set "--demo" or "--cloud", you will specify a CSV
inside the application.

Provide a "Private CSV" {PRIVATE_TEXT}

Provide a "Public CSV" {PUBLIC_TEXT}

Provide both {PUBLIC_PRIVATE_TEXT}
""",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--demo",
        action="store_true",
        help="Use generated fake CSV for a quick demo",
    )
    group.add_argument(
        "--cloud",
        action="store_true",
        help="Prompt for column names instead of CSV upload",
    )
    return parser


def _get_args():
    """
    >>> _get_args()
    Namespace(demo=False, cloud=False)
    """
    arg_parser = _get_arg_parser()

    if "pytest" in argv[0] or ("shiny" in argv[0] and "run" == argv[1]):
        # We are running a test,
        # and ARGV is polluted, so override:
        args = arg_parser.parse_args([])  # pragma: no cover
    else:
        # Normal parsing:
        args = arg_parser.parse_args()  # pragma: no cover

    return args


class CLIInfo(NamedTuple):
    is_demo: bool
    in_cloud: bool
    qa_mode: bool


def get_cli_info() -> CLIInfo:  # pragma: no cover
    args = _get_args()
    return CLIInfo(is_demo=args.demo, in_cloud=args.cloud, qa_mode=False)
