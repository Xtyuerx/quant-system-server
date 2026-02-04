from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    EXIT = "EXIT"
    SELL_STOP = "SELL_STOP"  # 预留给风控
    HOLD = "HOLD"

class Signal:
    """
    回测信号对象
    """
    def __init__(self, type: SignalType):
        self.type = type
        self.name = type.value  # ✅ 保持兼容性

    def __repr__(self):
        return f"Signal({self.type.value})"  # ✅ 修正