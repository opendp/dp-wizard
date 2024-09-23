from dp_creator_ii.template import Template
import opendp.prelude as dp


def test_template():
    context_template = Template('context.py')
    context_code = context_template.fill({
        'CSV_PATH': '"dp_creator_ii/tests/fake.csv"',
        'UNIT': '1',
        'LOSS': '1',
        'WEIGHTS': '[1]'
    })

    globals = {}
    exec(context_code, globals)
    assert isinstance(globals['context'], dp.Context)
