from abc import ABC, abstractmethod
from datetime import datetime
from math import gcd
from pathlib import Path
from typing import Iterable

from dp_wizard_templates.code_template import Template

from dp_wizard import __version__, get_template_root, opendp_version
from dp_wizard.types import ColumnIdentifier, Product
from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    make_column_config_block,
    make_privacy_loss_block,
    make_privacy_unit_block,
)
from dp_wizard.utils.code_generators.analyses import count, histogram
from dp_wizard.utils.dp_helper import confidence
from dp_wizard.utils.shared import make_cut_points

root = get_template_root(__file__)


def _analysis_has_bounds(analysis) -> bool:
    return analysis.analysis_name != count.name


class AbstractGenerator(ABC):
    def __init__(self, analysis_plan: AnalysisPlan):
        self.analysis_plan = analysis_plan

    def _get_synth_or_stats(self) -> str:
        match self.analysis_plan.product:
            case Product.STATISTICS:
                return "stats"
            case Product.SYNTHETIC_DATA:
                return "synth"
            case _:  # pragma: no cover
                raise ValueError(self.analysis_plan.product)

    def _get_extra(self) -> str:
        # Notebooks shouldn't depend on mbi if they don't need it.
        # (DP Wizard itself will require mbi, because it needs
        # to be able to execute both kinds of notebooks.)
        match self.analysis_plan.product:
            case Product.STATISTICS:
                return "polars"
            case Product.SYNTHETIC_DATA:
                return "mbi"
            case _:  # pragma: no cover
                raise ValueError(self.analysis_plan.product)

    @abstractmethod
    def _get_notebook_or_script(self) -> str: ...  # pragma: no cover

    def _get_root_template(self) -> str:
        adj = self._get_synth_or_stats()
        noun = self._get_notebook_or_script()
        return f"{adj}_{noun}"

    @abstractmethod
    def _make_stats_context(self) -> str: ...  # pragma: no cover

    @abstractmethod
    def _make_extra_blocks(self) -> dict[str, str]: ...  # pragma: no cover

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

        extra = self._get_extra()

        code = (
            Template(self._get_root_template(), root)
            .fill_expressions(
                TITLE=str(self.analysis_plan),
                DEPENDENCIES=f"'opendp[{extra}]=={opendp_version}' matplotlib",
                DP_WIZARD_V_VERSION=f"v{__version__}",
                DATE_TIME=datetime.now().strftime("%b %d, %Y at %I:%M%p"),
            )
            .fill_code_blocks(
                IMPORTS_BLOCK=Template(template).finish(),
                UTILS_BLOCK=(Path(__file__).parent.parent / "shared.py").read_text(),
                **self._make_extra_blocks(),
            )
            .fill_comment_blocks(
                WINDOWS_COMMENT_BLOCK="""
(If installing in the Windows CMD shell,
use double-quotes instead of single-quotes below.)""",
                ENCODING_COMMENT_BLOCK="""
A note on `utf8-lossy`: CSVs can use different "character encodings" to
represent characters outside the ASCII character set, but out-of-the-box
the Polars library only supports UTF8. Specifying `utf8-lossy` preserves as
much information as possible, and any unrecognized characters will be replaced
by "�". If this is not sufficient, you will need to preprocess your data to
reencode it as UTF8.""",
            )
            .finish()
        )
        return self._clean_up_py(code)

    def _clean_up_py(self, py: str):
        return py

    def _make_margins_list(
        self,
        bin_names: Iterable[str],
        groups: Iterable[str],
        max_rows: int,
    ):
        import opendp.prelude as dp

        def basic_template(GROUPS, MAX_ROWS):
            # "max_partition_length" should be a loose upper bound,
            # for example, the size of the total population being sampled.
            # https://docs.opendp.org/en/OPENDP_V_VERSION/api/python/opendp.extras.polars.html#opendp.extras.polars.Margin.max_partition_length
            #
            # In production, "max_groups" should be set by considering
            # the number of possible values for each grouping column,
            # and taking their product.
            dp.polars.Margin(
                by=GROUPS,
                invariant="keys",
                max_length=MAX_ROWS,
                max_groups=100,
            )

        def bin_template(GROUPS, BIN_NAME):
            dp.polars.Margin(by=([BIN_NAME] + GROUPS), invariant="keys")

        margins = [
            Template(basic_template)
            .fill_expressions(OPENDP_V_VERSION=f"v{opendp_version}")
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

    def _make_stats_queries(self):
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

    def _make_partial_synth_context(self):
        privacy_unit_block = make_privacy_unit_block(
            contributions=self.analysis_plan.contributions,
            contributions_entity=self.analysis_plan.contributions_entity,
        )
        # If there are no groups and all analyses have bounds (so we have cut points),
        # then OpenDP requires that pure DP be used for contingency tables.

        privacy_loss_block = make_privacy_loss_block(
            pure=not self.analysis_plan.groups
            and all(
                _analysis_has_bounds(analyses[0])
                for analyses in self.analysis_plan.columns.values()
            ),
            epsilon=self.analysis_plan.epsilon,
            max_rows=self.analysis_plan.max_rows,
        )
        return (
            Template("synth_context", root)
            .fill_expressions(
                OPENDP_V_VERSION=f"v{opendp_version}",
            )
            .fill_code_blocks(
                PRIVACY_UNIT_BLOCK=privacy_unit_block,
                PRIVACY_LOSS_BLOCK=privacy_loss_block,
            )
        )

    def _make_synth_query(self):
        def template(synth_context, COLUMNS, CUTS):
            synth_query = (
                synth_context.query()
                .select(COLUMNS)
                .contingency_table(
                    # Numeric columns will generally require cut points,
                    # unless they contain only a few distinct values.
                    cuts=CUTS,
                    # If you know the possible values for particular columns,
                    # supply them here to use your privacy budget more efficiently:
                    # keys={"your_column": ["known_value"]},
                )
            )
            contingency_table = synth_query.release()

            # Calling
            # [`project_melted()`](https://docs.opendp.org/en/OPENDP_V_VERSION/api/python/opendp.extras.mbi.html#opendp.extras.mbi.ContingencyTable.project_melted)
            # returns a dataframe with one row per combination of values.
            # We'll first check the number of possible rows,
            # to make sure it's not too large:

            # +
            from math import prod

            possible_rows = prod([len(v) for v in contingency_table.keys.values()])
            (
                contingency_table.project_melted([COLUMNS])
                if possible_rows < 100_000
                else "Too big!"
            )
            # -

            # Finally, a contingency table can also be used
            # to create synthetic data by calling
            # [`synthesize()`](https://docs.opendp.org/en/OPENDP_V_VERSION/api/python/opendp.extras.mbi.html#opendp.extras.mbi.ContingencyTable.synthesize).
            # (There may be warnings from upstream libraries
            # which we can ignore for now.)

            # +
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter(action="ignore", category=FutureWarning)
                synthetic_data = contingency_table.synthesize()
            synthetic_data  # type: ignore
            # -

        # The make_cut_points() call could be moved into generated code,
        # but that would require more complex templating,
        # and more reliance on helper functions.
        cuts = {
            k: sorted(
                {
                    # TODO: Error if float cut points are used with integer data.
                    # Is an upstream fix possible?
                    # (Sort the set because we might get int collisions,
                    # and repeated cut points are also an error.)
                    int(x)
                    for x in make_cut_points(
                        lower_bound=int(v[0].lower_bound),
                        upper_bound=int(v[0].upper_bound),
                        # bin_count is not set for mean: default to 10.
                        bin_count=v[0].bin_count or 10,
                    )
                }
            )
            for (k, v) in self.analysis_plan.columns.items()
            if _analysis_has_bounds(v[0])
        }
        return (
            Template(template)
            .fill_expressions(
                OPENDP_V_VERSION=f"v{opendp_version}",
                COLUMNS=", ".join(
                    repr(k)
                    for k in (
                        list(self.analysis_plan.columns.keys())
                        + self.analysis_plan.groups
                    )
                ),
            )
            .fill_values(
                CUTS=cuts,
            )
            .finish()
        )
