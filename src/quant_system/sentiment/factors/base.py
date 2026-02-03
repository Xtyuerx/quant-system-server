from abc import ABC, abstractmethod

class BaseFactor(ABC):
    @abstractmethod
    def compute(
        self,
        prices: Dict[str, List[float]],
        t: int
    ) -> Dict[str, float]:
        """
        在时间 t 计算横截面 factor 值
        key: symbol
        value: 因子暴露
        """
        ...
