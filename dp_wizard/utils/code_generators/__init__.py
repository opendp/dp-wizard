from typing import NamedTuple, Optional, Iterable
from abc import ABC, abstractmethod
from pathlib import Path
import re

import black

from dp_wizard.utils.csv_helper import name_to_identifier
from dp_wizard.utils.code_generators._template import Template
from dp_wizard.utils.dp_helper import confidence


class AnalysisPlanColumn(NamedTuple):
    lower_bound: float
    upper_bound: float
    bin_count: int
    weight: int


class AnalysisPlan(NamedTuple):
    csv_path: Optional[str]
    contributions: int
    epsilon: float
    columns: dict[str, AnalysisPlanColumn]


class _CodeGenerator(ABC):
    root_template = "placeholder"

    def __init__(self, analysis_plan: AnalysisPlan):
        self.csv_path = analysis_plan.csv_path
        self.contributions = analysis_plan.contributions
        self.epsilon = analysis_plan.epsilon
        self.columns = analysis_plan.columns

    @abstractmethod
    def _make_context(self) -> str: ...  # pragma: no cover

    def _make_extra_blocks(self):
        return {}

    def make_py(self):
        code = (
            Template(self.root_template)
            .fill_blocks(
                IMPORTS_BLOCK=_make_imports(),
                COLUMNS_BLOCK=self._make_columns(),
                CONTEXT_BLOCK=self._make_context(),
                QUERIES_BLOCK=self._make_queries(),
                **self._make_extra_blocks(),
            )
            .finish()
        )
        return black.format_str(code, mode=black.Mode())

    def _make_margins_dict(self, bin_names: Iterable[str]):
        margins = ["(): dp.polars.Margin(public_info='lengths',),"] + [
            f"('{bin_name}',): dp.polars.Margin(public_info='keys',),"
            for bin_name in bin_names
        ]

        margins_dict = "{" + "".join(margins) + "\n    }"
        return margins_dict

    def _make_columns(self):
        return "\n".join(
            make_column_config_block(
                name=name,
                lower_bound=col.lower_bound,
                upper_bound=col.upper_bound,
                bin_count=col.bin_count,
            )
            for name, col in self.columns.items()
        )

    def _make_pre(self) -> str:
        """
        If generating a notebook, this will open a new code paragraph.
        """
        return ""

    def _make_post(self) -> str:
        """
        If generating a notebook, this will close a new code paragraph.
        """
        return ""

    def _make_confidence_note(self):
        return f"{int(confidence * 100)}% confidence interval"

    def _make_queries(self):
        pre = self._make_pre()
        post = self._make_post()
        column_names = self.columns.keys()
        return (
            f"{pre}confidence = {confidence} # {self._make_confidence_note()}\n{post}"
            + "\n".join(
                f"{pre}{self._make_query(column_name)}{post}"
                for column_name in column_names
            )
        )

    def _make_query(self, column_name):
        indentifier = name_to_identifier(column_name)
        title = f"DP counts for {column_name}"
        accuracy_name = f"{indentifier}_accuracy"
        histogram_name = f"{indentifier}_histogram"
        return (
            Template("query")
            .fill_values(
                BIN_NAME=f"{indentifier}_bin",
            )
            .fill_expressions(
                QUERY_NAME=f"{indentifier}_query",
                ACCURACY_NAME=accuracy_name,
                HISTOGRAM_NAME=histogram_name,
            )
            .fill_blocks(
                OUTPUT_BLOCK=self._make_output(
                    title=title,
                    accuracy_name=accuracy_name,
                    histogram_name=histogram_name,
                )
            )
            .finish()
        )

    def _make_output(self, title: str, accuracy_name: str, histogram_name: str):
        return (
            Template(f"{self.root_template}_output")
            .fill_values(
                TITLE=title,
            )
            .fill_expressions(
                ACCURACY_NAME=accuracy_name,
                HISTOGRAM_NAME=histogram_name,
                CONFIDENCE_NOTE=self._make_confidence_note(),
            )
            .finish()
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
        return self._make_partial_context().fill_values(CSV_PATH=self.csv_path).finish()

    def _make_pre(self):
        return "# +\n"

    def _make_post(self):
        return "# -\n"

    def _make_extra_blocks(self):
        outputs_expression = (
            "{"
            + ",".join(
                Template("report_kv")
                .fill_values(
                    NAME=name,
                    CONFIDENCE=confidence,
                )
                .fill_expressions(
                    IDENTIFIER_HISTOGRAM=f"{name_to_identifier(name)}_histogram",
                    IDENTIFIER_ACCURACY=f"{name_to_identifier(name)}_accuracy",
                )
                .finish()
                for name in self.columns.keys()
            )
            + "}"
        )
        tmp_path = Path(__file__).parent.parent.parent / "tmp"
        reports_block = (
            Template("reports")
            .fill_expressions(
                OUTPUTS=outputs_expression,
                COLUMNS={k: v._asdict() for k, v in self.columns.items()},
            )
            .fill_values(
                CSV_PATH=self.csv_path,
                EPSILON=self.epsilon,
                TXT_REPORT_PATH=str(tmp_path / "report.txt"),
                CSV_REPORT_PATH=str(tmp_path / "report.csv"),
            )
            .finish()
        )
        return {"REPORTS_BLOCK": reports_block}


class ScriptGenerator(_CodeGenerator):
    root_template = "script"

    def _make_context(self):
        return (
            self._make_partial_context().fill_expressions(CSV_PATH="csv_path").finish()
        )

    def _make_confidence_note(self):
        # In the superclass, the string is unquoted so it can be
        # used in comments: It needs to be wrapped here.
        return repr(super()._make_confidence_note())


# Public functions used to generate code snippets in the UI;
# These do not require an entire analysis plan, so they stand on their own.


def make_privacy_unit_block(contributions: int):
    return Template("privacy_unit").fill_values(CONTRIBUTIONS=contributions).finish()


def make_privacy_loss_block(epsilon: float):
    return Template("privacy_loss").fill_values(EPSILON=epsilon).finish()


def make_column_config_block(
    name: str, lower_bound: float, upper_bound: float, bin_count: int
):
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
        .finish()
    )


# Private helper functions:
# These do not depend on the AnalysisPlan,
# so it's better to keep them out of the class.


def _snake_case(name: str):
    """
    >>> _snake_case("HW GRADE")
    'hw_grade'
    >>> _snake_case("123")
    '_123'
    """
    snake = re.sub(r"\W+", "_", name.lower())
    # TODO: More validation in UI so we don't get zero-length strings.
    if snake == "" or not re.match(r"[a-z]", snake[0]):
        snake = f"_{snake}"
    return snake


def _make_imports():
    return (
        Template("imports").fill_values().finish()
        + (Path(__file__).parent.parent / "shared.py").read_text()
    )
