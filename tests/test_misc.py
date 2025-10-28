import re
import subprocess

import pytest

from dp_wizard import __version__, opendp_version, package_root

tests = {
    "flake8 linting": "flake8 . --count --show-source --statistics",
    "pyright type checking": "pyright",
    "precommit checks": "pre-commit run --all-files",
}


@pytest.mark.parametrize("cmd", tests.values(), ids=tests.keys())
def test_subprocess(cmd: str):
    result = subprocess.run(cmd, shell=True)
    assert result.returncode == 0, f'"{cmd}" failed'


def test_version():
    assert re.match(r"\d+\.\d+\.\d+", __version__)


@pytest.mark.parametrize(
    "rel_path",
    [
        "pyproject.toml",
        "requirements-dev.txt",
    ],
)
def test_opendp_pin(rel_path):
    opendp_lines = [
        line
        for line in (package_root.parent / rel_path).read_text().splitlines()
        if "opendp[" in line
    ]
    assert all([f"opendp[mbi]=={opendp_version}" in line for line in opendp_lines])


@pytest.mark.parametrize(
    "rel_path",
    [
        "dp_wizard/__init__.py",
        "README.md",
        "README-PYPI.md",
        ".github/workflows/test.yml",
        "pyproject.toml",
    ],
)
def test_python_min_version(rel_path):
    text = (package_root.parent / rel_path).read_text()
    assert "3.10" in text
    if "README" in rel_path:
        # Make sure we haven't upgraded one reference by mistake.
        assert not re.search(r"3.1[^0]", text)
