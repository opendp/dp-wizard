from tempfile import NamedTemporaryFile
import subprocess
import re
import pytest
import opendp.prelude as dp
from dp_creator_ii.template import _Template, make_notebook_py, make_script_py


fake_csv = "dp_creator_ii/tests/fixtures/fake.csv"


def test_fill_template():
    context_template = _Template("context.py")
    context_block = str(
        context_template.fill_values(
            {
                "CSV_PATH": fake_csv,
                "UNIT": 1,
                "LOSS": 1,
                "WEIGHTS": [1],
            }
        )
    )
    assert f"data=pl.scan_csv('{fake_csv}', encoding=\"utf8-lossy\")" in context_block


def test_fill_template_unfilled_slots():
    context_template = _Template("context.py")
    with pytest.raises(
        Exception,
        match=re.escape("context.py has unfilled slots: CSV_PATH, LOSS, UNIT, WEIGHTS"),
    ):
        str(context_template.fill_values({}))


def test_make_notebook():
    notebook = make_notebook_py(
        csv_path=fake_csv,
        unit=1,
        loss=1,
        weights=[1],
    )
    globals = {}
    exec(notebook, globals)
    assert isinstance(globals["context"], dp.Context)


def test_make_script():
    script = make_script_py(
        unit=1,
        loss=1,
        weights=[1],
    )

    with NamedTemporaryFile(mode="w", delete=False) as fp:
        fp.write(script)
        fp.close()

        result = subprocess.run(["python", fp.name, "--csv", fake_csv])
        assert result.returncode == 0
