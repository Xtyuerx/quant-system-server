from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SELL_STOP = "SELL_STOP"
    HOLD = "HOLD"

class Signal:
    """
    回测信号对象
    """
    def __init__(self, type: SignalType):
        self.type = type

    def __repr__(self):
        return f"Signal(type={self.type.value})"
