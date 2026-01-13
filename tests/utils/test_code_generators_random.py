import warnings

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dp_wizard import package_root
from dp_wizard.types import ColumnName, Product
from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.code_generators.analyses import mean
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


@settings(
    deadline=None,
    # Not sure, but I think the abundance of range bounds
    # is the cause of this warning.
    suppress_health_check=[HealthCheck.filter_too_much],
)
@given(
    bin_count=st.integers(),
    epsilon=st.floats(min_value=MIN_EPSILON, max_value=MAX_EPSILON),
    lower_upper=st.tuples(good_floats, good_floats).filter(
        lambda l_u: MIN_BOUND <= l_u[0] < l_u[1] <= MAX_BOUND
    ),
    max_rows=st.integers(min_value=MIN_ROW_COUNT, max_value=MAX_ROW_COUNT),
    contributions=st.integers(min_value=1, max_value=MAX_CONTRIBUTIONS),
    # All-caps string from user could be confused for slot:
    # TODO: https://github.com/opendp/dp-wizard/issues/796
    # notebook_note=good_strings,
)
def test_make_random_notebook(bin_count, epsilon, lower_upper, max_rows, contributions):
    lower_bound, upper_bound = lower_upper
    mean_plan_column = AnalysisPlanColumn(
        statistic_name=mean.name,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        bin_count=bin_count,  # Unused by mean
        weight=4,
    )
    plan = AnalysisPlan(
        product=Product.STATISTICS,
        groups={},
        columns={ColumnName("2B"): [mean_plan_column]},
        contributions=contributions,
        contributions_entity="PLACEHOLDER",  # TODO: enum?
        csv_path=abc_csv_path,
        epsilon=epsilon,
        max_rows=max_rows,
    )
    notebook_py = NotebookGenerator(plan, "PLACEHOLDER").make_py(reformat=True)
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
