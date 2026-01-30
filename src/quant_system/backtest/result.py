from dataclasses import dataclass
from typing import List


@dataclass
class BacktestResult:
    equity_curve: List[float]
