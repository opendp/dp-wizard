from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path
import pytest
import opendp.prelude as dp

from dp_wizard import AnalysisType
from dp_wizard.utils.code_generators import (
    make_column_config_block,
    Template,
    ScriptGenerator,
    NotebookGenerator,
    AnalysisPlan,
    AnalysisPlanColumn,
)


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
            analysis_type=AnalysisType.MEAN,
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
            analysis_type=AnalysisType.HISTOGRAM,
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


def test_param_conflict():
    with pytest.raises(Exception, match=r"mutually exclusive"):
        Template("context", template="Not allowed if path present")


def test_fill_expressions():
    template = Template(None, template="No one VERB the ADJ NOUN!")
    filled = template.fill_expressions(
        VERB="expects",
        ADJ="Spanish",
        NOUN="Inquisition",
    ).finish()
    assert filled == "No one expects the Spanish Inquisition!"


def test_fill_expressions_missing_slot_in_template():
    template = Template(None, template="No one ... the ADJ NOUN!")
    with pytest.raises(Exception, match=r"No 'VERB' slot to fill with 'expects'"):
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        ).finish()


def test_fill_expressions_extra_slot_in_template():
    template = Template(None, template="No one VERB ARTICLE ADJ NOUN!")
    with pytest.raises(Exception, match=r"'ARTICLE' slot not filled"):
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        ).finish()


def test_fill_values():
    template = Template(None, template="assert [STRING] * NUM == LIST")
    filled = template.fill_values(
        STRING="🙂",
        NUM=3,
        LIST=["🙂", "🙂", "🙂"],
    ).finish()
    assert filled == "assert ['🙂'] * 3 == ['🙂', '🙂', '🙂']"


def test_fill_values_missing_slot_in_template():
    template = Template(None, template="assert [STRING] * ... == LIST")
    with pytest.raises(Exception, match=r"No 'NUM' slot to fill with '3'"):
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        ).finish()


def test_fill_values_extra_slot_in_template():
    template = Template(None, template="CMD [STRING] * NUM == LIST")
    with pytest.raises(Exception, match=r"'CMD' slot not filled"):
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        ).finish()


def test_fill_blocks():
    # "OK" is less than three characters, so it is not a slot.
    template = Template(
        None,
        template="""# MixedCase is OK

FIRST

with fake:
    SECOND
    if True:
        THIRD
""",
    )
    template.fill_blocks(
        FIRST="\n".join(f"import {i}" for i in "abc"),
        SECOND="\n".join(f"f({i})" for i in "123"),
        THIRD="\n".join(f"{i}()" for i in "xyz"),
    )
    assert (
        template.finish()
        == """# MixedCase is OK

import a
import b
import c

with fake:
    f(1)
    f(2)
    f(3)
    if True:
        x()
        y()
        z()
"""
    )


def test_fill_blocks_missing_slot_in_template_alone():
    template = Template(None, template="No block slot")
    with pytest.raises(Exception, match=r"No 'SLOT' slot"):
        template.fill_blocks(SLOT="placeholder").finish()


def test_fill_blocks_missing_slot_in_template_not_alone():
    template = Template(None, template="No block SLOT")
    with pytest.raises(
        Exception, match=r"Block slots must be alone on line; No 'SLOT' slot"
    ):
        template.fill_blocks(SLOT="placeholder").finish()


def test_fill_blocks_extra_slot_in_template():
    template = Template(None, template="EXTRA\nSLOT")
    with pytest.raises(Exception, match=r"'EXTRA' slot not filled"):
        template.fill_blocks(SLOT="placeholder").finish()


def test_fill_blocks_not_string():
    template = Template(None, template="SOMETHING")
    with pytest.raises(
        Exception,
        match=r"For SOMETHING in template-instead-of-path, expected string, not 123",
    ):
        template.fill_blocks(SOMETHING=123).finish()


def number_lines(text: str):
    return "\n".join(
        f"# {i}:\n{line}" if line and not i % 5 else line
        for (i, line) in enumerate(text.splitlines())
    )


histogram_plan_column = AnalysisPlanColumn(
    analysis_type=AnalysisType.HISTOGRAM,
    lower_bound=5,
    upper_bound=15,
    bin_count=20,
    weight=4,
)
mean_plan_column = AnalysisPlanColumn(
    analysis_type=AnalysisType.MEAN,
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
