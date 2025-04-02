from sys import argv
from pathlib import Path
import argparse
import csv
import random
from typing import NamedTuple, Optional


def _existing_csv_type(arg: str) -> Path:
    path = Path(arg)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"No such file: {arg}")
    if path.suffix != ".csv":
        raise argparse.ArgumentTypeError(f'Must have ".csv" extension: {arg}')
    return path


PUBLIC_TEXT = """if you have a public data set, and are curious how
DP can be applied: The preview visualizations will use your public data."""
PRIVATE_TEXT = """if you only have a private data set, and want to
make a release from it: The preview visualizations will only use
simulated data, and apart from the headers, the private CSV is not
read until the release."""
PUBLIC_PRIVATE_TEXT = """if you have two CSVs
with the same structure. Perhaps the public CSV is older and no longer
sensitive. Preview visualizations will be made with the public data,
but the release will be made with private data."""


def _get_arg_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="DP Wizard makes it easier to get started with "
        "Differential Privacy.",
        epilog=f"""
Use "--public_csv" {PUBLIC_TEXT}

Use "--private_csv" {PRIVATE_TEXT}

Use "--public_csv" and "--private_csv" together {PUBLIC_PRIVATE_TEXT}
""",
    )
    parser.add_argument(
        "--public_csv",
        dest="public_csv_path",
        metavar="CSV",
        type=_existing_csv_type,
        help="Path to public CSV",
    )
    parser.add_argument(
        "--private_csv",
        dest="private_csv_path",
        metavar="CSV",
        type=_existing_csv_type,
        help="Path to private CSV",
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
    Namespace(public_csv_path=None, private_csv_path=None, contributions=1, demo=False)
    """
    arg_parser = _get_arg_parser()

    if "pytest" in argv[0] or ("shiny" in argv[0] and "run" == argv[1]):
        # We are running a test,
        # and ARGV is polluted, so override:
        args = arg_parser.parse_args([])  # pragma: no cover
    else:
        # Normal parsing:
        args = arg_parser.parse_args()  # pragma: no cover

    if args.demo:  # pragma: no cover
        other_args = {arg for arg in dir(args) if not arg.startswith("_")} - {
            "demo",
            "contributions",
        }
        set_args = [k for k in other_args if getattr(args, k) is not None]
        if set_args:
            arg_parser.error(
                "When --demo is set, other arguments should be skipped: "
                + ", ".join(set_args)
            )
    return args


def _clip(n: float, lower_bound: float, upper_bound: float) -> float:
    """
    >>> _clip(-5, 0, 10)
    0
    >>> _clip(5, 0, 10)
    5
    >>> _clip(15, 0, 10)
    10
    """
    return max(min(n, upper_bound), lower_bound)


class CLIInfo(NamedTuple):
    public_csv_path: Optional[str]
    private_csv_path: Optional[str]
    contributions: int
    is_demo: bool


def _make_fake_data(path: Path, contributions):
    random.seed(0)  # So the mock data will be stable across runs.
    with path.open("w", newline="") as demo_handle:
        fields = ["student_id", "class_year", "hw_number", "grade", "self_assessment"]
        writer = csv.DictWriter(demo_handle, fieldnames=fields)
        writer.writeheader()
        for student_id in range(1, 101):
            class_year = int(_clip(random.gauss(2, 1), 1, 4))
            for hw_number in range(1, contributions + 1):
                # Older students do slightly better in the class,
                # but each assignment gets harder.
                mean_grade = random.gauss(90, 5) + class_year * 2 - hw_number
                grade = int(_clip(random.gauss(mean_grade, 5), 0, 100))
                self_assessment = 1 if grade > 90 and random.random() > 0.1 else 0
                writer.writerow(
                    {
                        "student_id": student_id,
                        "class_year": class_year,
                        "hw_number": hw_number,
                        "grade": grade,
                        "self_assessment": self_assessment,
                    }
                )


def _get_demo_cli_info() -> CLIInfo:
    """
    >>> cli_info = _get_demo_cli_info()
    >>> with open(cli_info.private_csv_path, newline="") as csv_handle:
    ...     reader = csv.DictReader(csv_handle)
    ...     reader.fieldnames
    ...     rows = list(reader)
    ...     rows[0].values()
    ...     rows[-1].values()
    ['student_id', 'class_year', 'hw_number', 'grade', 'self_assessment']
    dict_values(['1', '2', '1', '82', '0'])
    dict_values(['100', '2', '10', '78', '0'])
    """
    private_csv_path = Path(__file__).parent.parent / "tmp" / "demo.csv"
    contributions = 10
    _make_fake_data(private_csv_path, contributions)

    return CLIInfo(
        public_csv_path=None,
        private_csv_path=str(private_csv_path),
        contributions=contributions,
        is_demo=True,
    )


def get_cli_info() -> CLIInfo:  # pragma: no cover
    args = _get_args()
    if args.demo:
        return _get_demo_cli_info()
    return CLIInfo(
        public_csv_path=args.public_csv_path,
        private_csv_path=args.private_csv_path,
        contributions=args.contributions,
        is_demo=False,
    )
