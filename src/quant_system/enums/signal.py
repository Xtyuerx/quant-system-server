from enum import IntEnum


class Signal(IntEnum):
    FLAT = 0     # 空仓
    LONG = 1     # 做多
    SHORT = -1   # 做空（先预留）
