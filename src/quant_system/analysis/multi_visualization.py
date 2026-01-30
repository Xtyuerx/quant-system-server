import matplotlib.pyplot as plt
from typing import Dict, List
from quant_system.backtest.trade import Trade

def plot_multi_strategy_comparison(
    price_data: Dict[str, List[float]],
    backtest_results: Dict[str, Dict[str, object]],
    title: str = "Multi-Strategy Multi-Asset Comparison",
    save_path: str = None
):
    """
    绘制多标的、多策略 equity_curve 对比
    - price_data: symbol -> price list
    - backtest_results: symbol -> strategy_name -> SimpleBacktest instance
    """
    plt.figure(figsize=(14, 7))

    for symbol, strat_results in backtest_results.items():
        for strat_name, bt in strat_results.items():
            label = f"{symbol}-{strat_name}"
            plt.plot(bt.equity_curve, label=label)

    plt.title(title)
    plt.xlabel("Time Step")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved comparison plot to {save_path}")

    plt.show()
