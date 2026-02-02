from typing import List
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.result import BacktestResult
from quant_system.strategy.base import Strategy


def run_param_scan(
    symbol: str,
    prices: List[float],
    strategy_cls: type[Strategy],
    param_grid: dict,
) -> List[BacktestResult]:
    """
    param_grid example:
    {"window": [3, 5, 10, 20]}
    """
    results: List[BacktestResult] = []

    for param_name, values in param_grid.items():
        for v in values:
            # 1️⃣ 构造策略
            strategy = strategy_cls(**{param_name: v})
            signals = strategy.generate_signals(prices)

            # 2️⃣ 跑回测（E6）
            bt = BacktestEngine(
                symbol=symbol,
                prices=prices,
                signals=signals,
            )

            equity_curve = bt.run()

            # 3️⃣ 包装 Result（E7）
            final_equity = equity_curve[-1]
            total_return = final_equity / bt.initial_cash - 1

            result = BacktestResult(
                symbol=symbol,
                initial_cash=bt.initial_cash,
                final_equity=final_equity,
                equity_curve=equity_curve,
            )

            # 4️⃣ 记录参数
            result.params = {param_name: v}
            results.append(result)

    return results
