import numpy as np


def volume_sentiment(volume: np.ndarray, window: int = 20) -> float:
    """
    放量 = 情绪升温
    """
    if len(volume) < window * 2:
        return 0.0

    recent = volume[-window:]
    past = volume[-window*2:-window]

    ratio = recent.mean() / (past.mean() + 1e-6)

    # 映射到 -1 ~ +1
    return float(np.tanh(ratio - 1))
