# Symlinked at top level of repo to follow posit connect launch conventions.
from dp_wizard.shiny import make_app
from dp_wizard.utils.argparse_helpers import get_cli_info

app = make_app(get_cli_info())
