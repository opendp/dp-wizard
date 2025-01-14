"""
We'll use the following terms consistently throughout the application:
- name: This is the exact column header in the CSV.
- label: This is the string we'll display.
- id: This is the opaque string we'll pass as a module ID.
- identifier: This is a form that can be used as a Python identifier.
"""

import re
import polars as pl
from pathlib import Path


def read_csv_names(csv_path: Path):
    # Polars is overkill, but it is more robust against
    # variations in encoding than Python stdlib csv.
    # However, it could be slow:
    #
    # > Determining the column names of a LazyFrame requires
    # > resolving its schema, which is a potentially expensive operation.
    lf = pl.scan_csv(csv_path)
    return lf.collect_schema().names()


def get_csv_names_mismatch(public_csv_path: Path, private_csv_path: Path):
    public_names = set(read_csv_names(public_csv_path))
    private_names = set(read_csv_names(private_csv_path))
    extra_public = public_names - private_names
    extra_private = private_names - public_names
    return (extra_public, extra_private)


def get_csv_row_count(csv_path: Path):
    lf = pl.scan_csv(csv_path)
    return lf.select(pl.len()).collect().item()


def read_csv_ids_labels(csv_path: Path):
    return {
        name_to_id(name): f"{i+1}: {name or '[blank]'}"
        for i, name in enumerate(read_csv_names(csv_path))
    }


def read_csv_ids_names(csv_path: Path):
    return {name_to_id(name): name for name in read_csv_names(csv_path)}


def name_to_id(name: str):
    # Shiny is fussy about module IDs,
    # but we don't need them to be human readable.
    return str(hash(name)).replace("-", "_")


def name_to_identifier(name: str):
    return re.sub(r"\W+", "_", name).lower()
