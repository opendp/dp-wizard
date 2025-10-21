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

Path(TXT_REPORT_PATH).write_text(dump(report))

synthetic_data.write_csv(CSV_REPORT_PATH)
