"""DP Creator II makes it easier to get started with Differential Privacy."""

import shiny
from dp_creator_ii.argparse_helpers import get_csv_contrib


__version__ = "0.0.1"


def main():  # pragma: no cover
    # We only call this here so "--help" is handled,
    # and to validate inputs before starting the server.
    get_csv_contrib()

    shiny.run_app(
        app="dp_creator_ii.app",
        launch_browser=True,
        reload=True,
    )
