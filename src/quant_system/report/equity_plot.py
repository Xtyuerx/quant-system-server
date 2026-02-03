import matplotlib.pyplot as plt
from quant_system.backtest.result import BacktestResult

def plot_equity_curve(result: BacktestResult):
    plt.figure()
    plt.plot(result.equity_curve)
    plt.title(f"Equity Curve - {result.symbol}")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.show()
