#!/usr/bin/env python3
# This is probably reinventing the wheel.
# I'm happy with flit and pip-compile separately,
# but by design they are both simple tools that do one job.
# TODO: See if pip-tools or poetry can handle this?

from pathlib import Path
from subprocess import check_call
from os import chdir
from tomlkit import dumps, parse, array


def echo_check_call(cmd):  # pragma: no cover
    print(f"Running: {cmd}")
    # Usually avoid "shell=True",
    # but using it here so we can quote the sed expression.
    check_call(cmd, shell=True)


def pip_compile_install(file_name):  # pragma: no cover
    echo_check_call(f"pip-compile --rebuild {file_name}")
    txt_file_name = file_name.replace(".in", ".txt")
    echo_check_call(f"pip install -r {txt_file_name}")
    # Abbreviate the path so it's not showing developer-specific details.
    # sed doesn't have exactly the same options on all platforms,
    # but this is good enough for now.
    echo_check_call(f"sed -i '' 's:/.*/dp-wizard/:.../dp-wizard/:' {txt_file_name}")


def parse_requirements(file_name):  # pragma: no cover
    lines = Path(file_name).read_text().splitlines()
    return sorted(line for line in lines if line and not line.strip().startswith("#"))


def to_toml_array(file_name):  # pragma: no cover
    """
    Just given a list, the TOML array is a single line,
    which makes the diff hard to read.
    This will format the array with one entry per line
    """
    toml_array = array()
    for dependency in parse_requirements(file_name):
        toml_array.add_line(dependency)
    toml_array.add_line(indent="")
    return toml_array


def rewrite_pyproject_toml():  # pragma: no cover
    pyproject_path = Path("pyproject.toml")
    pyproject = parse(pyproject_path.read_text())
    pyproject["project"]["dependencies"] = to_toml_array("requirements.in")
    pyproject["project"]["optional-dependencies"]["app"] = to_toml_array(
        "requirements.txt"
    )
    pyproject_path.write_text(dumps(pyproject))


def main():  # pragma: no cover
    chdir(Path(__file__).parent.parent)
    pip_compile_install("requirements.in")
    pip_compile_install("requirements-dev.in")
    rewrite_pyproject_toml()


if __name__ == "__main__":  # pragma: no cover
    main()
