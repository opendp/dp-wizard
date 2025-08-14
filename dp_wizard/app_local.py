from shiny import App

from dp_wizard.shiny import make_app_ui_from_cli_info, make_server_from_cli_info
from dp_wizard.utils.argparse_helpers import get_cli_info

cli_info = get_cli_info()

app = App(
    make_app_ui_from_cli_info(cli_info),
    make_server_from_cli_info(cli_info),
)
