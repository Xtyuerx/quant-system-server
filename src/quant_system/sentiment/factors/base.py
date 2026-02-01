from abc import ABC, abstractmethod

class BaseFactor(ABC):
    """
    所有情绪因子的基类
    """

    # 因子唯一名称（字符串）
    name: str = ""

    # 使用范围：market / stock
    scope: str  # "market" | "stock"

    @abstractmethod
    def compute(self, data: dict) -> float:
        """
        输入行情数据，输出一个情绪分值
        """
        raise NotImplementedError
