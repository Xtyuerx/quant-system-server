from quant_system.backtest.engine import BacktestEngine

class MultiBacktest:
    def __init__(self, data_list):
        self.data_list = data_list

    def run(self) -> list:
        results = []

        for symbol, prices, signals in self.data_list:
            bt = BacktestEngine(
                prices=prices,
                signals=signals,
                symbol=symbol,
            )
            result = bt.run()
            results.append(result)

        return results
