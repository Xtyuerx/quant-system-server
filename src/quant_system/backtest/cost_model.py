from dataclasses import dataclass


@dataclass
class CostModel:
    """
    交易成本模型
    
    适用于 A 股市场：
    - 佣金：双向收取，最低 5 元
    - 印花税：仅卖出收取（千一）
    """
    commission_rate: float = 0.0003  # 万三佣金（0.03%）
    min_commission: float = 5.0      # 最低佣金 5 元
    stamp_duty_rate: float = 0.001   # 千一印花税（仅卖出）
    
    def calculate_buy_cost(self, price: float, size: float) -> float:
        """
        计算买入成本
        
        Args:
            price: 买入价格
            size: 买入数量
            
        Returns:
            总成本（佣金）
        """
        transaction_value = price * size
        commission = max(
            transaction_value * self.commission_rate,
            self.min_commission
        )
        return commission
    
    def calculate_sell_cost(self, price: float, size: float) -> float:
        """
        计算卖出成本
        
        Args:
            price: 卖出价格
            size: 卖出数量
            
        Returns:
            总成本（佣金 + 印花税）
        """
        transaction_value = price * size
        
        # 佣金
        commission = max(
            transaction_value * self.commission_rate,
            self.min_commission
        )
        
        # 印花税（仅卖出）
        stamp_duty = transaction_value * self.stamp_duty_rate
        
        return commission + stamp_duty
    
    def get_total_cost(self, price: float, size: float, side: str) -> float:
        """
        统一接口：获取交易成本
        
        Args:
            price: 价格
            size: 数量
            side: "BUY" 或 "SELL"
        """
        if side == "BUY":
            return self.calculate_buy_cost(price, size)
        elif side == "SELL":
            return self.calculate_sell_cost(price, size)
        else:
            raise ValueError(f"Unknown side: {side}")


# 预定义的成本模型
class NoCostModel(CostModel):
    """无成本模型（用于对比）"""
    def __init__(self):
        super().__init__(
            commission_rate=0.0,
            min_commission=0.0,
            stamp_duty_rate=0.0
        )


class LowCostModel(CostModel):
    """低成本模型（万一）"""
    def __init__(self):
        super().__init__(
            commission_rate=0.0001,  # 万一
            min_commission=5.0,
            stamp_duty_rate=0.001
        )


class HighCostModel(CostModel):
    """高成本模型（万五）"""
    def __init__(self):
        super().__init__(
            commission_rate=0.0005,  # 万五
            min_commission=5.0,
            stamp_duty_rate=0.001
        )