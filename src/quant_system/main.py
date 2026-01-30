from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy
from quant_system.backtest.simple_backtest import SimpleBacktest
from quant_system.metrics.performance import total_return, max_drawdown


def main():
    print("Quant System Started 🚀")

    dates, prices = load_prices_from_csv("sample_prices.csv")

    strategy = BuyAndHoldStrategy()
    signals = strategy.generate_signals(prices)

    backtest = SimpleBacktest(prices, signals, initial_cash=100_000)
    equity_curve = backtest.run()

    tr = total_return(equity_curve)
    mdd = max_drawdown(equity_curve)

    print("Final equity:", equity_curve[-1])
    print(f"Total Return: {tr:.2%}")
    print(f"Max Drawdown: {mdd:.2%}")


if __name__ == "__main__":
    main()
