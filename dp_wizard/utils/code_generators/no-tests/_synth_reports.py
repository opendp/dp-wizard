import csv
from pathlib import Path

from yaml import dump


# https://stackoverflow.com/a/6027615/10727889
def flatten_dict(dictionary, parent_key=""):
    """
    Walk tree to return flat dictionary.
    >>> from pprint import pp
    >>> pp(flatten_dict({
    ...     "inputs": {
    ...         "data": "fake.csv"
    ...     },
    ...     "outputs": {
    ...         "a column": {
    ...             "(0, 1]": 24,
    ...             "(1, 2]": 42,
    ...         }
    ...     }
    ... }))
    {'inputs: data': 'fake.csv',
     'outputs: a column: (0, 1]': 24,
     'outputs: a column: (1, 2]': 42}
    """
    separator = ": "
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


report = {
    "inputs": {
        "data": CSV_PATH,
        "epsilon": EPSILON,
        "columns": COLUMNS,
        "contributions": contributions,
    },
    "outputs": OUTPUTS,
}

print(dump(report))
Path(TXT_REPORT_PATH).write_text(dump(report))

synthetic_data.write_csv(CSV_REPORT_PATH)
