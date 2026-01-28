import argparse
from sys import argv
from typing import NamedTuple

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


_default_host = "127.0.0.1"
_default_port = 8000


def _get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="DP Wizard makes it easier to get started with "
        "Differential Privacy.",
        epilog=f"""
Unless you have set "--sample" or "--cloud", you will specify a CSV
inside the application.

Provide a "Private CSV" {PRIVATE_TEXT}

Provide a "Public CSV" {PUBLIC_TEXT}

Provide both {PUBLIC_PRIVATE_TEXT}
""",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--sample",
        action="store_true",
        help="Generate a sample CSV: "
        "See how DP Wizard works without providing your own data",
    )
    group.add_argument(
        "--cloud",
        action="store_true",
        help="Prompt for column names instead of CSV upload",
    )

    parser.add_argument(
        "--host",
        default=_default_host,
        help="Bind socket to this host",
    )
    parser.add_argument(
        "--port",
        default=_default_port,
        help="Bind socket to this port. If 0, a random port will be used.",
    )
    parser.add_argument(
        "--no_browser",
        action="store_true",
        help="By default, a browser is started; Enable this for no browser.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable to watch source directory and reload on changes.",
    )
    return parser


def _get_args() -> argparse.Namespace:
    """
    >>> _get_args()
    Namespace(sample=False, cloud=False)
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
    is_sample_csv: bool
    is_cloud_mode: bool
    is_qa_mode: bool
    host: str
    port: int
    launch_browser: bool
    reload: bool

    def get_is_tutorial_mode(self) -> bool:
        return self.is_sample_csv or self.is_cloud_mode  # pragma: no cover


def cli_info_defaults(
    is_sample_csv: bool,
    is_cloud_mode: bool,
    is_qa_mode: bool,
) -> CLIInfo:
    return CLIInfo(
        is_sample_csv=is_sample_csv,
        is_cloud_mode=is_cloud_mode,
        is_qa_mode=is_qa_mode,
        host=_default_host,
        port=_default_port,
        launch_browser=False,
        reload=False,
    )


def get_cli_info() -> CLIInfo:  # pragma: no cover
    args = _get_args()
    return CLIInfo(
        is_sample_csv=args.sample,
        is_cloud_mode=args.cloud,
        is_qa_mode=False,
        host=args.host,
        port=args.port,
        launch_browser=not args.no_browser,
        reload=args.reload,
    )
