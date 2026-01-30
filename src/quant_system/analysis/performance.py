from typing import List


def total_return(equity_curve: List[float]) -> float:
    """
    总收益率
    """
    if not equity_curve:
        return 0.0
    return (equity_curve[-1] / equity_curve[0]) - 1


def max_drawdown(equity_curve: List[float]) -> float:
    """
    最大回撤（负数）
    """
    peak = equity_curve[0]
    max_dd = 0.0

    for equity in equity_curve:
        if equity > peak:
            peak = equity
        drawdown = (equity - peak) / peak
        if drawdown < max_dd:
            max_dd = drawdown

    return max_dd
