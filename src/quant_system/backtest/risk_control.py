"""
风险控制模块

实现各种风控策略：
- 最大回撤限制
- 止损/止盈
- 最大仓位限制
- 单日最大亏损限制
"""
from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class RiskControl:
    """
    风险控制配置
    
    Attributes:
        max_drawdown_limit: 最大回撤限制（触发强平），如 -0.2 表示 -20%
        max_position_ratio: 最大仓位比例，如 1.0 表示满仓，0.5 表示半仓
        stop_loss_pct: 单笔交易止损比例，如 -0.05 表示 -5%
        take_profit_pct: 单笔交易止盈比例，如 0.10 表示 10%
        max_daily_loss: 单日最大亏损限制，如 -0.05 表示 -5%
        enabled: 是否启用风控
    """
    max_drawdown_limit: float = -0.2         # -20% 触发强平
    max_position_ratio: float = 1.0          # 100% 最大仓位
    stop_loss_pct: Optional[float] = None    # 单笔止损（None 表示不启用）
    take_profit_pct: Optional[float] = None  # 单笔止盈（None 表示不启用）
    max_daily_loss: Optional[float] = None   # 单日最大亏损
    enabled: bool = True


class RiskMonitor:
    """
    风险监控器
    
    用于实时监控交易过程中的风险指标
    """
    
    def __init__(self, risk_control: RiskControl, initial_cash: float):
        self.risk_control = risk_control
        self.initial_cash = initial_cash
        self.daily_start_equity: Optional[float] = None
        self.position_entry_price: Optional[float] = None
        self.force_exit_triggered = False
        
    def check_max_drawdown(self, equity_curve: List[float]) -> bool:
        """
        检查是否触发最大回撤限制
        
        Returns:
            True: 触发强制平仓
            False: 未触发
        """
        if not self.risk_control.enabled:
            return False
            
        if len(equity_curve) < 2:
            return False
        
        current_drawdown = self._calculate_current_drawdown(equity_curve)
        
        if current_drawdown <= self.risk_control.max_drawdown_limit:
            self.force_exit_triggered = True
            return True
        
        return False
    
    def check_stop_loss(self, entry_price: float, current_price: float) -> bool:
        """
        检查是否触发止损
        
        Args:
            entry_price: 买入价格
            current_price: 当前价格
            
        Returns:
            True: 触发止损
            False: 未触发
        """
        if not self.risk_control.enabled:
            return False
            
        if self.risk_control.stop_loss_pct is None:
            return False
        
        # 计算当前收益率
        return_pct = (current_price - entry_price) / entry_price
        
        if return_pct <= self.risk_control.stop_loss_pct:
            return True
        
        return False
    
    def check_take_profit(self, entry_price: float, current_price: float) -> bool:
        """
        检查是否触发止盈
        
        Args:
            entry_price: 买入价格
            current_price: 当前价格
            
        Returns:
            True: 触发止盈
            False: 未触发
        """
        if not self.risk_control.enabled:
            return False
            
        if self.risk_control.take_profit_pct is None:
            return False
        
        # 计算当前收益率
        return_pct = (current_price - entry_price) / entry_price
        
        if return_pct >= self.risk_control.take_profit_pct:
            return True
        
        return False
    
    def check_daily_loss_limit(self, current_equity: float) -> bool:
        """
        检查是否触发单日亏损限制
        
        Args:
            current_equity: 当前权益
            
        Returns:
            True: 触发限制，应停止交易
            False: 未触发
        """
        if not self.risk_control.enabled:
            return False
            
        if self.risk_control.max_daily_loss is None:
            return False
        
        if self.daily_start_equity is None:
            self.daily_start_equity = current_equity
            return False
        
        # 计算今日损失
        daily_return = (current_equity - self.daily_start_equity) / self.daily_start_equity
        
        if daily_return <= self.risk_control.max_daily_loss:
            return True
        
        return False
    
    def get_position_size(
        self, 
        cash: float, 
        price: float,
        target_ratio: float = 1.0
    ) -> float:
        """
        计算仓位大小（考虑最大仓位限制）
        
        Args:
            cash: 可用现金
            price: 当前价格
            target_ratio: 目标仓位比例（如 1.0 表示满仓）
            
        Returns:
            实际可买入的股数
        """
        if not self.risk_control.enabled:
            return cash * target_ratio / price
        
        # 应用最大仓位限制
        actual_ratio = min(target_ratio, self.risk_control.max_position_ratio)
        
        return cash * actual_ratio / price
    
    def _calculate_current_drawdown(self, equity_curve: List[float]) -> float:
        """计算当前回撤"""
        equity_array = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - peak) / peak
        return float(drawdown[-1])
    
    def reset_daily_monitor(self, current_equity: float):
        """重置日内监控（用于新的交易日）"""
        self.daily_start_equity = current_equity
    
    def set_entry_price(self, price: float):
        """记录开仓价格"""
        self.position_entry_price = price
    
    def clear_position(self):
        """清除持仓记录"""
        self.position_entry_price = None


# 预定义的风控配置
class ConservativeRiskControl(RiskControl):
    """保守型风控（适合稳健投资者）"""
    def __init__(self):
        super().__init__(
            max_drawdown_limit=-0.1,    # -10% 强平
            max_position_ratio=0.7,     # 70% 最大仓位
            stop_loss_pct=-0.03,        # -3% 止损
            take_profit_pct=0.08,       # 8% 止盈
            max_daily_loss=-0.02,       # -2% 日内止损
        )


class AggressiveRiskControl(RiskControl):
    """激进型风控（适合进取投资者）"""
    def __init__(self):
        super().__init__(
            max_drawdown_limit=-0.3,    # -30% 强平
            max_position_ratio=1.0,     # 100% 满仓
            stop_loss_pct=-0.10,        # -10% 止损
            take_profit_pct=0.20,       # 20% 止盈
            max_daily_loss=None,        # 不限制日内亏损
        )


class NoRiskControl(RiskControl):
    """无风控（用于测试）"""
    def __init__(self):
        super().__init__(
            max_drawdown_limit=-1.0,    # 实际上不会触发
            max_position_ratio=1.0,
            stop_loss_pct=None,
            take_profit_pct=None,
            max_daily_loss=None,
            enabled=False,
        )