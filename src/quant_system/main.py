import argparse

import pandas as pd
from quant_system.backtest.multi_backtest import MultiBacktest
from quant_system.visualization.plotting import plot_equity_multi
from quant_system.strategy.signal import SignalType
from quant_system.runner.param_scan import run_param_scan
from quant_system.strategy.simple_ma import SimpleMAStrategy
from quant_system.report.export import export_csv
from quant_system.report.equity_plot import plot_equity_curve

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

    results \
        .sort_by("total_return", descending=True) \
        .head(5) \
        .pretty_print()

    best = results.best("total_return")
    plot_equity_curve(best)

    results.to_csv("ma_scan_results_head_5.csv")