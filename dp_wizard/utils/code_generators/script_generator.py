import re

from dp_wizard.types import Product
from dp_wizard.utils.code_generators.abstract_generator import AbstractGenerator


def _remove_jupytext(py: str):
    """
    Remove jupytext light annotations that are only used for notebook generation.

    >>> py_src = '''
    ... # + tags=["this is removed"]
    ... # Comment stays
    ... Code stays
    ... # -
    ... # - Line above is removed, but this could be a list item.
    ... '''.strip()
    >>> print(_remove_jupytext(py_src))
    <BLANKLINE>
    # Comment stays
    Code stays
    <BLANKLINE>
    # - Line above is removed, but this could be a list item.
    """
    # The output is passed through black,
    # so don't worry about formatting of output.
    py = re.sub(r"# \+.*", "", py)
    py = re.sub(r"# -$", "", py, flags=re.MULTILINE)
    return py


class ScriptGenerator(AbstractGenerator):
    def _get_notebook_or_script(self):
        return "script"

    def _clean_up_py(self, py: str):
        return _remove_jupytext(py)

    def _make_columns(self):
        column_config_dict = self._make_column_config_dict()
        return "\n".join(
            f"# Expression for `{name}`\n{block}"
            for name, block in column_config_dict.items()
        )

    def _make_stats_context(self):
        return (
            self._make_partial_stats_context()
            .fill_expressions(CSV_PATH="path")
            .fill_blocks(OPTIONAL_CSV_BLOCK="", OPTIONAL_CONVERT_TO_CSV_BLOCK="")
            .finish()
        )

    def _make_synth_context(self):
        return (
            self._make_partial_synth_context()
            .fill_expressions(CSV_PATH="path")
            .fill_blocks(OPTIONAL_CSV_BLOCK="", OPTIONAL_CONVERT_TO_CSV_BLOCK="")
            .finish()
        )

    def _make_confidence_note(self):
        # In the superclass, the string is unquoted so it can be
        # used in comments: It needs to be wrapped here.
        return repr(super()._make_confidence_note())

    def _make_extra_blocks(self):
        match self.analysis_plan.product:
            case Product.SYNTHETIC_DATA:
                return {
                    "SYNTH_CONTEXT_BLOCK": self._make_synth_context(),
                    "SYNTH_QUERY_BLOCK": self._make_synth_query(),
                }
            case Product.STATISTICS:
                return {
                    "COLUMNS_BLOCK": self._make_columns(),
                    "STATS_CONTEXT_BLOCK": self._make_stats_context(),
                    "STATS_QUERIES_BLOCK": self._make_stats_queries(),
                }
            case _:  # pragma: no cover
                raise ValueError(self.analysis_plan.product)
