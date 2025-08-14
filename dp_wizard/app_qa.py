from shiny import App

from dp_wizard.shiny import make_app_ui_from_cli_info, make_server_from_cli_info
from dp_wizard.utils.argparse_helpers import CLIInfo

cli_info = CLIInfo(
    is_sample_csv=True,
    is_cloud_mode=False,
    is_qa_mode=True,
)

app = App(
    make_app_ui_from_cli_info(cli_info),
    make_server_from_cli_info(cli_info),
)
