from pathlib import Path
from subprocess import check_call

from tomlkit import dumps, parse


def pip_compile_install(file_name):
    check_call(["pip-compile", "--rebuild", file_name])
    check_call(["pip", "install", "-r", file_name.replace(".in", ".txt")])


def parse_requirements(file_name):
    requirements_path = Path(__file__).parent / file_name
    lines = requirements_path.read_text().splitlines()
    return sorted(line for line in lines if line and not line.strip().startswith("#"))


def rewrite_pyproject_toml():
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    pyproject = parse(pyproject_path.read_text())
    # TODO: multiline format?
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
