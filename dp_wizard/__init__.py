"""DP Wizard makes it easier to get started with Differential Privacy."""

import shiny
from dp_wizard.utils.argparse_helpers import get_cli_info


__version__ = "0.0.1"


def main():  # pragma: no cover
    # We only call this here so "--help" is handled,
    # and to validate inputs before starting the server.
    get_cli_info()

    shiny.run_app(
        app="dp_wizard.app",
        launch_browser=True,
        reload=True,
    )
