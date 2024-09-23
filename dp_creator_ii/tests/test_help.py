from pathlib import Path

import dp_creator_ii


def test_help():
    help = dp_creator_ii.get_parser().format_help()
    # Text is a little different under Python 3.9:
    help = help.replace('optional arguments:', 'options:')
    print(help)

    readme_md = (Path(__file__).parent.parent.parent / 'README.md').read_text()
    assert help in readme_md