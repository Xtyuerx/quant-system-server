from abc import ABC, abstractmethod
from typing import List
from quant_system.backtest.signal import SignalType

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, prices: List[float]) -> List[SignalType]:
        ...
