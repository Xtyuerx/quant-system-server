class MultiBacktest:
    def __init__(self, backtests):
        """
        backtests: List[BacktestEngine]
        """
        self.backtests = backtests

    def run(self):
        results = {}

        for bt in self.backtests:
            result = bt.run()
            results[result.symbol] = result

        return results
