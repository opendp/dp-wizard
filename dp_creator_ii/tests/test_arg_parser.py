from pathlib import Path
from argparse import ArgumentTypeError

import pytest

from dp_creator_ii import get_arg_parser, existing_csv


def test_help():
    help = (
        get_arg_parser()
        .format_help()
        # argparse doesn't actually know the name of the script
        # and inserts the name of the running program instead.
        .replace("__main__.py", "dp-creator-ii")
        .replace("pytest", "dp-creator-ii")
        # Text is different under Python 3.9:
        .replace("optional arguments:", "options:")
    )
    print(help)

    readme_md = (Path(__file__).parent.parent.parent / "README.md").read_text()
    assert help in readme_md


def test_arg_validation_no_file():
    with pytest.raises(ArgumentTypeError, match="No such file: no-such-file"):
        existing_csv("no-such-file")


def test_arg_validation_not_csv():
    with pytest.raises(ArgumentTypeError, match='Must have ".csv" extension:'):
        existing_csv(Path(__file__).parent / "fixtures" / "fake.ipynb")


def test_arg_validation_works():
    path = existing_csv(Path(__file__).parent / "fixtures" / "fake.csv")
    assert path.name == "fake.csv"
