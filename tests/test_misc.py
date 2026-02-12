import re
import subprocess
from pathlib import Path

import pytest

from dp_wizard import __version__, opendp_version, package_root

tests = {
    "flake8 linting": "flake8 . --count --show-source --statistics",
    "pyright type checking": "pyright",
    "precommit checks": "pre-commit run --all-files",
    # pandoc invocation aligned with scripts/slides.sh:
    "pandoc slides up to date": (
        "pandoc --to=slidy "
        "--include-before-body=docs/include-before-body.html "
        "docs/index.md "
        "--output docs/index-test.html "
        "--standalone "
        "&& diff docs/index.html docs/index-test.html"
    ),
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


def get_file_paths() -> list[Path]:
    # TODO: Is there a package that respects .gitignore?
    top_level_paths = [
        path
        for path in package_root.parent.iterdir()
        if not (
            path.match("*venv*")
            or path.name
            in [
                "docs",
                ".git",
                ".DS_Store",
                "dist",
                ".coverage",
                ".hypothesis",
                ".gitignore",
                ".pytest_cache",
            ]
        )
    ]
    file_paths = []
    for path in top_level_paths:
        if path.is_file():
            file_paths.append(path)
        else:
            file_paths += [
                path
                for path in path.glob("**/*")
                if path.is_file()
                and not (
                    path.match("*.pyc")
                    or path.name
                    in ["__pycache__", ".DS_Store", "favicon.ico", Path(__file__).name]
                )
            ]
    return file_paths


def test_common_typos():
    expected_pairs = [
        (r"github(?!\.com)(?!\.io)(?!/workflows)", ["GitHub"]),
        (r"dp.wizard\[[^]]+\]", ["dp_wizard[pins]"]),
        (r"pip install --editable \S+", ["pip install --editable '.[pins]'"]),
        (
            r"pip install \S+",
            [
                "pip install 'dp_wizard[pins]'",
                "pip install 'dp_wizard[pins]';",
                "pip install 'dp_wizard[pins]'`",
                "pip install DEPENDENCIES",
                "pip install -r",
                "pip install --editable",
                "pip install flit",
                "pip install pytest",  # In test fixtures
                'pip install pytest"',
            ],
        ),
    ]
    failures = []
    for path in get_file_paths():
        rel_path = path.relative_to(package_root.parent)
        try:
            text = path.read_text()
        except Exception as e:
            pytest.fail(f"Exception reading {path}: {e}")
        for pattern, expected in expected_pairs:
            for match in re.findall(rf"(.*)({pattern})(.*)", text):
                if match[1] not in expected:
                    options = " or ".join(f'"{e}"' for e in expected)
                    failures.append(
                        f"Expected {options} in {rel_path}, not:"
                        f"\n> {''.join(match)}"
                    )
    if failures:
        pytest.fail("\n".join(failures))
