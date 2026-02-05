"""
双均线策略（多参数示例）

用于演示参数热力图
"""
from typing import List
from quant_system.strategy.base import Strategy
from quant_system.enums.signal import SignalType


class DualMAStrategy(Strategy):
    """
    双均线策略
    
    Args:
        fast_window: 快速均线周期
        slow_window: 慢速均线周期
        threshold: 交叉阈值（可选，用于过滤虚假信号）
    """
    def __init__(
        self, 
        fast_window: int = 5, 
        slow_window: int = 20,
        threshold: float = 0.0
    ):
        if fast_window >= slow_window:
            raise ValueError("fast_window 必须小于 slow_window")
        
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.threshold = threshold
    
    def generate_signals(self, prices: List[float]) -> List[SignalType]:
        """
        生成交易信号
        
        策略逻辑：
        - 快速均线上穿慢速均线 → 买入
        - 快速均线下穿慢速均线 → 卖出
        """
        signals = []
        position = False  # 当前是否持仓
        
        for i in range(len(prices)):
            # 前期数据不足
            if i < self.slow_window:
                signals.append(SignalType.HOLD)
                continue
            
            # 计算快慢均线
            fast_ma = sum(prices[i - self.fast_window:i]) / self.fast_window
            slow_ma = sum(prices[i - self.slow_window:i]) / self.slow_window
            
            # 计算均线差值
            ma_diff = (fast_ma - slow_ma) / slow_ma
            
            # 金叉：买入
            if ma_diff > self.threshold and not position:
                signals.append(SignalType.BUY)
                position = True
            
            # 死叉：卖出
            elif ma_diff < -self.threshold and position:
                signals.append(SignalType.EXIT)
                position = False
            
            else:
                signals.append(SignalType.HOLD)
        
        return signals