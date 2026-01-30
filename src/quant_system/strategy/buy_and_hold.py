from typing import List
from quant_system.strategy.base_strategy import BaseStrategy
from quant_system.backtest.signal import Signal, SignalType

class BuyAndHoldStrategy(BaseStrategy):
    def generate_signals(self, prices: List[float]):
        signals = []
        bought = False
        for _ in prices:
            if not bought:
                signals.append(Signal(type=SignalType.BUY))
                bought = True
            else:
                signals.append(Signal(type=SignalType.HOLD))
        return signals