from quant_system.backtest.simple_backtest import SimpleBacktest

class MultiBacktest:
    def __init__(self, symbols, prices_loader, signals_generator):
        self.symbols = symbols
        self.prices_loader = prices_loader
        self.signals_generator = signals_generator

    def run(self):
        results = {}

        for symbol in self.symbols:
            prices = self.prices_loader(symbol)
            signals = self.signals_generator(prices)

            bt = SimpleBacktest(
                prices=prices,
                signals=signals,
            )

            result = bt.run()
            results[symbol] = result

        return results
