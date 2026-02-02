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
        parts = [
            f"final_equity={self.final_equity:.2f}",
            f"total_return={self.total_return:.2%}",
            f"max_drawdown={self.max_drawdown:.2%}",
        ]
        return f"BacktestResult({', '.join(parts)})"