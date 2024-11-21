"""
Strings of ALL CAPS are replaced in these templates.
Keeping them in a format which can actually be parsed as python
makes some things easier, but it is also reinventing the wheel.
We may revisit this.
"""

from typing import Iterable, Any, Optional
from pathlib import Path
import re
from dp_wizard.utils.csv_helper import name_to_identifier


class _Template:
    def __init__(self, path: Optional[str], template: Optional[str] = None):
        if path is not None:
            self._path = f"_{path}.py"
            template_path = Path(__file__).parent / "no-tests" / self._path
            self._template = template_path.read_text()
        if template is not None:
            if path is not None:
                raise Exception('"path" and "template" are mutually exclusive')
            self._path = "template-instead-of-path"
            self._template = template
        self._initial_slots = self._find_slots()

    def _find_slots(self):
        # Slots:
        # - are all caps or underscores
        # - have word boundary on either side
        # - are at least three characters
        slot_re = r"\b[A-Z][A-Z_]{2,}\b"
        return set(re.findall(slot_re, self._template))

    def fill_expressions(self, **kwargs: str):
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template = re.sub(rf"\b{k_re}\b", str(v), self._template)
        return self

    def fill_values(self, **kwargs: Any):
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template = re.sub(rf"\b{k_re}\b", repr(v), self._template)
        return self

    def fill_blocks(self, **kwargs: str):
        for k, v in kwargs.items():

            def match_indent(match: re.Match[str]):
                # This does what we want, but binding is confusing.
                indented_lines: list[str] = [
                    match.group(1) + line for line in v.split("\n")  # noqa: B023
                ]
                return "\n".join(indented_lines)

            k_re = re.escape(k)
            self._template = re.sub(
                rf"^([ \t]*){k_re}$",
                match_indent,
                self._template,
                flags=re.MULTILINE,
            )
        return self

    def finish(self) -> str:
        unfilled_slots = self._initial_slots & self._find_slots()
        if unfilled_slots:
            raise Exception(
                f"Template {self._path} has unfilled slots: "
                f'{", ".join(sorted(unfilled_slots))}\n\n{self._template}'
            )
        return self._template


def _make_margins_dict(bin_names: Iterable[str]):
    # TODO: Don't worry too much about the formatting here.
    # Plan to run the output through black for consistency.
    # https://github.com/opendp/dp-creator-ii/issues/50
    margins = (
        [
            """
        (): dp.polars.Margin(
            public_info="lengths",
        ),"""
        ]
        + [
            f"""
        ("{bin_name}",): dp.polars.Margin(
            public_info="keys",
        ),"""
            for bin_name in bin_names
        ]
    )

    margins_dict = "{" + "".join(margins) + "\n    }"
    return margins_dict


def _make_context_for_notebook(
    csv_path: str,
    contributions: int,
    epsilon: float,
    weights: Iterable[int],
    column_names: Iterable[str],
):
    privacy_unit_block = make_privacy_unit_block(contributions)
    privacy_loss_block = make_privacy_loss_block(epsilon)
    margins_dict = _make_margins_dict([f"{name}_bin" for name in column_names])
    columns = ", ".join([f"{name}_config" for name in column_names])
    return (
        _Template("context")
        .fill_expressions(
            MARGINS_DICT=margins_dict,
            COLUMNS=columns,
        )
        .fill_values(
            CSV_PATH=csv_path,
            WEIGHTS=weights,
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK=privacy_unit_block,
            PRIVACY_LOSS_BLOCK=privacy_loss_block,
        )
        .finish()
    )


def _make_context_for_script(
    contributions: int,
    epsilon: float,
    weights: Iterable[float],
    column_names: Iterable[str],
):
    privacy_unit_block = make_privacy_unit_block(contributions)
    privacy_loss_block = make_privacy_loss_block(epsilon)
    margins_dict = _make_margins_dict([f"{name}_bin" for name in column_names])
    columns = ",".join([f"{name}_config" for name in column_names])
    return (
        _Template("context")
        .fill_expressions(
            CSV_PATH="csv_path",
            MARGINS_DICT=margins_dict,
            COLUMNS=columns,
        )
        .fill_values(
            WEIGHTS=weights,
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK=privacy_unit_block,
            PRIVACY_LOSS_BLOCK=privacy_loss_block,
            MARGINS_DICT=margins_dict,
        )
        .finish()
    )


def _make_imports():
    return (
        _Template("imports").fill_values().finish()
        + (Path(__file__).parent.parent / "shared.py").read_text()
    )


def _make_columns(columns: dict[str, dict[str, str]]) -> str:
    return "\n".join(
        make_column_config_block(
            name=name,
            lower_bound=col["lower_bound"],  # type: ignore
            upper_bound=col["upper_bound"],  # type: ignore
            bin_count=col["bin_count"],  # type: ignore
        )
        for name, col in columns.items()  # type: ignore
    )


def _make_query(column_name: str):
    indentifier = name_to_identifier(column_name)
    return (
        _Template("query")
        .fill_values(
            BIN_NAME=f"{indentifier}_bin",
        )
        .fill_expressions(
            QUERY_NAME=f"{indentifier}_query",
            ACCURACY_NAME=f"{indentifier}_accuracy",
            HISTOGRAM_NAME=f"{indentifier}_histogram",
        )
        .finish()
    )


def _make_queries(column_names: Iterable[str]):
    return "confidence = 0.95\n\n" + "\n".join(
        _make_query(column_name) for column_name in column_names
    )


def make_notebook_py(
    csv_path: str,
    contributions: int,
    epsilon: float,
    columns: dict[str, dict[str, Any]],
):
    return (
        _Template("notebook")
        .fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            COLUMNS_BLOCK=_make_columns(columns),
            CONTEXT_BLOCK=_make_context_for_notebook(
                csv_path=csv_path,
                contributions=contributions,
                epsilon=epsilon,
                weights=[column["weight"] for column in columns.values()],
                column_names=[name_to_identifier(name) for name in columns.keys()],
            ),
            QUERIES_BLOCK=_make_queries(columns.keys()),
        )
        .finish()
    )


def make_script_py(
    contributions: int, epsilon: float, columns: dict[str, dict[str, Any]]
):
    return (
        _Template("script")
        .fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            COLUMNS_BLOCK=_make_columns(columns),
            CONTEXT_BLOCK=_make_context_for_script(
                # csv_path is a CLI parameter in the script
                contributions=contributions,
                epsilon=epsilon,
                weights=[column["weight"] for column in columns.values()],
                column_names=[name_to_identifier(name) for name in columns.keys()],
            ),
            QUERIES_BLOCK=_make_queries(columns.keys()),
        )
        .finish()
    )


def make_privacy_unit_block(contributions: int):
    return _Template("privacy_unit").fill_values(CONTRIBUTIONS=contributions).finish()


def make_privacy_loss_block(epsilon: float):
    return _Template("privacy_loss").fill_values(EPSILON=epsilon).finish()


def make_column_config_block(
    name: str, lower_bound: float, upper_bound: float, bin_count: int
) -> str:
    """
    >>> print(make_column_config_block(
    ...     name="HW GRADE",
    ...     lower_bound=0,
    ...     upper_bound=100,
    ...     bin_count=10
    ... ))
    # From the public information, determine the bins for 'HW GRADE':
    hw_grade_cut_points = make_cut_points(
        lower_bound=0,
        upper_bound=100,
        bin_count=10,
    )
    <BLANKLINE>
    # Use these bins to define a Polars column:
    hw_grade_config = (
        pl.col('HW GRADE')
        .cut(hw_grade_cut_points)
        .alias('hw_grade_bin')  # Give the new column a name.
        .cast(pl.String)
    )
    <BLANKLINE>
    """
    snake_name = _snake_case(name)
    return (
        _Template("column_config")
        .fill_expressions(
            CUT_LIST_NAME=f"{snake_name}_cut_points",
            POLARS_CONFIG_NAME=f"{snake_name}_config",
        )
        .fill_values(
            LOWER_BOUND=lower_bound,
            UPPER_BOUND=upper_bound,
            BIN_COUNT=bin_count,
            COLUMN_NAME=name,
            BIN_COLUMN_NAME=f"{snake_name}_bin",
        )
        .finish()
    )


def _snake_case(name: str):
    """
    >>> _snake_case("HW GRADE")
    'hw_grade'
    """
    return re.sub(r"\W+", "_", name.lower())
