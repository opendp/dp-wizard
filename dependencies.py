from pathlib import Path
from tomlkit import dumps, parse, items


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
    rewrite_pyproject_toml()


if __name__ == "__main__":
    main()
