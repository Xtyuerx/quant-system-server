from enum import Enum

class Signal(Enum):
    LONG = 1
    SHORT = -1
    HOLD = 0

def sentiment_to_signal(sentiment: float) -> Signal:
    """
    简单规则：
      sentiment > 0.3 → 买入
      sentiment < -0.3 → 卖出
      否则 → 观望
    """
    if sentiment > 0.3:
        return Signal.LONG
    elif sentiment < -0.3:
        return Signal.SHORT
    else:
        return Signal.HOLD
