from pathlib import Path
from tomlkit import dumps, parse, table


def parse_requirements(file_name):
    requirements_path = Path(__file__).parent / file_name
    lines = requirements_path.read_text().splitlines()
    return [line for line in lines if line and not line.strip().startswith("#")]


def rewrite_pyproject_toml():
    pyproject = parse((Path(__file__).parent / "pyproject.toml").read_text())
    pyproject["project"]["dependencies"] = parse_requirements("requirements-app.in")
    pyproject["project"]["optional-dependencies"]["app"] = parse_requirements(
        "requirements-app.txt"
    )
    print(dumps(pyproject))


def main():
    rewrite_pyproject_toml()


if __name__ == "__main__":
    main()
