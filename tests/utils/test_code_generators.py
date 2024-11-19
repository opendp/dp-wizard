from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path
import re
import pytest
import opendp.prelude as dp
from dp_wizard.utils.code_generators import (
    Template,
    ScriptGenerator,
    NotebookGenerator,
    AnalysisPlan,
    AnalysisPlanColumn,
)


fixtures_path = Path(__file__).parent.parent / "fixtures"
fake_csv = "tests/fixtures/fake.csv"


def test_param_conflict():
    with pytest.raises(Exception, match=r"mutually exclusive"):
        Template("context", template="Not allowed if path present")


def test_fill_expressions():
    template = Template(None, template="No one VERB the ADJ NOUN!")
    filled = str(
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        )
    )
    assert filled == "No one expects the Spanish Inquisition!"


def test_fill_values():
    template = Template(None, template="assert [STRING] * NUM == LIST")
    filled = str(
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        )
    )
    assert filled == "assert ['🙂'] * 3 == ['🙂', '🙂', '🙂']"


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
        str(template)
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


def test_fill_template_unfilled_slots():
    context_template = Template("context")
    with pytest.raises(
        Exception,
        match=re.escape("context.py has unfilled slots"),
    ):
        str(context_template.fill_values())


def test_make_notebook():
    notebook = NotebookGenerator(
        AnalysisPlan(
            csv_path=fake_csv,
            contributions=1,
            epsilon=1,
            columns={
                # For a strong test, use a column whose name
                # doesn't work as a python identifier.
                "hw-number": AnalysisPlanColumn(
                    lower_bound=5,
                    upper_bound=15,
                    bin_count=20,
                    weight=4,
                )
            },
        )
    ).make_py()
    print(notebook)
    globals = {}
    exec(notebook, globals)
    assert isinstance(globals["context"], dp.Context)


def test_make_script():
    script = ScriptGenerator(
        AnalysisPlan(
            csv_path=None,
            contributions=1,
            epsilon=1,
            columns={
                "hw-number": AnalysisPlanColumn(
                    lower_bound=5,
                    upper_bound=15,
                    bin_count=20,
                    weight=4,
                )
            },
        )
    ).make_py()
    print(script)

    with NamedTemporaryFile(mode="w") as fp:
        fp.write(script)
        fp.flush()

        result = subprocess.run(["python", fp.name, "--csv", fake_csv])
        assert result.returncode == 0
