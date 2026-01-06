from dp_wizard.shiny import make_app
from dp_wizard.utils.argparse_helpers import get_cli_info

app = make_app(get_cli_info())
