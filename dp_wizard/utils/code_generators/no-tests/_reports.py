from yaml import dump
from pathlib import Path

report = {
    "inputs": {
        "data": CSV_PATH,
    },
    "outputs": OUTPUTS,
}


print(dump(report))

Path("/tmp/report.txt").write_text(dump(report))
