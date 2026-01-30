from abc import ABC, abstractmethod
from typing import List


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, prices: List[float]) -> List[int]:
        """
        根据价格生成交易信号
        1 = 持有 / 做多
        0 = 空仓
        -1 = 做空（先预留）
        """
        pass
