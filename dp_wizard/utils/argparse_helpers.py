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
Unless you have set "--demo" or "--no_uploads", you will specify a CSV
inside the application.

Provide a "Public CSV" {PUBLIC_TEXT}

Provide a "Private CSV" {PRIVATE_TEXT}

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
        "--no_uploads",
        action="store_true",
        help="Prompt for column names instead of CSV upload",
    )
    return parser


def _get_args():
    """
    >>> _get_args()
    Namespace(demo=False, no_uploads=False)
    """
    arg_parser = _get_arg_parser()

    if "pytest" in argv[0] or ("shiny" in argv[0] and "run" == argv[1]):
        # We are running a test,
        # and ARGV is polluted, so override:
        args = arg_parser.parse_args([])  # pragma: no cover
    else:
        # Normal parsing:
        args = arg_parser.parse_args()  # pragma: no cover

    if args.demo:  # pragma: no cover
        other_args = {arg for arg in dir(args) if not arg.startswith("_")} - {
            "demo",
            "contributions",
            "no_uploads",
        }
        set_args = [k for k in other_args if getattr(args, k) is not None]
        if set_args:
            arg_parser.error(
                "When --demo is set, other arguments should be skipped: "
                + ", ".join(set_args)
            )
    return args


class CLIInfo(NamedTuple):
    is_demo: bool
    no_uploads: bool


def get_cli_info() -> CLIInfo:  # pragma: no cover
    args = _get_args()
    return CLIInfo(
        is_demo=args.demo,
        no_uploads=args.no_uploads,
    )
