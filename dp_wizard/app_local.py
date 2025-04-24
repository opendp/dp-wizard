from shiny import App

from dp_wizard.shiny import app_ui, make_server_from_cli_info
from dp_wizard.utils.argparse_helpers import get_cli_info


app = App(
    app_ui,
    make_server_from_cli_info(get_cli_info()),
)
