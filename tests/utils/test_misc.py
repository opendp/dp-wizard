import subprocess
import pytest


tests = {
    "flake8 linting": "flake8 . --count --show-source --statistics",
    "mypy type checking": "mypy .",
}


@pytest.mark.parametrize("cmd", tests.values(), ids=tests.keys())
def test_subprocess(cmd):
    result = subprocess.run(cmd, shell=True)
    assert result.returncode == 0, f'"{cmd}" failed'
