import re
from argparse import ArgumentTypeError
from pathlib import Path

import pytest

from dp_wizard.utils.argparse_helpers import _existing_csv_type, _get_arg_parser

fixtures_path = Path(__file__).parent.parent / "fixtures"


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

    root_path = Path(__file__).parent.parent.parent

    readme_pypi_md = norm_ws((root_path / "README-PYPI.md").read_text())
    assert help in readme_pypi_md, "--help content not in README-PYPI.md"

    readme_md = norm_ws((root_path / "README.md").read_text())
    assert readme_pypi_md in readme_md, "README-PYPI.md content not in README.md"


def test_arg_validation_no_file():
    with pytest.raises(ArgumentTypeError, match="No such file: no-such-file"):
        _existing_csv_type("no-such-file")


def test_arg_validation_not_csv():
    with pytest.raises(ArgumentTypeError, match='Must have ".csv" extension:'):
        _existing_csv_type(str(fixtures_path / "fake.ipynb"))


def test_arg_validation_works():
    path = _existing_csv_type(str(fixtures_path / "fake.csv"))
    assert path.name == "fake.csv"
