from pathlib import Path
from argparse import ArgumentTypeError
import re

import pytest

from dp_wizard.utils.argparse_helpers import _get_arg_parser, _existing_csv_type


fixtures_path = Path(__file__).parent.parent / "fixtures"


def extract_block(md):
    '''
    >>> fake_md = """
    ... header
    ... ```
    ... block
    ... ```
    ... footer
    ... """
    >>> extract_block(fake_md)
    'block'

    >>> extract_block('sorry')
    Traceback (most recent call last):
    ...
    Exception: no match for block
    '''
    match = re.search(r"```\n(.*?)\n```", md, flags=re.DOTALL)
    if match:
        return match.group(1)
    raise Exception("no match for block")


def test_help():
    help = re.sub(
        # line wrapping of params varies:
        r"\]\s+\[",
        "] [",
        _get_arg_parser().format_help(),
    )
    help = re.sub(
        # argparse inserts info from the running process:
        r"usage: (-c|__main__\.py|pytest)",
        "usage: dp-wizard",
        help,
    )
    help = help.strip()

    root_path = Path(__file__).parent.parent.parent

    readme_md = (root_path / "README.md").read_text()
    assert help == extract_block(readme_md)

    readme_pypi_md = (root_path / "README-PYPI.md").read_text()
    assert help == extract_block(readme_pypi_md)


def test_arg_validation_no_file():
    with pytest.raises(ArgumentTypeError, match="No such file: no-such-file"):
        _existing_csv_type("no-such-file")


def test_arg_validation_not_csv():
    with pytest.raises(ArgumentTypeError, match='Must have ".csv" extension:'):
        _existing_csv_type(str(fixtures_path / "fake.ipynb"))


def test_arg_validation_works():
    path = _existing_csv_type(str(fixtures_path / "fake.csv"))
    assert path.name == "fake.csv"
