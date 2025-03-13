from typing import NamedTuple, Optional, Iterable
from abc import ABC, abstractmethod
from pathlib import Path
import re

import black

from dp_wizard import AnalysisType
from dp_wizard.utils.csv_helper import name_to_identifier
from dp_wizard.utils.code_generators._template import Template
from dp_wizard.utils.dp_helper import confidence


class AnalysisPlanColumn(NamedTuple):
    analysis_type: str
    lower_bound: float
    upper_bound: float
    bin_count: int
    weight: int


class AnalysisPlan(NamedTuple):
    csv_path: Optional[str]
    contributions: int
    epsilon: float
    groups: list[str]
    columns: dict[str, AnalysisPlanColumn]


class _CodeGenerator(ABC):
    root_template = "placeholder"

    def __init__(self, analysis_plan: AnalysisPlan):
        self.csv_path = analysis_plan.csv_path
        self.contributions = analysis_plan.contributions
        self.epsilon = analysis_plan.epsilon
        self.groups = analysis_plan.groups
        self.columns = analysis_plan.columns

    @abstractmethod
    def _make_context(self) -> str: ...  # pragma: no cover

    def _make_extra_blocks(self):
        return {}

    def _make_cell(self, block) -> str:
        """
        For the script generator, this is just a pass through.
        """
        return block

    def make_py(self):
        code = (
            Template(self.root_template)
            .fill_expressions(
                DEPENDENCIES="'opendp[polars]==0.12.1a20250227001' matplotlib"
            )
            .fill_blocks(
                IMPORTS_BLOCK=Template("imports").finish(),
                UTILS_BLOCK=(Path(__file__).parent.parent / "shared.py").read_text(),
                COLUMNS_BLOCK=self._make_columns(),
                CONTEXT_BLOCK=self._make_context(),
                QUERIES_BLOCK=self._make_queries(),
                **self._make_extra_blocks(),
            )
            .finish()
        )
        # Line length determined by PDF rendering.
        return black.format_str(code, mode=black.Mode(line_length=74))

    def _make_margins_list(self, bin_names: Iterable[str], groups: Iterable[str]):
        groups_str = ", ".join(f"'{g}'" for g in groups)
        margins = (
            [
                f"""
            # "max_partition_length" should be a loose upper bound,
            # for example, the size of the total population being sampled.
            # https://docs.opendp.org/en/stable/api/python/opendp.extras.polars.html#opendp.extras.polars.Margin.max_partition_length
            dp.polars.Margin(by=[{groups_str}], public_info='lengths', max_partition_length=1000000, max_num_partitions=100),
            """  # noqa: B950 (too long!)
            ]
            + [
                f"dp.polars.Margin(by=['{bin_name}', {groups_str}], "
                "public_info='keys',),"
                for bin_name in bin_names
            ]
        )

        margins_list = "[" + "".join(margins) + "\n    ]"
        return margins_list

    def _make_columns(self):
        return "\n".join(
            make_column_config_block(
                name=name,
                analysis_type=col.analysis_type,
                lower_bound=col.lower_bound,
                upper_bound=col.upper_bound,
                bin_count=col.bin_count,
            )
            for name, col in self.columns.items()
        )

    def _make_confidence_note(self):
        return f"{int(confidence * 100)}% confidence interval"

    def _make_queries(self):
        to_return = [
            self._make_cell(
                f"confidence = {confidence} # {self._make_confidence_note()}"
            )
        ]
        for column_name in self.columns.keys():
            to_return.append(self._make_query(column_name))

        return "\n".join(to_return)

    def _make_query(self, column_name):
        plan = self.columns[column_name]
        identifier = name_to_identifier(column_name)
        accuracy_name = f"{identifier}_accuracy"
        stats_name = f"{identifier}_stats"

        match plan.analysis_type:
            case AnalysisType.HISTOGRAM:
                query = (
                    Template("histogram_query")
                    .fill_values(
                        BIN_NAME=f"{identifier}_bin",
                        GROUP_NAMES=self.groups,
                    )
                    .fill_expressions(
                        QUERY_NAME=f"{identifier}_query",
                        ACCURACY_NAME=accuracy_name,
                        STATS_NAME=stats_name,
                    )
                    .finish()
                )
            case AnalysisType.MEAN:  # pragma: no cover
                query = (
                    Template("mean_query")
                    .fill_values(
                        GROUP_NAMES=self.groups,
                    )
                    .fill_expressions(
                        QUERY_NAME=f"{identifier}_query",
                        STATS_NAME=stats_name,
                        CONFIG_NAME=f"{identifier}_config",
                    )
                    .finish()
                )
            case _:  # pragma: no cover
                raise Exception("Unrecognized analysis")

        match plan.analysis_type:
            case AnalysisType.HISTOGRAM:
                output = (
                    Template(f"histogram_{self.root_template}_output")
                    .fill_values(
                        COLUMN_NAME=column_name,
                        GROUP_NAMES=self.groups,
                    )
                    .fill_expressions(
                        ACCURACY_NAME=accuracy_name,
                        HISTOGRAM_NAME=stats_name,
                        CONFIDENCE_NOTE=self._make_confidence_note(),
                    )
                    .finish()
                )
            case AnalysisType.MEAN:  # pragma: no cover
                output = Template(f"mean_{self.root_template}_output").finish()
            case _:  # pragma: no cover
                raise Exception("Unrecognized analysis")

        return self._make_cell(query) + self._make_cell(output)

    def _make_partial_context(self):
        weights = [column.weight for column in self.columns.values()]
        bin_column_names = [
            name_to_identifier(name)
            for name, plan in self.columns.items()
            if plan.analysis_type == AnalysisType.HISTOGRAM
        ]

        privacy_unit_block = make_privacy_unit_block(self.contributions)
        privacy_loss_block = make_privacy_loss_block(self.epsilon)

        margins_list = self._make_margins_list(
            [f"{name}_bin" for name in bin_column_names],
            self.groups,
        )
        extra_columns = ", ".join(
            [
                f"{name_to_identifier(name)}_config"
                for name, plan in self.columns.items()
                if plan.analysis_type == AnalysisType.HISTOGRAM
            ]
        )
        return (
            Template("context")
            .fill_expressions(
                MARGINS_LIST=margins_list,
                EXTRA_COLUMNS=extra_columns,
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

    def _make_cell(self, block):
        return f"\n# +\n{block}\n# -\n"

    def _make_report_kv(self, name, analysis_type):
        match analysis_type:
            case AnalysisType.HISTOGRAM:
                return (
                    Template("histogram_report_kv")
                    .fill_values(
                        NAME=name,
                        CONFIDENCE=confidence,
                    )
                    .fill_expressions(
                        IDENTIFIER_STATS=f"{name_to_identifier(name)}_stats",
                        IDENTIFIER_ACCURACY=f"{name_to_identifier(name)}_accuracy",
                    )
                    .finish()
                )
            case AnalysisType.MEAN:  # pragma: no cover
                return (
                    Template("mean_report_kv")
                    .fill_values(
                        NAME=name,
                    )
                    .finish()
                )
            case _:  # pragma: no cover
                raise Exception("Unrecognized analysis")

    def _make_extra_blocks(self):
        outputs_expression = (
            "{"
            + ",".join(
                self._make_report_kv(name, plan.analysis_type)
                for name, plan in self.columns.items()
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
    name: str,
    analysis_type: str,
    lower_bound: float,
    upper_bound: float,
    bin_count: int,
):
    snake_name = _snake_case(name)

    match analysis_type:
        case AnalysisType.HISTOGRAM:
            config = (
                Template("histogram_config")
                .fill_expressions(
                    CUT_LIST_NAME=f"{snake_name}_cut_points",
                    CONFIG_NAME=f"{snake_name}_config",
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
        case AnalysisType.MEAN:
            config = (
                Template("mean_config")
                .fill_expressions(
                    CONFIG_NAME=f"{snake_name}_config",
                )
                .fill_values(
                    COLUMN_NAME=name,
                    LOWER_BOUND=lower_bound,
                    UPPER_BOUND=upper_bound,
                )
                .finish()
            )
        case _:
            raise Exception("Unrecognized analysis")

    return config


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
