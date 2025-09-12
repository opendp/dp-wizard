from pathlib import Path

from dp_wizard_templates.code_template import Template

from dp_wizard.types import ColumnIdentifier
from dp_wizard.utils.code_generators.abstract_generator import (
    AbstractGenerator,
    get_template_root,
)
from dp_wizard.utils.dp_helper import confidence

PLACEHOLDER_CSV_NAME = "fill-in-correct-path.csv"

root = get_template_root(__file__)


class NotebookGenerator(AbstractGenerator):
    def _get_notebook_or_script(self):
        return "notebook"

    def _make_stats_context(self):
        return self._fill_partial_context(self._make_partial_stats_context())

    def _make_synth_context(self):
        return self._fill_partial_context(self._make_partial_synth_context())

    def _fill_partial_context(self, partial_context):
        placeholder_csv_content = ",".join(self.analysis_plan.columns)
        return (
            partial_context.fill_values(
                CSV_PATH=self.analysis_plan.csv_path,
            )
            .fill_blocks(
                OPTIONAL_CSV_BLOCK=(
                    "# Write to placeholder CSV so the notebook can still execute:\n"
                    "from pathlib import Path\n"
                    f"Path('{PLACEHOLDER_CSV_NAME}').write_text('{placeholder_csv_content}')\n"
                    if self.analysis_plan.csv_path == PLACEHOLDER_CSV_NAME
                    else ""
                )
            )
            .finish()
        )

    def _make_python_cell(self, block):
        return f"\n# +\n{block}\n# -\n"

    def _make_columns(self):
        column_config_dict = self._make_column_config_dict()
        return "\n".join(
            f"# ### Expression for `{name}`\n{self._make_python_cell(block)}"
            for name, block in column_config_dict.items()
        )

    def _make_report_kv(self, name, analysis_type):
        from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

        analysis = get_analysis_by_name(analysis_type)
        return analysis.make_report_kv(
            name=name, confidence=confidence, identifier=ColumnIdentifier(name)
        )

    def _make_reports_block(self):
        def template(synthetic_data):
            {  # noqa: B018: Allow useless dict
                "columns": synthetic_data.columns,
                "rows": [list(row) for row in synthetic_data.rows()],
            }  # type: ignore

        outputs_expression = (
            Template(template).finish()
            if self.analysis_plan.is_synthetic_data
            else (
                "{"
                + ",".join(
                    self._make_report_kv(name, plan[0].analysis_name)
                    for name, plan in self.analysis_plan.columns.items()
                )
                + "}"
            )
        )
        tmp_path = Path(__file__).parent.parent.parent / "tmp"
        reports_block = (
            Template(f"{self._get_synth_or_stats()}_reports", root)
            .fill_expressions(
                OUTPUTS=outputs_expression,
                COLUMNS={
                    k: v[0]._asdict() for k, v in self.analysis_plan.columns.items()
                },
            )
            .fill_values(
                CSV_PATH=self.analysis_plan.csv_path,
                EPSILON=self.analysis_plan.epsilon,
                TXT_REPORT_PATH=str(tmp_path / "report.txt"),
                CSV_REPORT_PATH=str(tmp_path / "report.csv"),
            )
            .finish()
        )
        return reports_block

    def _make_extra_blocks(self):
        if self.analysis_plan.is_synthetic_data:
            return {
                "SYNTH_CONTEXT_BLOCK": self._make_synth_context(),
                "SYNTH_QUERY_BLOCK": self._make_synth_query(),
                "SYNTH_REPORTS_BLOCK": self._make_reports_block(),
            }
        else:
            return {
                "COLUMNS_BLOCK": self._make_columns(),
                "STATS_CONTEXT_BLOCK": self._make_stats_context(),
                "STATS_QUERIES_BLOCK": self._make_stats_queries(),
                "STATS_REPORTS_BLOCK": self._make_reports_block(),
            }
