import csv
from pathlib import Path

from yaml import dump

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

synthetic_data.write_csv(target_path / "report.csv")

# TODO: Use figures
