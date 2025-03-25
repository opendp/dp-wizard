from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path
import pytest
import opendp.prelude as dp

from dp_wizard.utils.code_generators.analyses import histogram, mean
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
        == """hw_grade_config = (
    pl.col('HW GRADE')
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.mean((0, 100))
)"""
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
        == """# From the public information, determine the bins for 'HW GRADE':
hw_grade_cut_points = make_cut_points(
    lower_bound=0,
    upper_bound=100,
    bin_count=10,
)

# Use these bins to define a Polars column:
hw_grade_config = (
    pl.col('HW GRADE')
    .cut(hw_grade_cut_points)
    .alias('hw_grade_bin')  # Give the new column a name.
    .cast(pl.String)
)"""
    )


fixtures_path = Path(__file__).parent.parent / "fixtures"
fake_csv = "tests/fixtures/fake.csv"


def number_lines(text: str):
    return "\n".join(
        f"# {i}:\n{line}" if line and not i % 5 else line
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
kwargs = {
    "csv_path": fake_csv,
    "contributions": 1,
    "epsilon": 1,
}
plans = [
    AnalysisPlan(groups=groups, columns=columns, **kwargs)
    for groups in [[], ["class year"]]
    for columns in [
        {"hw-number": histogram_plan_column},
        {"hw-number": mean_plan_column},
        {"hw-number": histogram_plan_column, "grade": mean_plan_column},
    ]
]


def id_for_plan(plan: AnalysisPlan):
    columns = ", ".join(f"{v.analysis_type} of {k}" for k, v in plan.columns.items())
    return f"{columns}; grouped by ({', '.join(plan.groups)})"


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
            ["python", fp.name, "--csv", fake_csv], capture_output=True
        )
        assert result.returncode == 0
