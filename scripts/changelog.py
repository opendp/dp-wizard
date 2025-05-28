#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path


root_path = Path(__file__).parent.parent


def get_prev_version():
    """
    >>> len(get_prev_version().splitlines())
    1
    """
    return (root_path / "dp_wizard" / "VERSION").read_text().strip()


def log_until(match):  # pragma: no cover
    lines = subprocess.check_output(["git", "log", "--oneline"], text=True).splitlines()
    if match is None:
        return lines
    head = []
    for line in lines:
        if match in line:
            break
        head.append(line)
    return head


def parse_log(lines):
    """
    >>> print(parse_log([
    ...     'abcd0000 bar! (#2)',
    ...     'abcd0001 foo? (#1)',
    ... ]))
    - bar! [#2](https://github.com/opendp/dp-wizard/pull/2)
    - foo? [#1](https://github.com/opendp/dp-wizard/pull/1)
    """
    output_lines = []
    for line in lines:
        line = re.sub(r"^\w+\s+", "", line)  # Remove hash
        line = re.sub(r"^\([^)]+\)\s+", "", line)  # Remove tag
        line = re.sub(
            r"\(#(\d+)\)", r"[#\1](https://github.com/opendp/dp-wizard/pull/\1)", line
        )
        output_lines.append(f"- {line}")
    return "\n".join(output_lines)


def main():  # pragma: no cover
    old_changelog_lines = (root_path / "CHANGELOG.md").read_text().splitlines()
    new_changelog_lines = []

    prev_version = get_prev_version()
    log_lines = log_until(prev_version)
    changelog_update = parse_log(log_lines)

    for line in old_changelog_lines:
        if prev_version in line:
            new_changelog_lines.append(changelog_update)
            new_changelog_lines.append("")
        new_changelog_lines.append(line)

    (root_path / "CHANGELOG.md").write_text("\n".join(new_changelog_lines))


if __name__ == "__main__":  # pragma: no cover
    main()
