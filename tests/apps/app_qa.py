from dp_wizard.shiny import make_app
from dp_wizard.utils.argparse_helpers import cli_info_defaults

app = make_app(
    cli_info_defaults(
        is_sample_csv=True,
        is_qa_mode=True,
    )
)
