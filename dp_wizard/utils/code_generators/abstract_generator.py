from abc import ABC, abstractmethod
from math import gcd
from pathlib import Path
from typing import Iterable

from dp_wizard_templates.code_template import Template

from dp_wizard import get_template_root, opendp_version
from dp_wizard.types import ColumnIdentifier
from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    make_column_config_block,
    make_privacy_loss_block,
    make_privacy_unit_block,
)
from dp_wizard.utils.code_generators.analyses import histogram
from dp_wizard.utils.dp_helper import confidence

root = get_template_root(__file__)


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
        def template():
            import matplotlib.pyplot as plt  # noqa: F401
            import opendp.prelude as dp  # noqa: F401
            import polars as pl  # noqa: F401

            # The OpenDP team is working to vet the core algorithms.
            # Until that is complete we need to opt-in to use these features.
            dp.enable_features("contrib")

        code = (
            Template(self.root_template, root)
            .fill_expressions(
                TITLE=str(self.analysis_plan),
                WINDOWS_NOTE="(If installing in the Windows CMD shell, "
                "use double-quotes instead of single-quotes below.)",
                DEPENDENCIES=f"'opendp[polars]=={opendp_version}' matplotlib",
            )
            .fill_blocks(
                IMPORTS_BLOCK=Template(template).finish(),
                UTILS_BLOCK=(Path(__file__).parent.parent / "shared.py").read_text(),
                COLUMNS_BLOCK=self._make_columns(),
                CONTEXT_BLOCK=self._make_context(),
                QUERIES_BLOCK=self._make_queries(),
                **self._make_extra_blocks(),
            )
            .finish()
        )
        return code

    def _make_margins_list(
        self,
        bin_names: Iterable[str],
        groups: Iterable[str],
        max_rows: int,
    ):
        import opendp.prelude as dp

        def basic_template(GROUPS, OPENDP_VERSION, MAX_ROWS):
            # "max_partition_length" should be a loose upper bound,
            # for example, the size of the total population being sampled.
            # https://docs.opendp.org/en/OPENDP_VERSION/api/python/opendp.extras.polars.html#opendp.extras.polars.Margin.max_partition_length
            #
            # In production, "max_num_partitions" should be set by considering
            # the number of possible values for each grouping column,
            # and taking their product.
            dp.polars.Margin(
                by=GROUPS,
                public_info="keys",
                max_partition_length=MAX_ROWS,
                max_num_partitions=100,
            )

        def bin_template(GROUPS, BIN_NAME):
            dp.polars.Margin(by=([BIN_NAME] + GROUPS), public_info="keys")

        margins = [
            Template(basic_template)
            .fill_expressions(OPENDP_VERSION=opendp_version)
            .fill_values(GROUPS=groups, MAX_ROWS=max_rows)
            .finish()
        ] + [
            Template(bin_template)
            .fill_values(GROUPS=groups, BIN_NAME=bin_name)
            .finish()
            for bin_name in bin_names
        ]

        margins_list = "[" + ", ".join(margins) + "\n    ]"
        return margins_list

    @abstractmethod
    def _make_columns(self) -> str: ...  # pragma: no cover

    def _make_column_config_dict(self):
        return {
            name: make_column_config_block(
                name=name,
                analysis_name=col[0].analysis_name,
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
        identifier = ColumnIdentifier(column_name)
        accuracy_name = f"{identifier}_accuracy"
        stats_name = f"{identifier}_stats"

        from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

        analysis = get_analysis_by_name(plan[0].analysis_name)
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
        note = analysis.make_note()

        return (
            self._make_comment_cell(f"### Query for `{column_name}`:")
            + self._make_python_cell(query)
            + self._make_python_cell(output)
            + (self._make_comment_cell(note) if note else "")
        )

    def _make_weights_expression(self):
        weights_dict = {
            name: plans[0].weight for name, plans in self.analysis_plan.columns.items()
        }
        weights_message = (
            "Allocate the privacy budget to your queries in this ratio:"
            if len(weights_dict) > 1
            else "With only one query, the entire budget is allocated to that query:"
        )
        weights_gcd = gcd(*(weights_dict.values()))
        return (
            f"[ # {weights_message}\n"
            + "".join(
                f"{weight//weights_gcd}, # {name}\n"
                for name, weight in weights_dict.items()
            )
            + "]"
        )

    def _make_partial_context(self):

        from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

        bin_column_names = [
            ColumnIdentifier(name)
            for name, plan in self.analysis_plan.columns.items()
            if get_analysis_by_name(plan[0].analysis_name).has_bins
        ]

        privacy_unit_block = make_privacy_unit_block(self.analysis_plan.contributions)
        privacy_loss_block = make_privacy_loss_block(
            epsilon=self.analysis_plan.epsilon,
            max_rows=self.analysis_plan.max_rows,
        )

        is_just_histograms = all(
            plan_column[0].analysis_name == histogram.name
            for plan_column in self.analysis_plan.columns.values()
        )
        margins_list = (
            # Histograms don't need margins.
            "[]"
            if is_just_histograms
            else self._make_margins_list(
                bin_names=[f"{name}_bin" for name in bin_column_names],
                groups=self.analysis_plan.groups,
                max_rows=self.analysis_plan.max_rows,
            )
        )
        extra_columns = ", ".join(
            [
                f"{ColumnIdentifier(name)}_bin_expr"
                for name, plan in self.analysis_plan.columns.items()
                if get_analysis_by_name(plan[0].analysis_name).has_bins
            ]
        )
        return (
            Template("context", root)
            .fill_expressions(
                MARGINS_LIST=margins_list,
                EXTRA_COLUMNS=extra_columns,
                OPENDP_VERSION=opendp_version,
                WEIGHTS=self._make_weights_expression(),
            )
            .fill_blocks(
                PRIVACY_UNIT_BLOCK=privacy_unit_block,
                PRIVACY_LOSS_BLOCK=privacy_loss_block,
            )
        )
