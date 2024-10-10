from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path
import re
import pytest
import opendp.prelude as dp
from dp_creator_ii.template import _Template, make_notebook_py, make_script_py


fake_csv = "dp_creator_ii/tests/fixtures/fake.csv"


def test_fill_expressions():
    template = _Template(None, template="No one VERB the ADJ NOUN!")
    filled = str(
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        )
    )
    assert filled == "No one expects the Spanish Inquisition!"


def test_fill_values():
    template = _Template(None, template="assert [STRING] * NUM == LIST")
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
    template = _Template(
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
    context_template = _Template("context.py")
    with pytest.raises(
        Exception,
        match=re.escape(
            "context.py has unfilled slots: "
            "CSV_PATH, LOSS, PRIVACY_UNIT_BLOCK, WEIGHTS"
        ),
    ):
        str(context_template.fill_values())


def test_make_notebook():
    notebook = make_notebook_py(
        csv_path=fake_csv,
        contributions=1,
        loss=1,
        weights=[1],
    )
    globals = {}
    exec(notebook, globals)
    assert isinstance(globals["context"], dp.Context)


def test_make_script():
    script = make_script_py(
        contributions=1,
        loss=1,
        weights=[1],
    )

    def clear_empty_lines(text):
        # Cleanup whitespace after indenting blocks
        return re.sub(r"^\s+$", "", text, flags=re.MULTILINE).strip()

    expected_script = (
        Path(__file__).parent / "fixtures" / "expected-script.py"
    ).read_text()
    assert clear_empty_lines(script) == clear_empty_lines(expected_script)

    with NamedTemporaryFile(mode="w") as fp:
        fp.write(script)
        fp.flush()

        result = subprocess.run(["python", fp.name, "--csv", fake_csv])
        assert result.returncode == 0
