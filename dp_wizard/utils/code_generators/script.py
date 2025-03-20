from dp_wizard.utils.code_generators.abc import CodeGenerator


class ScriptGenerator(CodeGenerator):
    root_template = "script"

    def _make_context(self):
        return (
            self._make_partial_context().fill_expressions(CSV_PATH="csv_path").finish()
        )

    def _make_confidence_note(self):
        # In the superclass, the string is unquoted so it can be
        # used in comments: It needs to be wrapped here.
        return repr(super()._make_confidence_note())
