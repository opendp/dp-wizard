import re
from pathlib import Path
import subprocess
import pytest
import json
from dp_wizard.utils.converters import convert_py_to_nb, _strip_nb_coda


fixtures_path = Path(__file__).parent.parent / "fixtures"


def norm_nb(nb_str):
    nb_str = re.sub(r'"id": "[^"]+"', '"id": "12345678"', nb_str)
    nb_str = re.sub(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z",
        "2024-01-01T00:00:00.000000Z",
        nb_str,
    )

    nb = json.loads(nb_str)
    nb["metadata"] = {}
    for cell in nb["cells"]:
        cell["metadata"] = {}

    return json.dumps(nb, indent=1)


def test_convert_py_to_nb():
    python_str = (fixtures_path / "fake.py").read_text()
    actual_nb_str = convert_py_to_nb(python_str)
    expected_nb_str = (fixtures_path / "fake.ipynb").read_text()

    normed_actual_nb_str = norm_nb(actual_nb_str)
    normed_expected_nb_str = norm_nb(expected_nb_str)
    assert normed_actual_nb_str == normed_expected_nb_str


def test_convert_py_to_nb_execute():
    python_str = (fixtures_path / "fake.py").read_text()
    actual_nb_str = convert_py_to_nb(python_str, execute=True)
    expected_nb_str = (fixtures_path / "fake-executed.ipynb").read_text()

    normed_actual_nb_str = norm_nb(actual_nb_str)
    normed_expected_nb_str = norm_nb(expected_nb_str)
    assert normed_actual_nb_str == normed_expected_nb_str


def test_strip_nb_coda():
    # Trivial test just to get 100% branch coverage.
    nb = {"cells": []}
    assert nb == json.loads(_strip_nb_coda(json.dumps(nb)))


def test_convert_py_to_nb_error():
    python_str = "Invalid python!"
    with pytest.raises(subprocess.CalledProcessError):
        convert_py_to_nb(python_str, execute=True)
