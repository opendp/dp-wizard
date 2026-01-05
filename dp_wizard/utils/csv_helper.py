import csv
import random
import re
from pathlib import Path

import polars as pl

from dp_wizard.types import ColumnId, ColumnLabel, ColumnName, CsvInfo


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


def get_csv_names_mismatch(
    public_csv_path: Path, private_csv_path: Path
) -> tuple[set[ColumnName], set[ColumnName]]:
    public_names = set(CsvInfo(public_csv_path).get_all_column_names())
    private_names = set(CsvInfo(private_csv_path).get_all_column_names())
    extra_public = public_names - private_names
    extra_private = private_names - public_names
    return (extra_public, extra_private)


def get_csv_row_count(csv_path: Path) -> int:
    lf = pl.scan_csv(csv_path, ignore_errors=True)
    return lf.select(pl.len()).collect().item()


def id_labels_dict_from_schema(
    schema: dict[ColumnName, pl.DataType],
) -> dict[ColumnId, ColumnLabel]:
    """
    >>> id_labels_dict_from_schema(pl.Schema({"abc": pl.Int32}))
    {'...': '1: abc'}
    """
    return {
        ColumnId(name): ColumnLabel(f"{i+1}: {name}")
        for i, name in enumerate(schema.keys())
    }


def id_names_dict_from_schema(
    schema: dict[ColumnName, pl.DataType],
) -> dict[ColumnId, ColumnName]:
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


def infer_csv_info(names_values_str: str) -> CsvInfo:
    """
    >>> infer_csv_info("missing\\nstr : foobar\\nint:42")
    CsvInfo({'missing': String, 'str': String, 'int': Int64}, warnings=[], errors=[])
    >>> infer_csv_info("")
    CsvInfo({}, warnings=[], errors=[])

    """
    names_values_list = [
        (name_value.split(":") + ["", ""])[:2]
        for name_value in names_values_str.splitlines()
    ]
    names_values_dict = {
        name.strip(): value.strip() for [name, value] in names_values_list
    }
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile("w") as tmp:
        tmp.write(",".join(names_values_dict.keys()))
        tmp.write("\n")
        tmp.write(",".join(names_values_dict.values()))
        tmp.flush()
        return CsvInfo(Path(tmp.name))


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
