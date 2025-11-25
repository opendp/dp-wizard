from pathlib import Path

import polars as pl

from dp_wizard.types import ColumnId, ColumnLabel, ColumnName


def read_polars_schema(csv_path: Path) -> pl.Schema:
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
