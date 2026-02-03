import csv
from quant_system.report.result_table import ResultTable


def export_csv(table: ResultTable, path: str):
    rows = table.rows()
    if not rows:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
