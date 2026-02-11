import warnings
from datetime import timedelta

import opendp.prelude as dp
import polars as pl
from hypothesis import HealthCheck, given, note, settings
from hypothesis import strategies as st

from dp_wizard import package_root
from dp_wizard.types import ColumnName, Product
from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.code_generators.analyses import histogram, mean
from dp_wizard.utils.code_generators.notebook_generator import NotebookGenerator
from dp_wizard.utils.constraints import (
    MAX_BOUND,
    MAX_CONTRIBUTIONS,
    MAX_EPSILON,
    MAX_ROW_COUNT,
    MIN_BOUND,
    MIN_EPSILON,
    MIN_ROW_COUNT,
)

abc_csv_path = str((package_root.parent / "tests/fixtures/abc.csv").absolute())

good_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
)

# Without filter we get:
# > ValueError: source code string cannot contain null bytes
#
# It's not feasible for users to supply a null character through a form input,
# so we can filter this out.
# good_strings = st.text().filter(lambda s: "\x00" not in s)


bounds_pair = st.tuples(good_floats, good_floats).filter(
    lambda l_u: MIN_BOUND <= l_u[0] < l_u[1] <= MAX_BOUND
)


@settings(
    # Default is 100 examples.
    max_examples=5,
    # These calculations, particularly synthetic data, are known to be slow.
    deadline=timedelta(seconds=10),
    # Not sure, but I think the abundance of range bounds causes this warning.
    suppress_health_check=[HealthCheck.filter_too_much],
)
@given(
    product=st.sampled_from(Product),
    bin_count=st.integers(min_value=1),
    epsilon=st.floats(min_value=MIN_EPSILON, max_value=MAX_EPSILON),
    histogram_lower_upper=bounds_pair,
    mean_lower_upper=bounds_pair,
    median_lower_upper=bounds_pair,
    max_rows=st.integers(min_value=MIN_ROW_COUNT, max_value=MAX_ROW_COUNT),
    contributions=st.integers(min_value=1, max_value=MAX_CONTRIBUTIONS),
    notebook_note=st.text(
        alphabet=st.characters(
            codec="utf-8",
            # Null character does cause a notebook error, but impossible
            # for user to pass null character through form.
            # https://stackoverflow.com/questions/6961208
            exclude_characters="\x00",
        )
    ),
)
def test_make_random_notebook(
    product,
    bin_count,
    epsilon,
    histogram_lower_upper,
    mean_lower_upper,
    median_lower_upper,
    max_rows,
    contributions,
    notebook_note,
):
    histogram_lower_bound, histogram_upper_bound = histogram_lower_upper
    histogram_plan_column = AnalysisPlanColumn(
        statistic_name=histogram.name,
        lower_bound=histogram_lower_bound,
        upper_bound=histogram_upper_bound,
        bin_count=bin_count,
        weight=4,
    )

    mean_lower_bound, mean_upper_bound = mean_lower_upper
    mean_plan_column = AnalysisPlanColumn(
        statistic_name=mean.name,
        lower_bound=mean_lower_bound,
        upper_bound=mean_upper_bound,
        bin_count=bin_count,  # Unused by mean
        weight=4,
    )

    median_lower_bound, median_upper_bound = median_lower_upper
    median_plan_column = AnalysisPlanColumn(
        statistic_name=mean.name,
        lower_bound=median_lower_bound,
        upper_bound=median_upper_bound,
        bin_count=bin_count,
        weight=4,
    )

    plan = AnalysisPlan(
        product=product,
        groups={},
        analysis_columns={
            ColumnName("1A"): [histogram_plan_column],
            ColumnName("2B"): [mean_plan_column],
            ColumnName("3C"): [median_plan_column],
        },
        schema_columns={
            ColumnName("1A"): pl.Float32(),
            ColumnName("2B"): pl.Float32(),
            ColumnName("3C"): pl.Float32(),
        },
        contributions=contributions,
        contributions_entity="PLACEHOLDER",  # TODO: enum?
        csv_path=abc_csv_path,
        epsilon=epsilon,
        max_rows=max_rows,
    )
    note(f"{plan=}")
    notebook_py = NotebookGenerator(plan, notebook_note).make_py(reformat=True)
    globals = {}

    with warnings.catch_warnings():
        # Ignore future warning and epsilon > 5
        warnings.simplefilter(action="ignore")
        exec(notebook_py, globals)

    # Close plots to avoid this warning:
    # > RuntimeWarning: More than 20 figures have been opened.
    # > Figures created through the pyplot interface (`matplotlib.pyplot.figure`)
    # > are retained until explicitly closed and may consume too much memory.
    import matplotlib.pyplot as plt

    plt.close("all")

    match plan.product:
        case Product.SYNTHETIC_DATA:
            context_global = "synth_context"
        case Product.STATISTICS:
            context_global = "stats_context"
        case _:  # pragma: no cover
            raise ValueError(plan.product)
    assert isinstance(globals[context_global], dp.Context)
