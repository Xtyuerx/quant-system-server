import numpy as np


def momentum_sentiment(close: np.ndarray, window: int = 20) -> float:
    """
    趋势一致性
    """
    if len(close) < window:
        return 0.0

    ret = close[-1] / close[-window] - 1
    return float(np.tanh(ret * 5))
