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
if isinstance(contingency_table_melted, str):
    # If too many rows, contingency_table_melted is just an error message:
    Path(CONTINGENCY_TABLE_PATH).write_text(contingency_table_melted)
else:
    contingency_table_melted.write_csv(CONTINGENCY_TABLE_PATH)
