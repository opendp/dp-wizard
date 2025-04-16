#!/usr/bin/env python3
# This is probably reinventing the wheel.
# I'm happy with flit and pip-compile separately,
# but by design they are both simple tools that do one job.
# TODO: See if pip-tools or poetry can handle this?

from pathlib import Path
from subprocess import check_call

from tomlkit import dumps, parse


def echo_check_call(cmd):
    print(f"Running: {cmd}")
    # Usually avoid "shell=True",
    # but using it here so we can quote the sed expression.
    check_call(cmd, shell=True)


def pip_compile_install(file_name):
    echo_check_call(f"pip-compile --rebuild {file_name}")
    txt_file_name = file_name.replace(".in", ".txt")
    echo_check_call(f"pip install -r {txt_file_name}")
    echo_check_call(f"sed -i -e 's:/.*/dp-wizard/:.../dp-wizard/:' {txt_file_name}")


def parse_requirements(file_name):
    requirements_path = Path(__file__).parent / file_name
    lines = requirements_path.read_text().splitlines()
    return sorted(line for line in lines if line and not line.strip().startswith("#"))


def rewrite_pyproject_toml():
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    pyproject = parse(pyproject_path.read_text())
    # TODO: Can we split it to have one dependency per line?
    # https://tomlkit.readthedocs.io/en/latest/api/#tomlkit.items.Array
    pyproject["project"]["dependencies"] = parse_requirements(
        "requirements-app.in",
    )
    pyproject["project"]["optional-dependencies"]["app"] = parse_requirements(
        "requirements-app.txt",
    )
    pyproject_path.write_text(dumps(pyproject))


def main():
    pip_compile_install("requirements-app.in")
    pip_compile_install("requirements-dev.in")
    rewrite_pyproject_toml()


if __name__ == "__main__":
    main()
