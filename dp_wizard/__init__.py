"""DP Wizard makes it easier to get started with Differential Privacy."""

import os
from logging import warning
from pathlib import Path

package_root = Path(__file__).parent
__version__ = (package_root / "VERSION").read_text().strip()
opendp_version = "0.14.1"
registry_url = "https://registry.opendp.org/deployments-registry/"
config_root = Path(os.path.expanduser("~")) / ".dp-wizard"
if not config_root.exists():
    config_root.mkdir()  # pragma: no cover


def get_template_root(path: str) -> Path:
    # We use the same convention everywhere,
    # but there are separate directories
    # for each of the analyses.
    return Path(path).parent / "no-tests"


def main() -> None:  # pragma: no cover
    import sys

    min_version = "3.10"
    if sys.version_info < tuple(int(v) for v in min_version.split(".")):
        raise Exception(
            f"DP Wizard requires Python {min_version}"
            f" or newer. This is Python {sys.version}."
        )

    import shiny

    from dp_wizard.utils.argparse_helpers import get_cli_info

    cli_info = get_cli_info()

    not_first_run_path = config_root / "not-first-run.txt"
    if not not_first_run_path.exists():
        warning("┌──────────────────────────────────┐")
        warning("│ First startup may take a minute! │")
        warning("│ Successive runs will be faster.  │")
        warning("└──────────────────────────────────┘")
        not_first_run_path.touch()

    shiny.run_app(
        app="dp_wizard.app",
        host=cli_info.host,
        port=cli_info.port,
        launch_browser=cli_info.launch_browser,
        reload=cli_info.reload,
    )
