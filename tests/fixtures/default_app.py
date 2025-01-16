from shiny import App

from dp_wizard.app import app_ui, make_server_from_cli_info
from dp_wizard.utils.argparse_helpers import CLIInfo

app = App(
    app_ui,
    make_server_from_cli_info(
        CLIInfo(
            public_csv_path=None,
            private_csv_path=None,
            contributions=1,
            is_demo=False,
        )
    ),
)
