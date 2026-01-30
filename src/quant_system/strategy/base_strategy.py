from abc import ABC, abstractmethod
from typing import List
from quant_system.backtest.signal import Signal

class BaseStrategy(ABC):
    """
    策略抽象基类
    """

    @abstractmethod
    def generate_signals(self, prices: List[float]) -> List[Signal]:
        """
        输入价格序列，输出信号序列
        """
        pass
