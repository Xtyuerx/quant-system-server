import argparse

import pandas as pd
from quant_system.backtest.multi_backtest import MultiBacktest
from quant_system.visualization.plotting import plot_equity_multi
from quant_system.strategy.signal import SignalType
from quant_system.runner.param_scan import run_param_scan
from quant_system.strategy.simple_ma import SimpleMAStrategy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot equity curve after backtest",
    )
    args = parser.parse_args()

    prices_aapl = [150, 152, 151, 153, 155]
    prices_msft = [300, 301, 302, 303, 304]
    prices = [150, 152, 151, 153, 155, 158, 160, 159]
    
    strategy = SimpleMAStrategy(window=3)

    data_list = [
        (
            "AAPL.csv",
            prices_aapl,
            strategy.generate_signals(prices_aapl),
        ),
        (
            "MSFT.csv",
            prices_msft,
            strategy.generate_signals(prices_msft),
        ),
    ]

    multi_bt = MultiBacktest(data_list)
    
    results = run_param_scan(
        symbol="AAPL.csv",
        prices=prices,
        strategy_cls=SimpleMAStrategy,
        param_grid={"window": [3, 5, 10, 20]},
    )

    # 🔥 核心：拉平
    df = pd.DataFrame([r.to_dict() for r in results])

    # 排序规则（示例）
    df = df.sort_values(
        by=["total_return", "max_drawdown"],
        ascending=[False, True],
    )

    print(df)

    top_results = sorted(
        results,
        key=lambda r: r.total_return,
        reverse=True,
    )[:3]

    plot_equity_multi(
        top_results,
        title="Top 3 MA Windows",
    )

    results_sorted = sorted(
        results,
        key=lambda r: r.total_return,
        reverse=True,
    )

    for r in results_sorted:
        print(r.params, r.total_return, r.max_drawdown)

