import csv
import random
import re
from pathlib import Path

import polars as pl

from dp_wizard.types import ColumnId, ColumnLabel, ColumnName


def convert_text(text: str, target_type: pl.DataType) -> list[str | float]:
    """
    >>> convert_text("\\n\\n before\\n \\nand, after \\n\\n", pl.String)
    ['before', 'and', 'after']

    >>> convert_text("-1,0,1,3.14159", pl.Int32)
    [-1, 0, 1]

    >>> convert_text("-1.1,0,1.1,foobar", pl.Float32)
    [-1.1, 0.0, 1.1]
    """
    if target_type.is_float():
        convert = float
    elif target_type.is_integer():
        convert = int
    elif target_type == pl.Boolean:
        convert = bool
    elif target_type == pl.String:
        convert = str
    else:
        raise Exception(f"Unexpected type: {target_type}")  # pragma: no cover

    def safe_convert(value: str) -> str | float | bool | None:
        try:
            new = convert(value)
        except ValueError:
            new = None
        return new

    clean_lines = [
        clean_line for line in re.split(r"[\n,]", text) if (clean_line := line.strip())
    ]

    converted_lines = [
        converted_line
        for line in clean_lines
        if (converted_line := safe_convert(line)) is not None
    ]
    return converted_lines


def read_polars_schema(csv_path: Path | bytes) -> pl.Schema:
    # Polars is overkill, but it is more robust against
    # variations in encoding than Python stdlib csv.
    # However, it could be slow:
    #
    # > Determining the column names of a LazyFrame requires
    # > resolving its schema, which is a potentially expensive operation.
    lf = pl.scan_csv(csv_path)
    # TODO: What happens if column names are missing?
    return lf.collect_schema()


def read_csv_numeric_names(csv_path: Path) -> list[ColumnName]:  # pragma: no cover
    lf = pl.scan_csv(csv_path)
    numeric_names = [
        name for name, pl_type in lf.collect_schema().items() if pl_type.is_numeric()
    ]
    # Exclude columns missing names:
    return [ColumnName(name) for name in numeric_names if name.strip() != ""]


def get_csv_names_mismatch(
    public_csv_path: Path, private_csv_path: Path
) -> tuple[set[ColumnName], set[ColumnName]]:
    public_names = set(ColumnName(name) for name in read_polars_schema(public_csv_path))
    private_names = set(
        ColumnName(name) for name in read_polars_schema(private_csv_path)
    )
    extra_public = public_names - private_names
    extra_private = private_names - public_names
    return (extra_public, extra_private)


def get_csv_row_count(csv_path: Path) -> int:
    lf = pl.scan_csv(csv_path)
    return lf.select(pl.len()).collect().item()


def id_labels_dict_from_schema(schema: pl.Schema) -> dict[ColumnId, ColumnLabel]:
    """
    >>> id_labels_dict_from_schema(pl.Schema({"abc": pl.Int32}))
    {'...': '1: abc'}
    """
    return {
        ColumnId(name): ColumnLabel(f"{i+1}: {name}")
        for i, name in enumerate(schema.keys())
    }


def id_names_dict_from_schema(schema: pl.Schema) -> dict[ColumnId, ColumnName]:
    """
    >>> id_names_dict_from_schema(pl.Schema({"abc": pl.Int32}))
    {'...': 'abc'}
    """
    return {ColumnId(name): ColumnName(name) for name in schema.keys()}


def make_sample_csv(path: Path, contributions: int) -> None:
    """
    >>> import tempfile
    >>> from pathlib import Path
    >>> import csv
    >>> with tempfile.NamedTemporaryFile() as temp:
    ...     make_sample_csv(Path(temp.name), 10)
    ...     with open(temp.name, newline="") as csv_handle:
    ...         reader = csv.DictReader(csv_handle)
    ...         reader.fieldnames
    ...         rows = list(reader)
    ...         rows[0].values()
    ...         rows[-1].values()
    ['student_id', 'class_year_str', 'hw_number', 'grade', 'self_assessment']
    dict_values(['1', 'sophomore', '1', '82', '0'])
    dict_values(['100', 'sophomore', '10', '78', '0'])
    """
    random.seed(0)  # So the mock data will be stable across runs.
    with path.open("w", newline="") as sample_csv_handle:
        fields = [
            "student_id",
            "class_year_str",
            "hw_number",
            "grade",
            "self_assessment",
        ]
        class_year_map = ["first year", "sophomore", "junior", "senior"]
        writer = csv.DictWriter(sample_csv_handle, fieldnames=fields)
        writer.writeheader()
        for student_id in range(1, 101):
            class_year = int(_clip(random.gauss(1, 1), 0, 3))
            for hw_number in range(1, contributions + 1):
                # Older students do slightly better in the class,
                # but each assignment gets harder.
                mean_grade = random.gauss(90, 5) + (class_year + 1) * 2 - hw_number
                grade = int(_clip(random.gauss(mean_grade, 5), 0, 100))
                self_assessment = 1 if grade > 90 and random.random() > 0.1 else 0
                writer.writerow(
                    {
                        "student_id": student_id,
                        "class_year_str": class_year_map[class_year],
                        "hw_number": hw_number,
                        "grade": grade,
                        "self_assessment": self_assessment,
                    }
                )


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
