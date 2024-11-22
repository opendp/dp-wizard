from yaml import dump
from pathlib import Path

report = {
    "inputs": INPUTS,
    "outputs": OUTPUTS,
}


print(dump(report))

Path("/tmp/report.txt").write_text(dump(report))
