from pathlib import Path

from dp_wizard_templates.code_template import Template

from dp_wizard import opendp_version
from dp_wizard.types import ColumnIdentifier
from dp_wizard.utils.code_generators import (
    make_privacy_loss_block,
    make_privacy_unit_block,
)
from dp_wizard.utils.code_generators.analyses import (
    histogram,
)
from dp_wizard.utils.code_generators.base_generators._base_generator import (
    BaseGenerator,
    confidence,
)

root = Path(__file__).parent.parent / "no-tests"


class StatsGenerator(BaseGenerator):

    def _make_stats_queries(self):
        to_return = [
            self._make_python_cell(
                f"confidence = {confidence} # {self._make_confidence_note()}"
            )
        ]
        for column_name in self.analysis_plan.columns.keys():
            to_return.append(self._make_query(column_name))

        return "\n".join(to_return)

    def _make_partial_stats_context(self):

        from dp_wizard.utils.code_generators.analyses import (
            get_analysis_by_name,
            has_bins,
        )

        bin_column_names = [
            ColumnIdentifier(name)
            for name, plan in self.analysis_plan.columns.items()
            if has_bins(get_analysis_by_name(plan[0].analysis_name))
        ]

        privacy_unit_block = make_privacy_unit_block(
            contributions=self.analysis_plan.contributions,
            contributions_entity=self.analysis_plan.contributions_entity,
        )
        privacy_loss_block = make_privacy_loss_block(
            pure=False,
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
                if has_bins(get_analysis_by_name(plan[0].analysis_name))
            ]
        )
        return (
            Template("stats_context", root)
            .fill_expressions(
                MARGINS_LIST=margins_list,
                EXTRA_COLUMNS=extra_columns,
                OPENDP_V_VERSION=f"v{opendp_version}",
                WEIGHTS=self._make_weights_expression(),
            )
            .fill_code_blocks(
                PRIVACY_UNIT_BLOCK=privacy_unit_block,
                PRIVACY_LOSS_BLOCK=privacy_loss_block,
            )
        )
