import matplotlib.pyplot as plt
import numpy as np
from quant_system.backtest.simple_backtest import SimpleBacktest
from quant_system.enums.signal import sentiment_to_signal
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.sentiment.market_sentiment import MarketSentiment
from quant_system.backtest.multi_backtest import MultiBacktest

def main():
    prices = load_prices_from_csv("AAPL.csv")

    """ sentiment = MarketSentiment(
        momentum_window=10,
        volatility_window=10,
        long_threshold=0.1,
        short_threshold=-0.1,
    ) """

    ms = MarketSentiment(
        momentum_window=10,
        volatility_window=10,
        long_threshold=0.005,
        short_threshold=-0.005,
    )
    signals = ms.generate_signals(prices)

    bt = SimpleBacktest(
        prices=prices,
        signals=signals,
        initial_cash=100_000,
    )

    multi_bt = MultiBacktest(
        symbols=["AAPL.csv", "MSFT.csv"],
        prices_loader=load_prices_from_csv,
        signals_generator=ms.generate_signals,
    )


    results = multi_bt.run()

    print()
    print("Symbol   FinalEquity   Return    MaxDD")
    print("---------------------------------------")

    for symbol, result in results.items():
        print(f"\n=== {symbol} ===")
        print(f"Final equity: {result.final_equity:.2f}")
        print(f"Total return: {result.total_return:.2%}")
        print(f"Max drawdown: {result.max_drawdown:.2%}")
        print("Equity curve (first 10):", result.equity_curve[:10])

if __name__ == "__main__":
    main()
