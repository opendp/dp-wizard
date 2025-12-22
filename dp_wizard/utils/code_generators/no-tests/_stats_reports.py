import csv
import re
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

target_path = Path(TARGET_PATH)
(target_path / "report.txt").write_text(dump(report))

flat_report = flatten_dict(report)
with (target_path / "report.csv").open(mode="w", newline="") as handle:
    writer = csv.writer(handle)
    for kv_pair in flat_report.items():
        writer.writerow(kv_pair)


def png_name(name):
    return re.sub(r"\W+", "-", name) + ".png"


for name, figure in figures.items():
    figure.savefig(target_path / png_name(name))


imgs = [f"<img src='{png_name(name)}' alt='{name}'>" for name in figures.keys()]
html = f"""
<html>
<body>
Figures:
{"\n".join(imgs)}
</body>
</html>"""
(target_path / "report.html").write_text(html)
