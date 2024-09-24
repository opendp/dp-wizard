from tempfile import NamedTemporaryFile
import subprocess
import opendp.prelude as dp
from dp_creator_ii.template import _Template, make_notebook, make_script


fake_csv = 'dp_creator_ii/tests/fake.csv'


def test_fill_template():
    context_template = _Template('context.py')
    context_block = str(context_template.fill_values({
        'CSV_PATH': fake_csv,
        'UNIT': 1,
        'LOSS': 1,
        'WEIGHTS': [1]
    }))
    assert f"data=pl.scan_csv('{fake_csv}')" in context_block


def test_make_notebook():
    notebook = make_notebook(
        csv_path=fake_csv,
        unit=1,
        loss=1,
        weights=[1]
    )
    globals = {}
    exec(notebook, globals)
    assert isinstance(globals['context'], dp.Context)


def test_make_script():
    script = make_script(
        unit=1,
        loss=1,
        weights=[1]
    )

    with NamedTemporaryFile(mode='w', delete_on_close=False) as fp:
        fp.write(script)
        fp.close()

        result = subprocess.run(
            ['python', fp.name, '--csv', fake_csv])
        assert result.returncode == 0
