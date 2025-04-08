import subprocess
import pytest
from pathlib import Path
import re
import dp_wizard


root_path = Path(__file__).parent.parent


tests = {
    "flake8 linting": "flake8 . --count --show-source --statistics",
    "pyright type checking": "pyright",
}


@pytest.mark.parametrize("cmd", tests.values(), ids=tests.keys())
def test_subprocess(cmd: str):
    result = subprocess.run(cmd, shell=True)
    assert result.returncode == 0, f'"{cmd}" failed'


def test_version():
    assert re.match(r"\d+\.\d+\.\d+", dp_wizard.__version__)


@pytest.mark.parametrize(
    "rel_path",
    [
        "pyproject.toml",
        "requirements-dev.in",
        "requirements-dev.txt",
        "dp_wizard/utils/code_generators/abstract_generator.py",
    ],
)
def test_opendp_pin(rel_path):
    opendp_lines = [
        line
        for line in (root_path / rel_path).read_text().splitlines()
        if "opendp[" in line
    ]
    assert len(opendp_lines) == 1
    assert "opendp[polars]==0.12.1a20250227001" in opendp_lines[0]


@pytest.mark.parametrize(
    "rel_path",
    [
        "README.md",
        "README-PYPI.md",
        ".github/workflows/test.yml",
    ],
)
def test_python_min_version(rel_path):
    text = (root_path / rel_path).read_text()
    assert "3.10" in text
    if "README" in rel_path:
        # Make sure we haven't upgraded one reference by mistake.
        assert not re.search(r"3.1[^0]", text)


def test_dependency_lower_bounds():
    pyproject = set(
        line.replace('"', "").replace(",", "").strip()
        for line in (root_path / "pyproject.toml").read_text().splitlines()
        if ">=" in line and "flit_core" not in line
    )
    requirements = set(
        line
        for line in (root_path / "requirements-dev.in").read_text().splitlines()
        if ">=" in line
    )
    assert len(requirements) > 0
    assert pyproject == requirements
