from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    make_column_config_block,
    make_privacy_loss_block,
    make_privacy_unit_block,
)
from dp_wizard.utils.code_generators.analyses import histogram
from dp_wizard.utils.code_template import Template
from dp_wizard.utils.csv_helper import name_to_identifier
from dp_wizard.utils.dp_helper import confidence


import black


from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable


class AbstractGenerator(ABC):
    root_template = "placeholder"

    def __init__(self, analysis_plan: AnalysisPlan):
        self.analysis_plan = analysis_plan

    @abstractmethod
    def _make_context(self) -> str: ...  # pragma: no cover

    def _make_extra_blocks(self):
        return {}

    def _make_python_cell(self, block) -> str:
        """
        Default to just pass through.
        """
        return block

    def _make_comment_cell(self, comment: str) -> str:
        return "".join(f"# {line}\n" for line in comment.splitlines())

    def make_py(self):
        code = (
            Template(self.root_template, __file__)
            .fill_expressions(
                TITLE=str(self.analysis_plan),
                DEPENDENCIES="'opendp[polars]==0.13.0' matplotlib",
            )
            .fill_blocks(
                IMPORTS_BLOCK=Template("imports", __file__).finish(),
                UTILS_BLOCK=(Path(__file__).parent.parent / "shared.py").read_text(),
                COLUMNS_BLOCK=self._make_columns(),
                CONTEXT_BLOCK=self._make_context(),
                QUERIES_BLOCK=self._make_queries(),
                **self._make_extra_blocks(),
            )
            .finish()
        )
        # Line length determined by PDF rendering.
        return black.format_str(code, mode=black.Mode(line_length=74))  # type: ignore

    def _make_margins_list(self, bin_names: Iterable[str], groups: Iterable[str]):
        groups_str = ", ".join(f"'{g}'" for g in groups)
        margins = (
            [
                f"""
            # "max_partition_length" should be a loose upper bound,
            # for example, the size of the total population being sampled.
            # https://docs.opendp.org/en/stable/api/python/opendp.extras.polars.html#opendp.extras.polars.Margin.max_partition_length
            #
            # In production, "max_num_partitions" should be set by considering the number
            # of possible values for each grouping column, and taking their product.
            dp.polars.Margin(by=[{groups_str}], public_info='keys', max_partition_length=1000000, max_num_partitions=100),
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

    @abstractmethod
    def _make_columns(self) -> str: ...  # pragma: no cover

    def _make_column_config_dict(self):
        return {
            name: make_column_config_block(
                name=name,
                analysis_type=col[0].analysis_type,
                lower_bound=col[0].lower_bound,
                upper_bound=col[0].upper_bound,
                bin_count=col[0].bin_count,
            )
            for name, col in self.analysis_plan.columns.items()
        }

    def _make_confidence_note(self):
        return f"{int(confidence * 100)}% confidence interval"

    def _make_queries(self):
        to_return = [
            self._make_python_cell(
                f"confidence = {confidence} # {self._make_confidence_note()}"
            )
        ]
        for column_name in self.analysis_plan.columns.keys():
            to_return.append(self._make_query(column_name))

        return "\n".join(to_return)

    def _make_query(self, column_name):
        plan = self.analysis_plan.columns[column_name]
        identifier = name_to_identifier(column_name)
        accuracy_name = f"{identifier}_accuracy"
        stats_name = f"{identifier}_stats"

        from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

        analysis = get_analysis_by_name(plan[0].analysis_type)
        query = analysis.make_query(
            code_gen=self,
            identifier=identifier,
            accuracy_name=accuracy_name,
            stats_name=stats_name,
        )
        output = analysis.make_output(
            code_gen=self,
            column_name=column_name,
            accuracy_name=accuracy_name,
            stats_name=stats_name,
        )

        return (
            self._make_comment_cell(f"### Query for `{column_name}`:")
            + self._make_python_cell(query)
            + self._make_python_cell(output)
        )

    def _make_partial_context(self):
        weights = [column[0].weight for column in self.analysis_plan.columns.values()]

        from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

        bin_column_names = [
            name_to_identifier(name)
            for name, plan in self.analysis_plan.columns.items()
            if get_analysis_by_name(plan[0].analysis_type).has_bins()
        ]

        privacy_unit_block = make_privacy_unit_block(self.analysis_plan.contributions)
        privacy_loss_block = make_privacy_loss_block(self.analysis_plan.epsilon)

        is_just_histograms = all(
            plan_column[0].analysis_type == histogram.name
            for plan_column in self.analysis_plan.columns.values()
        )
        margins_list = (
            # Histograms don't need margins.
            "[]"
            if is_just_histograms
            else self._make_margins_list(
                [f"{name}_bin" for name in bin_column_names],
                self.analysis_plan.groups,
            )
        )
        extra_columns = ", ".join(
            [
                f"{name_to_identifier(name)}_bin_expr"
                for name, plan in self.analysis_plan.columns.items()
                if get_analysis_by_name(plan[0].analysis_type).has_bins()
            ]
        )
        return (
            Template("context", __file__)
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
