import numpy as np
from .base import BaseFactor


class StockMomentumFactor(BaseFactor):
    """
    个股动量因子
    """

    name = "stock_momentum"
    scope = "stock"

    def compute(self, data: dict) -> float:
        close = np.asarray(data["close"], dtype=float)
        return float((close[-1] - close[0]) / close[0])
