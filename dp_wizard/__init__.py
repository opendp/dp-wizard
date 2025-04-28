"""DP Wizard makes it easier to get started with Differential Privacy."""

from pathlib import Path
from logging import warning


__version__ = (Path(__file__).parent / "VERSION").read_text().strip()


def main():  # pragma: no cover
    import sys

    min_version = "3.10"
    if sys.version_info < tuple(int(v) for v in min_version.split(".")):
        raise Exception(
            f"DP Wizard requires Python {min_version}"
            f" or newer. This is Python {sys.version}."
        )

    import shiny
    from dp_wizard.utils.argparse_helpers import get_cli_info

    # We only call this here so "--help" is handled,
    # and to validate inputs before starting the server.
    get_cli_info()

    not_first_run_path = Path(__file__).parent / "tmp/not-first-run.txt"
    if not not_first_run_path.exists():
        warning("┌──────────────────────────────────┐")
        warning("│ First startup may take a minute! │")
        warning("│ Successive runs will be faster.  │")
        warning("└──────────────────────────────────┘")
        not_first_run_path.touch()

    shiny.run_app(
        app="dp_wizard.app_local",
        launch_browser=True,
        reload=True,
    )
