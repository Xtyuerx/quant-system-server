import numpy as np
from quant_system.sentiment.factors.base import BaseFactor


class VolatilityFactor(BaseFactor):
    name = "volatility"
    scope = "market"
    weight = 1.0

    def compute(self, data: dict) -> float:
        close = np.asarray(data["close"], dtype=float)
        close = close[np.isfinite(close)]
        close = close[close > 0]

        if len(close) < 40:
            return 0.0

        log_price = np.log(close)
        returns = np.diff(log_price)

        recent = returns[-20:].std()
        past = returns[-40:-20].std()

        ratio = recent / (past + 1e-6)

        # 波动上升 = 恐惧
        return float(-np.tanh(ratio - 1))
