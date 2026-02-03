from quant_system.sentiment.factor.base import Factor


class MomentumFactor(Factor):
    def __init__(self, window: int):
        self.window = window

    def compute(self, prices, t):
        values = {}
        for symbol, series in prices.items():
            if t < self.window:
                continue
            values[symbol] = series[t] / series[t - self.window] - 1
        return values
