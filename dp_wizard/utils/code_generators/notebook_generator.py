from dp_wizard.utils.code_generators.abstract_generator import AbstractGenerator
from dp_wizard.utils.code_template import Template
from dp_wizard.utils.csv_helper import name_to_identifier
from dp_wizard.utils.dp_helper import confidence


from pathlib import Path

PLACEHOLDER_CSV_NAME = "fill-in-correct-path.csv"


class NotebookGenerator(AbstractGenerator):
    root_template = "notebook"

    def _make_context(self):
        placeholder_csv_content = ",".join(self.analysis_plan.columns)
        return (
            self._make_partial_context()
            .fill_values(
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
            name=name, confidence=confidence, identifier=name_to_identifier(name)
        )

    def _make_extra_blocks(self):
        outputs_expression = (
            "{"
            + ",".join(
                self._make_report_kv(name, plan[0].analysis_type)
                for name, plan in self.analysis_plan.columns.items()
            )
            + "}"
        )
        tmp_path = Path(__file__).parent.parent.parent / "tmp"
        reports_block = (
            Template("reports", __file__)
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
                HTML_REPORT_PATH=str(tmp_path / "report.html"),
            )
            .finish()
        )
        return {"REPORTS_BLOCK": reports_block}
