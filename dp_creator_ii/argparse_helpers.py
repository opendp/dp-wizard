from sys import argv
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError


def _existing_csv_type(arg):
    path = Path(arg)
    if not path.exists():
        raise ArgumentTypeError(f"No such file: {arg}")
    if path.suffix != ".csv":
        raise ArgumentTypeError(f'Must have ".csv" extension: {arg}')
    return path


def _get_arg_parser():
    parser = ArgumentParser(description=__doc__)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--csv",
        dest="csv_path",
        type=_existing_csv_type,
        help="Path to CSV containing private data",
    )
    input_group.add_argument(
        "--demo", action="store_true", help="Use generated fake CSV for a quick demo"
    )
    parser.add_argument(
        "--contrib",
        dest="contributions",
        metavar="CONTRIB",
        type=int,
        default=1,
        help="How many rows can an individual contribute?",
    )
    return parser


def _get_args():  # pragma: no cover
    arg_parser = _get_arg_parser()
    if argv[1:3] == ["run", "--port"]:
        # We are running a Playwright test,
        # and ARGV is polluted, so override:
        return arg_parser.parse_args([])
    else:
        # Normal parsing:
        return arg_parser.parse_args()


def _get_demo_csv_path():  # pragma: no cover
    # TODO
    pass


def get_csv_contrib():  # pragma: no cover
    args = _get_args()
    if args.csv_path is not None:
        csv_path = args.csv_path
    elif args.demo:
        csv_path = _get_demo_csv_path()
    else:
        csv_path = None
    return (csv_path, args.contributions)
