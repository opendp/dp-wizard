from pathlib import Path

from dp_wizard_templates.code_template import Template

from dp_wizard import opendp_version
from dp_wizard.utils.code_generators import (
    make_privacy_loss_block,
    make_privacy_unit_block,
)
from dp_wizard.utils.code_generators.base_generators._base_generator import (
    BaseGenerator,
    _analysis_has_bounds,
)
from dp_wizard.utils.shared import make_cut_points

root = Path(__file__).parent.parent / "no-tests"


class SynthGenerator(BaseGenerator):
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
