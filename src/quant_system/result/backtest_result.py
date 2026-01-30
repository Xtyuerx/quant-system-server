from typing import List


class BacktestResult:
    def __init__(
        self,
        equity_curve: List[float],
        total_return: float,
        max_drawdown: float,
    ):
        self.equity_curve = equity_curve
        self.total_return = total_return
        self.max_drawdown = max_drawdown
