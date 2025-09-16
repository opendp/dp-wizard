from dp_wizard.utils.code_generators.abstract_generator import AbstractGenerator


class ScriptGenerator(AbstractGenerator):
    def _get_notebook_or_script(self):
        return "script"

    def _make_columns(self):
        column_config_dict = self._make_column_config_dict()
        return "\n".join(
            f"# Expression for `{name}`\n{block}"
            for name, block in column_config_dict.items()
        )

    def _make_stats_context(self):
        return (
            self._make_partial_stats_context()
            .fill_expressions(CSV_PATH="csv_path")
            .fill_blocks(OPTIONAL_CSV_BLOCK="")
            .finish()
        )

    def _make_synth_context(self):
        return (
            self._make_partial_synth_context()
            .fill_expressions(CSV_PATH="csv_path")
            .fill_blocks(OPTIONAL_CSV_BLOCK="")
            .finish()
        )

    def _make_confidence_note(self):
        # In the superclass, the string is unquoted so it can be
        # used in comments: It needs to be wrapped here.
        return repr(super()._make_confidence_note())

    def _make_extra_blocks(self):
        if self.analysis_plan.is_synthetic_data:
            return {
                "SYNTH_CONTEXT_BLOCK": self._make_synth_context(),
                "SYNTH_QUERY_BLOCK": self._make_synth_query(),
            }
        else:
            return {
                "COLUMNS_BLOCK": self._make_columns(),
                "STATS_CONTEXT_BLOCK": self._make_stats_context(),
                "STATS_QUERIES_BLOCK": self._make_stats_queries(),
            }
