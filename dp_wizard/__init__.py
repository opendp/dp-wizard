"""DP Wizard makes it easier to get started with Differential Privacy."""

from pathlib import Path


__version__ = (Path(__file__).parent / "VERSION").read_text().strip()


class AnalysisType:
    HISTOGRAM = "Histogram"
    MEAN = "Mean"


def main():  # pragma: no cover
    import shiny
    from dp_wizard.utils.argparse_helpers import get_cli_info

    # We only call this here so "--help" is handled,
    # and to validate inputs before starting the server.
    get_cli_info()

    shiny.run_app(
        app="dp_wizard.app",
        launch_browser=True,
        reload=True,
    )
