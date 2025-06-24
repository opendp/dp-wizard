from tempfile import NamedTemporaryFile
import subprocess
import pytest
import re
import opendp.prelude as dp

from dp_wizard.utils.code_generators.analyses import histogram, mean, median
from dp_wizard.utils.code_generators import (
    make_column_config_block,
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.code_generators.notebook_generator import NotebookGenerator
from dp_wizard.utils.code_generators.script_generator import ScriptGenerator


def test_make_column_config_block_for_unrecognized():
    with pytest.raises(Exception, match=r"Unrecognized analysis"):
        make_column_config_block(
            name="HW GRADE",
            analysis_type="Bad AnalysisType!",
            lower_bound=0,
            upper_bound=100,
            bin_count=10,
        )


def test_make_column_config_block_for_mean():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_type=mean.name,
            lower_bound=0,
            upper_bound=100,
            bin_count=10,
        ).strip()
        == """# See the OpenDP Library docs for more on making private means:
# https://docs.opendp.org/en/stable/getting-started/tabular-data/essential-statistics.html#Mean

hw_grade_expr = (
    pl.col('HW GRADE')
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.mean((0, 100))
)"""
    )


def test_make_column_config_block_for_median():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_type=median.name,
            lower_bound=0,
            upper_bound=100,
            bin_count=20,
        ).strip()
        == """# See the OpenDP Library docs for more on making private medians and quantiles:
# https://docs.opendp.org/en/stable/getting-started/tabular-data/essential-statistics.html#Median

hw_grade_expr = (
    pl.col('HW GRADE')
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.quantile(0.5, make_cut_points(0, 100, bin_count=20))
)"""  # noqa: B950 (too long!)
    )


def test_make_column_config_block_for_histogram():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_type=histogram.name,
            lower_bound=0,
            upper_bound=100,
            bin_count=10,
        ).strip()
        == """# See the OpenDP Library docs for more on making private histograms:
# https://docs.opendp.org/en/stable/getting-started/examples/histograms.html

# Use the public information to make cut points for 'HW GRADE':
hw_grade_cut_points = make_cut_points(
    lower_bound=0,
    upper_bound=100,
    bin_count=10,
)

# Use these cut points to add a new binned column to the table:
hw_grade_bin_expr = (
    pl.col('HW GRADE')
    .cut(hw_grade_cut_points)
    .alias('hw_grade_bin')  # Give the new column a name.
    .cast(pl.String)
)"""
    )


abc_csv = "tests/fixtures/abc.csv"


def number_lines(text: str):
    return "\n".join(
        f"# {i}:\n{line}" if line and not i % 10 else line
        for (i, line) in enumerate(text.splitlines())
    )


histogram_plan_column = AnalysisPlanColumn(
    analysis_type=histogram.name,
    lower_bound=5,
    upper_bound=15,
    bin_count=20,
    weight=4,
)
mean_plan_column = AnalysisPlanColumn(
    analysis_type=mean.name,
    lower_bound=5,
    upper_bound=15,
    bin_count=0,  # Unused
    weight=4,
)
median_plan_column = AnalysisPlanColumn(
    analysis_type=median.name,
    lower_bound=5,
    upper_bound=15,
    bin_count=10,
    weight=4,
)


def id_for_plan(plan: AnalysisPlan):
    columns = ", ".join(f"{v[0].analysis_type} of {k}" for k, v in plan.columns.items())
    description = f"{columns}; grouped by ({', '.join(plan.groups) or 'nothing'})"
    return re.sub(r"\W+", "_", description)  # For selection with "pytest -k substring"


plans = [
    AnalysisPlan(
        groups=groups,
        columns=columns,
        contributions=contributions,
        csv_path=abc_csv,
        epsilon=1,
    )
    for contributions in [1, 10]
    for groups in [[], ["A"]]
    for columns in [
        # Single:
        {"B": [histogram_plan_column]},
        {"B": [mean_plan_column]},
        {"B": [median_plan_column]},
        # Multiple:
        {
            "B": [histogram_plan_column],
            "C": [mean_plan_column],
            "D": [median_plan_column],
        },
    ]
]


@pytest.mark.parametrize("plan", plans, ids=id_for_plan)
def test_make_notebook(plan):
    notebook = NotebookGenerator(plan).make_py()
    print(number_lines(notebook))
    globals = {}
    exec(notebook, globals)
    assert isinstance(globals["context"], dp.Context)


@pytest.mark.parametrize("plan", plans, ids=id_for_plan)
def test_make_script(plan):
    script = ScriptGenerator(plan).make_py()

    # Make sure jupytext formatting doesn't bleed into the script.
    # https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format
    assert "# -" not in script
    assert "# +" not in script

    with NamedTemporaryFile(mode="w") as fp:
        fp.write(script)
        fp.flush()

        result = subprocess.run(
            ["python", fp.name, "--csv", abc_csv], capture_output=True
        )
        assert result.returncode == 0
