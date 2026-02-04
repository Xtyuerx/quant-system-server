from typing import List
from quant_system.strategy.base import Strategy
from quant_system.backtest.signal import SignalType

class SimpleMAStrategy(Strategy):
    def __init__(self, window: int = 3):
        self.window = window

    def generate_signals(self, prices: List[float]) -> List[SignalType]:
        signals = []

        for i, price in enumerate(prices):
            if i < self.window:
                signals.append(SignalType.HOLD)
                continue

            ma = sum(prices[i - self.window:i]) / self.window

            if price > ma:
                signals.append(SignalType.BUY)
            else:
                signals.append(SignalType.HOLD)

        return signals
