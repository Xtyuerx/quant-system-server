import numpy as np
from .base import BaseFactor


class MarketVolatilityFactor(BaseFactor):
    """
    市场整体波动率因子
    """

    name = "market_volatility"
    scope = "market"

    def compute(self, data: dict) -> float:
        close = np.asarray(data["close"], dtype=float)
        returns = np.diff(np.log(close))

        # 波动越大 → 情绪越恐惧 → 分值越低
        return -float(np.std(returns))
