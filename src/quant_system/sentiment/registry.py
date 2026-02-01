from typing import Dict, List
from .factors.base import BaseFactor


class FactorRegistry:
    """
    管理所有情绪因子
    """

    def __init__(self):
        from quant_system.sentiment.factors.volatility import VolatilityFactor
        self._factors: Dict[str, List[BaseFactor]] = {
            "market": [
                VolatilityFactor(),
            ],
            "stock": [
                VolatilityFactor(),  # 现在先复用，后面再拆
            ],
        }

    def register(self, factor: BaseFactor):
        """
        注册一个因子
        """
        if not factor.name:
            raise ValueError("Factor must have a name")

        if factor.scope not in self._factors:
            raise ValueError(f"Unknown factor scope: {factor.scope}")

        self._factors[factor.scope].append(factor)

    def get_factors(self, scope: str) -> List[BaseFactor]:
        """
        按 scope 获取因子列表
        """
        return self._factors.get(scope, [])
