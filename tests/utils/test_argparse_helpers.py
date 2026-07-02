import re

from dp_wizard import package_root
from dp_wizard.utils.argparse_helpers import _get_arg_parser


def norm_ws(text):
    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def test_help():
    help = norm_ws(_get_arg_parser().format_help())
    help = re.sub(
        # argparse inserts info from the running process:
        r"usage: (-c|__main__\.py|pytest)",
        "usage: dp-wizard",
        help,
    )

    readme_md = norm_ws((package_root.parent.parent / "README.md").read_text())
    assert help in readme_md, "--help content not in README-PYPI.md"
