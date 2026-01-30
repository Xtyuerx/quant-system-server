from typing import List
from quant_system.strategy.base import Strategy
from quant_system.enums.signal import Signal


class BuyAndHoldStrategy(Strategy):
    def generate_signals(self, prices: List[float]) -> List[Signal]:
        return [Signal.LONG] * len(prices)
