from dp_creator_ii.template import _Template, make_notebook
import opendp.prelude as dp


def test_fill_template():
    context_template = _Template('context.py')
    context_code = context_template.fill_values({
        'CSV_PATH': 'dp_creator_ii/tests/fake.csv',
        'UNIT': 1,
        'LOSS': 1,
        'WEIGHTS': [1]
    })
    assert "data=pl.scan_csv('dp_creator_ii/tests/fake.csv')" in context_code


def test_make_notebook():
    notebook = make_notebook(
        csv_path='dp_creator_ii/tests/fake.csv',
        unit=1,
        loss=1,
        weights=[1]
    )
    print(notebook)
    globals = {}
    exec(notebook, globals)
    assert isinstance(globals['context'], dp.Context)
