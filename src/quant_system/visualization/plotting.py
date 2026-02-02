import matplotlib.pyplot as plt
from quant_system.backtest.result import BacktestResult

# 单策略 equity 曲线
def plot_equity(result: BacktestResult):
    plt.figure(figsize=(10, 4))
    plt.plot(result.equity_curve)
    plt.title(f"{result.symbol} Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 多策略 equity 曲线对比
def plot_equity_multi(
    results: list[BacktestResult],
    title: str = "Equity Curve Comparison",
):
    plt.figure(figsize=(10, 4))

    for r in results:
        label = r.symbol
        if hasattr(r, "params") and r.params:
            label += " " + ", ".join(f"{k}={v}" for k, v in r.params.items())

        plt.plot(r.equity_curve, label=label)

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()