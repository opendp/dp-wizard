from dp_wizard.shiny import make_app
from dp_wizard.utils.argparse_helpers import CLIInfo

app = make_app(
    CLIInfo(
        is_sample_csv=False,
        is_cloud_mode=True,
        is_qa_mode=False,
    )
)
