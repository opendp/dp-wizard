from dp_wizard.utils.code_generators.abstract_generator import AbstractGenerator


class ScriptGenerator(AbstractGenerator):
    root_template = "script"

    def _make_columns(self):
        column_config_dict = self._make_column_config_dict()
        return "\n".join(
            f"# Expression for `{name}`\n{block}"
            for name, block in column_config_dict.items()
        )

    def _make_context(self):
        return (
            self._make_partial_context().fill_expressions(CSV_PATH="csv_path").finish()
        )

    def _make_confidence_note(self):
        # In the superclass, the string is unquoted so it can be
        # used in comments: It needs to be wrapped here.
        return repr(super()._make_confidence_note())
