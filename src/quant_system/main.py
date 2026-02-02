from quant_system.strategy.signal import SignalType
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.multi_backtest import MultiBacktest

def main():
    data_list = [
        (
            "AAPL.csv",
            [150, 152, 151, 153, 155],
            [
                SignalType.HOLD,
                SignalType.BUY,
                SignalType.HOLD,
                SignalType.SELL,
                SignalType.HOLD,
            ],
        ),
        (
            "MSFT.csv",
            [300, 301, 302, 303, 304],
            [SignalType.HOLD] * 5,
        ),
    ]

    backtests = []
    for symbol, prices, signals in data_list:
        bt = BacktestEngine(
            prices=prices,
            signals=signals,
            symbol=symbol,
        )
        backtests.append(bt)

    multi_bt = MultiBacktest(backtests)
    results = multi_bt.run()

    for symbol, result in results.items():
        print(symbol, result.final_equity)

if __name__ == "__main__":
    main()
