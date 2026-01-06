import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import polars as pl
from shiny import reactive


class Weight(Enum):
    """
    >>> print(Weight.MORE_ACCURATE)
    More accurate
    >>> ints = [int(w.value) for w in Weight]
    >>> assert ints[2] / ints[1] == ints[1] / ints[0]
    """

    MORE_PRIVATE = "1"
    DEFAULT = "2"
    MORE_ACCURATE = "4"

    def __str__(self) -> str:
        return self.name.replace("_", " ").capitalize()


class Product(Enum):
    STATISTICS = auto()
    SYNTHETIC_DATA = auto()

    @classmethod
    def to_dict(cls) -> dict[str, str]:
        """
        >>> Product.to_dict()
        {'1': 'DP Statistics', '2': 'DP Synthetic Data'}
        """
        return {
            str(member.value): str(member) for (_, member) in cls.__members__.items()
        }

    def __str__(self) -> str:
        return "DP " + self.name.replace("_", " ").title()


class StatisticName(str):
    """
    A name like "Histogram" or "Mean".
    """

    pass


class ColumnName(str):
    """
    The exact column header in the CSV.
    """

    pass


class ColumnLabel(str):
    """
    The column label displayed in the UI.
    """

    pass


class ColumnId(str):
    """
    The opaque string we pass as a module ID.

    If we just sanitize the user string, it might collide with another user string.
    Hashing is safer, although hash collisions are not impossible.

    >>> import re
    >>> assert re.match(r'^[_0-9]+$', ColumnId('xyz'))
    """

    def __new__(cls, content: str):
        id = str(hash(content)).replace("-", "_")
        return str.__new__(cls, id)


class ColumnIdentifier(str):
    """
    A human-readable form that is a valid Python identifier.

    >>> ColumnIdentifier("basic")
    'basic'
    >>> ColumnIdentifier("1: Does this work?!")
    'number_1_does_this_work_'
    """

    def __new__(cls, content: str):
        identifier = re.sub(r"\W+", "_", content).lower()
        if re.match(r"\d", identifier):
            identifier = f"number_{identifier}"
        return str.__new__(cls, identifier)


class CsvInfo:
    def __init__(self, csv_path: Path | None):
        self._schema = (
            {
                ColumnName(k): v
                for k, v in pl.scan_csv(
                    csv_path,
                    # Read the whole CSV:
                    # Until we hear that this is too slow,
                    # it's better to be sure the types
                    # have been accurately inferred.
                    infer_schema_length=None,
                    # Default is to raise NoDataError:
                    # We prefer to validate below and set error.
                    raise_if_empty=False,
                )
                .collect_schema()
                .items()
                if k.strip() != ""
            }
            if csv_path is not None
            else {}
        )
        self._warnings: list[str] = []
        self._errors: list[str] = []
        column_names = self._schema.keys()

        # Schema errors:
        if column_names and not any(
            # startswith("_duplicated_") is there in case there are
            # multiple columns with missing names: Polars will retitle
            # those after the first.
            name and not name.startswith("_duplicated_")
            for name in column_names
        ):
            self._errors.append("No column names detected: First row of CSV empty?")
            return

        # Schema warnings:
        if column_names and not any(
            data_type.is_numeric() for data_type in self._schema.values()
        ):
            self._warnings.append("No numeric columns detected.")
        if len(column_names) == 1:
            columns = "".join(column_names)
            self._warnings.append(f"Only one column detected: '{columns}'")

        for column_name in column_names:

            # Row errors:
            tab = "\t"
            if tab in column_name:
                escaped_tab = "\\t"
                self._errors.append(
                    f"Tab in column name: '{column_name.replace(tab, escaped_tab)}'; "
                    "Is this actually a TSV rather than a CSV?"
                )
                return
            elif "�" in column_name:
                self._errors.append(
                    f"Bad column name: '{column_name}'; Is this a UTF-8 CSV?"
                )
                return

            # Row warnings:
            try:
                float(column_name)
                self._warnings.append(
                    f"Numeric column name: '{column_name}'; "
                    "Is the CSV missing a header row?"
                )
            except ValueError:
                pass
            if "_duplicated_" in column_name:
                self._warnings.append(
                    f"Column name modified to avoid duplication: '{column_name}'"
                )
            if column_name.strip() != column_name:
                self._warnings.append(
                    f"Column name is padded: '{column_name}'; "
                    "Padded numeric values will be treated as strings."
                )

    def __repr__(self):
        warnings = self._warnings
        errors = self._errors
        return f"CsvInfo({self._schema}, {warnings=}, {errors=})"

    def get_schema(self) -> dict[ColumnName, pl.DataType]:
        if self._errors:
            return {}  # pragma: no cover
        return self._schema

    def get_all_column_names(self) -> list[ColumnName]:
        if self._errors:
            return []
        return list(self._schema.keys())

    def get_numeric_column_names(self) -> list[ColumnName]:
        if self._errors:
            return []
        return [k for k, v in self._schema.items() if v.is_numeric()]

    def get_messages(self) -> list[str]:
        return self._errors + self._warnings

    def get_is_error(self) -> bool:
        return bool(self._errors)


@dataclass(kw_only=True, frozen=True)
class AppState:
    # CLI options:
    is_sample_csv: bool
    in_cloud: bool
    qa_mode: bool

    # Reactive bools:
    is_tutorial_mode: reactive.Value[bool]
    is_dataset_selected: reactive.Value[bool]
    is_analysis_defined: reactive.Value[bool]
    is_released: reactive.Value[bool]

    # Dataset choices:
    initial_private_csv_path: str
    private_csv_path: reactive.Value[str]
    initial_public_csv_path: str
    public_csv_path: reactive.Value[str]
    contributions: reactive.Value[int]
    contributions_entity: reactive.Value[str]
    max_rows: reactive.Value[str]
    initial_product: Product
    product: reactive.Value[Product]

    # Analysis choices:
    csv_info: reactive.Value[CsvInfo]
    group_column_names: reactive.Value[list[ColumnName]]
    epsilon: reactive.Value[float]

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    statistic_names: reactive.Value[dict[ColumnName, StatisticName]]
    lower_bounds: reactive.Value[dict[ColumnName, float]]
    upper_bounds: reactive.Value[dict[ColumnName, float]]
    bin_counts: reactive.Value[dict[ColumnName, int]]
    weights: reactive.Value[dict[ColumnName, Weight]]
    analysis_errors: reactive.Value[dict[ColumnName, bool]]

    # Per-group choices:
    # (Again a dict, with ColumnName as the key.)
    group_keys: reactive.Value[dict[ColumnName, list[str | float | bool]]]
