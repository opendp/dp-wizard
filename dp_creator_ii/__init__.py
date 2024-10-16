"""DP Creator II makes it easier to get started with Differential Privacy."""

import shiny
from dp_creator_ii.argparse_helpers import get_args


__version__ = "0.0.1"


def main():  # pragma: no cover
    # We call parse_args() again inside the app.
    # We only call it here so "--help" is handled,
    # and to validate inputs.
    get_args()

    shiny.run_app(
        app="dp_creator_ii.app",
        launch_browser=True,
        reload=True,
    )
