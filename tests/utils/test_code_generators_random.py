from hypothesis import given, settings
from hypothesis import strategies as st

from dp_wizard import package_root
from dp_wizard.types import ColumnName, Product
from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.code_generators.analyses import mean
from dp_wizard.utils.code_generators.notebook_generator import NotebookGenerator
from dp_wizard.utils.constraints import MAX_BOUND, MIN_BOUND

abc_csv_path = str((package_root.parent / "tests/fixtures/abc.csv").absolute())


def number_lines(text: str):
    return "\n".join(
        f"# {i}:\n{line}" if line and not i % 10 else line
        for (i, line) in enumerate(text.splitlines())
    )


good_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
)


@settings(deadline=None)
@given(
    bin_count=st.integers(),
    lower_upper=st.tuples(good_floats, good_floats).filter(
        lambda l_u: MIN_BOUND <= l_u[0] < l_u[1] <= MAX_BOUND
    ),
)
def test_make_random_notebook(bin_count, lower_upper):
    lower_bound, upper_bound = lower_upper
    mean_plan_column = AnalysisPlanColumn(
        statistic_name=mean.name,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        bin_count=bin_count,  # Unused
        weight=4,
    )
    plan = AnalysisPlan(
        product=Product.STATISTICS,
        groups={},
        columns={ColumnName("2B"): [mean_plan_column]},
        contributions=1,
        contributions_entity="Family",
        csv_path=abc_csv_path,
        epsilon=1,
        max_rows=100_000,
    )
    notebook_py = NotebookGenerator(plan, "Note goes here!").make_py(reformat=True)
    print(number_lines(notebook_py))
    globals = {}
    exec(notebook_py, globals)

    # Close plots to avoid this warning:
    # > RuntimeWarning: More than 20 figures have been opened.
    # > Figures created through the pyplot interface (`matplotlib.pyplot.figure`)
    # > are retained until explicitly closed and may consume too much memory.
    import matplotlib.pyplot as plt

    plt.close("all")
