class BacktestResult:
    def __init__(
        self,
        equity_curve,
        total_return=None,
        max_drawdown=None,
    ):
        self.equity_curve = equity_curve
        self.final_equity = equity_curve[-1]

        # 允许 SimpleBacktest 传，也允许这里兜底算
        if total_return is None:
            self.total_return = (self.final_equity / equity_curve[0]) - 1
        else:
            self.total_return = total_return

        self.max_drawdown = max_drawdown

    def __repr__(self):
        parts = [
            f"final_equity={self.final_equity:.2f}",
            f"total_return={self.total_return:.2%}",
        ]
        if self.max_drawdown is not None:
            parts.append(f"max_drawdown={self.max_drawdown:.2%}")

        return f"BacktestResult({', '.join(parts)})"
