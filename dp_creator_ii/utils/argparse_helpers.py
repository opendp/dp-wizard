from sys import argv
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError
import csv
import random
from warnings import warn
from collections import namedtuple


def _existing_csv_type(arg):
    path = Path(arg)
    if not path.exists():
        raise ArgumentTypeError(f"No such file: {arg}")
    if path.suffix != ".csv":
        raise ArgumentTypeError(f'Must have ".csv" extension: {arg}')
    return path


def _get_arg_parser():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=_existing_csv_type,
        help="Path to CSV containing private data",
    )
    parser.add_argument(
        "--contrib",
        dest="contributions",
        metavar="CONTRIB",
        type=int,
        default=1,
        help="How many rows can an individual contribute?",
    )
    parser.add_argument(
        "--demo", action="store_true", help="Use generated fake CSV for a quick demo"
    )
    return parser


def _get_args():
    """
    >>> _get_args()
    Namespace(csv_path=None, contributions=1, demo=False)
    """
    arg_parser = _get_arg_parser()

    if "pytest" in argv[0] or ("shiny" in argv[0] and "run" == argv[1]):
        # We are running a test,
        # and ARGV is polluted, so override:
        return arg_parser.parse_args([])
    else:
        # Normal parsing:
        return arg_parser.parse_args()  # pragma: no cover


def _clip(n, lower, upper):
    """
    >>> _clip(-5, 0, 10)
    0
    >>> _clip(5, 0, 10)
    5
    >>> _clip(15, 0, 10)
    10
    """
    return max(min(n, upper), lower)


def _get_demo_csv_contrib():
    """
    >>> csv_path, contributions, is_demo = _get_demo_csv_contrib()
    >>> with open(csv_path, newline="") as csv_handle:
    ...     reader = csv.DictReader(csv_handle)
    ...     reader.fieldnames
    ...     rows = list(reader)
    ...     rows[0]
    ...     rows[-1]
    ['student_id', 'class_year', 'hw_number', 'grade']
    {'student_id': '1', 'class_year': '2', 'hw_number': '1', 'grade': '73'}
    {'student_id': '100', 'class_year': '1', 'hw_number': '10', 'grade': '78'}
    """
    random.seed(0)  # So the mock data will be stable across runs.

    csv_path = "/tmp/demo.csv"
    contributions = 10

    with open(csv_path, "w", newline="") as demo_handle:
        fields = ["student_id", "class_year", "hw_number", "grade"]
        writer = csv.DictWriter(demo_handle, fieldnames=fields)
        writer.writeheader()
        for student_id in range(1, 101):
            class_year = int(_clip(random.gauss(2, 1), 1, 4))
            # Older students do slightly better in the class:
            mean_grade = random.gauss(80, 5) + class_year * 2
            for hw_number in range(1, contributions + 1):
                grade = int(_clip(random.gauss(mean_grade, 5), 0, 100))
                writer.writerow(
                    {
                        "student_id": student_id,
                        "class_year": class_year,
                        "hw_number": hw_number,
                        "grade": grade,
                    }
                )

    return CLIInfo(csv_path=csv_path, contributions=contributions, is_demo=True)


CLIInfo = namedtuple("CLIInfo", ["csv_path", "contributions", "is_demo"])


def get_cli_info():  # pragma: no cover
    args = _get_args()
    if args.demo:
        if args.csv_path is not None:
            warn('"--demo" overrides "--csv" and "--contrib"')
        return _get_demo_csv_contrib()
    return CLIInfo(
        csv_path=args.csv_path, contributions=args.contributions, is_demo=False
    )
