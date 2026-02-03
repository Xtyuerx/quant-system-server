import csv
from typing import List
from quant_system.backtest.result import BacktestResult


class ResultTable:
  def __init__(self, results: List[BacktestResult]):
    self.results = results

  def head(self, n: int = 5) -> "ResultTable":
    return ResultTable(self.results[:n])

  def tail(self, n: int = 5) -> "ResultTable":
    return ResultTable(self.results[-n:])

  def rows(self) -> list[dict]:
    return [r.to_row() for r in self.results]

  def sort_by(
    self,
    key: str,
    descending: bool = True,
  ) -> "ResultTable":
    sorted_results = sorted(
      self.results,
      key=lambda r: getattr(r, key),
      reverse=descending,
    )
    return ResultTable(sorted_results)

  def top(self, n: int) -> list[BacktestResult]:
    return self.results[:n]

  # 🚀 E9.2：核心
  def pretty_print(self):
    if not self.results:
      print("(empty)")
      return

    rows = [r.to_row() for r in self.results]
    headers = rows[0].keys()

    # 计算列宽
    col_widths = {
      h: max(len(str(row[h])) for row in rows)
      for h in headers
    }

    # header
    header_line = " | ".join(
      f"{h:<{col_widths[h]}}" for h in headers
    )
    sep_line = "-+-".join(
      "-" * col_widths[h] for h in headers
    )

    print(header_line)
    print(sep_line)

    # rows
    for row in rows:
      print(
        " | ".join(
          f"{str(row[h]):<{col_widths[h]}}"
          for h in headers
        )
      )
  
  def best(self, metric: str = "total_return"):
    return max(self.results, key=lambda r: getattr(r, metric))

  def to_csv(self, path: str):
    rows = [r.to_row() for r in self.results]
    with open(path, "w", newline="", encoding="utf-8") as f:
      writer = csv.DictWriter(f, fieldnames=rows[0].keys())
      writer.writeheader()
      writer.writerows(rows)