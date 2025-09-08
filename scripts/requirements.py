#!/usr/bin/env python3
# This is probably reinventing the wheel.
# I'm happy with flit and pip-compile separately,
# but by design they are both simple tools that do one job.
# TODO: See if pip-tools or poetry can handle this?

from os import chdir
from pathlib import Path
from subprocess import check_call

from tomlkit import array, dumps, parse


def echo_check_call(cmd):
    """
    >>> echo_check_call("echo 'Hello!'")
    Running: echo 'Hello!'
    >>> echo_check_call("intended-failure")
    Traceback (most recent call last):
    ...
    subprocess.CalledProcessError: Command 'intended-failure' returned non-zero exit status 127.
    """  # noqa: B950 (line too long)
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


def parse_requirements(file_name):
    """
    >>> print(parse_requirements("requirements.txt"))
    [...opendp...]
    """
    cwd_root()
    lines = Path(file_name).read_text().splitlines()
    return sorted(line for line in lines if line and not line.strip().startswith("#"))


def to_toml_array(file_name):
    """
    Just given a list, the TOML array is a single line,
    which makes the diff hard to read.
    This will format the array with one entry per line.

    >>> print(dumps(to_toml_array("requirements.txt")))
    [
    ...
        "opendp[...]==...",
    ...
    ]
    """
    toml_array = array()
    for dependency in parse_requirements(file_name):
        toml_array.add_line(dependency)
    toml_array.add_line(indent="")
    return toml_array


def get_new_pyproject_toml():
    """
    >>> print(get_new_pyproject_toml())
    [build-system]
    ...
    [project]
    ...
    """
    cwd_root()
    pyproject = parse(Path("pyproject.toml").read_text())
    pyproject["project"]["dependencies"] = to_toml_array("requirements.in")
    pyproject["project"]["optional-dependencies"]["app"] = to_toml_array(
        "requirements.txt"
    )
    return dumps(pyproject)


def rewrite_pyproject_toml():  # pragma: no cover
    cwd_root()
    Path("pyproject.toml").write_text(get_new_pyproject_toml())


def cwd_root():
    chdir(Path(__file__).parent.parent)


def main():  # pragma: no cover
    pip_compile_install("requirements.in")
    pip_compile_install("requirements-dev.in")
    rewrite_pyproject_toml()


if __name__ == "__main__":  # pragma: no cover
    main()
