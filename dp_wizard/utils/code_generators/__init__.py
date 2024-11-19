from typing import NamedTuple
from abc import ABC, abstractmethod
from pathlib import Path
import re
from dp_wizard.utils.csv_helper import name_to_identifier
from dp_wizard.utils.code_generators._template import Template


class AnalysisPlanColumn(NamedTuple):
    lower_bound: float
    upper_bound: float
    bin_count: int
    weight: int


class AnalysisPlan(NamedTuple):
    csv_path: str
    contributions: int
    epsilon: float
    columns: dict[str, AnalysisPlanColumn]


class _CodeGenerator(ABC):
    def __init__(self, analysis_plan):
        self.csv_path = analysis_plan.csv_path
        self.contributions = analysis_plan.contributions
        self.epsilon = analysis_plan.epsilon
        self.columns = analysis_plan.columns

    @abstractmethod
    def _make_context(self): ...  # pragma: no cover

    def make_py(self):
        return str(
            Template(self.root_template).fill_blocks(
                IMPORTS_BLOCK=_make_imports(),
                COLUMNS_BLOCK=self._make_columns(self.columns),
                CONTEXT_BLOCK=self._make_context(),
                QUERIES_BLOCK=self._make_queries(self.columns.keys()),
            )
        )

    def _make_margins_dict(self, bin_names):
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

    def _make_columns(self, columns):
        return "\n".join(
            make_column_config_block(
                name=name,
                lower_bound=col.lower_bound,
                upper_bound=col.upper_bound,
                bin_count=col.bin_count,
            )
            for name, col in columns.items()
        )

    def _make_queries(self, column_names):
        return "confidence = 0.95\n\n" + "\n".join(
            _make_query(column_name) for column_name in column_names
        )

    def _make_partial_context(self):
        weights = [column.weight for column in self.columns.values()]
        column_names = [name_to_identifier(name) for name in self.columns.keys()]
        privacy_unit_block = make_privacy_unit_block(self.contributions)
        privacy_loss_block = make_privacy_loss_block(self.epsilon)
        margins_dict = self._make_margins_dict([f"{name}_bin" for name in column_names])
        columns = ", ".join([f"{name}_config" for name in column_names])
        return (
            Template("context")
            .fill_expressions(
                MARGINS_DICT=margins_dict,
                COLUMNS=columns,
            )
            .fill_values(
                WEIGHTS=weights,
            )
            .fill_blocks(
                PRIVACY_UNIT_BLOCK=privacy_unit_block,
                PRIVACY_LOSS_BLOCK=privacy_loss_block,
            )
        )


class NotebookGenerator(_CodeGenerator):
    root_template = "notebook"

    def _make_context(self):
        return str(self._make_partial_context().fill_values(CSV_PATH=self.csv_path))


class ScriptGenerator(_CodeGenerator):
    root_template = "script"

    def _make_context(self):
        return str(self._make_partial_context().fill_expressions(CSV_PATH="csv_path"))


# Public functions used to generate code snippets in the UI;
# These do not require an entire analysis plan, so they stand on their own.


def make_privacy_unit_block(contributions):
    return str(Template("privacy_unit").fill_values(CONTRIBUTIONS=contributions))


def make_privacy_loss_block(epsilon):
    return str(Template("privacy_loss").fill_values(EPSILON=epsilon))


def make_column_config_block(name, lower_bound, upper_bound, bin_count):
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
    return str(
        Template("column_config")
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
    )


# Private helper functions:
# These do not depend on the AnalysisPlan,
# so it's better to keep them out of the class.


def _make_query(column_name):
    indentifier = name_to_identifier(column_name)
    return str(
        Template("query")
        .fill_values(
            BIN_NAME=f"{indentifier}_bin",
        )
        .fill_expressions(
            QUERY_NAME=f"{indentifier}_query",
            ACCURACY_NAME=f"{indentifier}_accuracy",
            HISTOGRAM_NAME=f"{indentifier}_histogram",
        )
    )


def _snake_case(name: str):
    """
    >>> _snake_case("HW GRADE")
    'hw_grade'
    """
    return re.sub(r"\W+", "_", name.lower())


def _make_imports():
    return (
        str(Template("imports").fill_values())
        + (Path(__file__).parent.parent / "shared.py").read_text()
    )
