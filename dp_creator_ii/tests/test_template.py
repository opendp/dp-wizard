from dp_creator_ii.template import Template


def test_template():
    context_template = Template('context.py')
    context_code = context_template.fill({
        'CSV_PATH': '"fake.csv"',
        'UNIT': '1',
        'LOSS': '1',
        'WEIGHTS': '[1]'
    })
    assert 'data=pl.scan_csv("fake.csv")' in context_code
