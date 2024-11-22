from yaml import dump
from pathlib import Path

report = {"outputs": OUTPUTS_DICT}


print(dump(report))

Path("/tmp/report.txt").write_text(dump(report))
