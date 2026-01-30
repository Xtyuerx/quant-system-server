from dataclasses import dataclass

@dataclass
class Trade:
    price: float       # 成交价格
    size: float        # 买入或卖出数量（正表示买，负表示卖）
    cash_after: float  # 成交后现金
    position_after: float  # 成交后持仓
    type: str          # 'BUY' 或 'SELL'
