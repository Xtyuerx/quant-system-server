from typing import List


def total_return(self) -> float:
    """
    领域属性
    """
    return (self.final_equity / self.initial_equity) - 1

def calc_max_drawdown(self) -> float:
    peak = self.equity_curve[0]
    max_dd = 0.0

    for equity in self.equity_curve:
        peak = max(peak, equity)
        drawdown = (equity - peak) / peak
        max_dd = min(max_dd, drawdown)

    return max_dd

@property
def max_drawdown(self) -> float:
    if "max_drawdown" not in self._metrics:
        self._metrics["max_drawdown"] = self.calc_max_drawdown()
    return self._metrics["max_drawdown"]