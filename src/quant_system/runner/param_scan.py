from typing import List
from itertools import product
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.result import BacktestResult
from quant_system.strategy.base import Strategy
from quant_system.report.result_table import ResultTable


def run_param_scan(
    symbol: str,
    prices: List[float],
    strategy_cls: type[Strategy],
    param_grid: dict,
) -> ResultTable:
    """
    param_grid example:
    {
        "window": [5, 10, 20],
        "threshold": [0.0, 0.01]
    }
    """
    results: List[BacktestResult] = []

    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())

    for values in product(*param_values):
        params = dict(zip(param_names, values))

        # 1️⃣ 构造策略
        strategy = strategy_cls(**params)
        signals = strategy.generate_signals(prices)

        # 2️⃣ 跑回测
        bt = BacktestEngine(
            symbol=symbol,
            prices=prices,
            signals=signals,
        )
        result = bt.run()  # ✅ 现在直接返回 BacktestResult

        # 3️⃣ 记录参数组合
        result.params = params
        results.append(result)

    return ResultTable(results)
