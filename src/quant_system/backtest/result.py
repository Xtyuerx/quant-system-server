from dataclasses import dataclass
from typing import List


@dataclass
class BacktestResult:
    symbol: str
    initial_cash: float
    final_equity: float
    equity_curve: List[float]

    @property
    def total_return(self) -> float:
        return (self.final_equity / self.initial_cash) - 1

    @property
    def max_drawdown(self) -> float:
        peak = self.equity_curve[0]
        max_dd = 0.0

        for equity in self.equity_curve:
            peak = max(peak, equity)
            drawdown = (equity - peak) / peak
            max_dd = min(max_dd, drawdown)

        return max_dd

    def summary(self) -> dict:
        return {
            "symbol": self.symbol,
            "final_equity": self.final_equity,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
        }

    def to_row(self) -> dict:
        return self.summary()
