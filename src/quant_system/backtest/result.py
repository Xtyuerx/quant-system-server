from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BacktestResult:
    symbol: str
    initial_cash: float
    final_equity: float
    equity_curve: List[float]
    params: Optional[dict] = None

    # 👇 内部缓存字段（不作为对外指标）
    _total_return: Optional[float] = None
    _max_drawdown: Optional[float] = None

    @property
    def total_return(self) -> float:
        if self._total_return is None:
            self._total_return = (self.final_equity / self.initial_cash) - 1
        return self._total_return

    @property
    def max_drawdown(self) -> float:
        if self._max_drawdown is None:
            peak = self.equity_curve[0]
            max_dd = 0.0

            for equity in self.equity_curve:
                peak = max(peak, equity)
                drawdown = (equity - peak) / peak
                max_dd = min(max_dd, drawdown)

            self._max_drawdown = max_dd

        return self._max_drawdown

    def summary(self) -> dict:
        return {
            "symbol": self.symbol,
            "final_equity": self.final_equity,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
        }

    def to_row(self) -> dict:
        row = {
            "symbol": self.symbol,
            "final_equity": f"{self.final_equity:,.2f}",
            "total_return": f"{self.total_return * 100:.2f}%",
            "max_drawdown": f"{self.max_drawdown * 100:.2f}%",
        }
        if self.params:
            row.update(self.params)
        return row

    def to_dict(self) -> dict:
        row = {
            "symbol": self.symbol,
            "final_equity": self.final_equity,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
        }
        if self.params:
            row.update(self.params)
        return row
    
    def to_pretty_dict(self) -> dict:
        row = {
            "symbol": self.symbol,
            "final_equity": f"${self.final_equity:,.2f}",
            "total_return": f"{self.total_return * 100:.2f}%",
            "max_drawdown": f"{self.max_drawdown * 100:.2f}%",
        }
        if self.params:
            row.update(self.params)
        return row