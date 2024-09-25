from pathlib import Path

import dp_creator_ii


def test_help():
    help = (
        dp_creator_ii.get_parser()
        .format_help()
        # argparse doesn't actually know the name of the script
        # and inserts the name of the running program instead.
        .replace("__main__.py", "dp-creator-ii")
        .replace("pytest", "dp-creator-ii")
        # Text is different under Python 3.9:
        .replace("optional arguments:", "options:")
    )
    print(help)

    readme_md = (Path(__file__).parent.parent.parent / "README.md").read_text()
    assert help in readme_md
