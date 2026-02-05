"""
滑点模型

模拟实际交易中的价格滑点：
- 固定滑点
- 比例滑点
- 基于成交量的滑点
"""
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class SlippageModel:
    """
    滑点模型基类
    
    滑点说明：
    - 买入时价格上滑（实际成交价更高）
    - 卖出时价格下滑（实际成交价更低）
    """
    pass


@dataclass
class FixedSlippage(SlippageModel):
    """
    固定滑点模型
    
    Attributes:
        slippage_bps: 滑点（基点），如 5 表示 0.05% = 万分之五
    """
    slippage_bps: int = 5  # 5 个基点 = 0.05%
    
    def apply_to_buy(self, price: float) -> float:
        """买入时价格上滑"""
        slippage = self.slippage_bps / 10000
        return price * (1 + slippage)
    
    def apply_to_sell(self, price: float) -> float:
        """卖出时价格下滑"""
        slippage = self.slippage_bps / 10000
        return price * (1 - slippage)


@dataclass
class ProportionalSlippage(SlippageModel):
    """
    比例滑点模型（根据交易金额）
    
    大额交易产生更大滑点
    """
    base_slippage_bps: int = 5      # 基础滑点
    size_impact_factor: float = 0.01  # 规模影响系数
    
    def apply_to_buy(self, price: float, size: float = 1000) -> float:
        """
        买入时价格上滑
        
        Args:
            price: 原始价格
            size: 交易数量（用于计算市场冲击）
        """
        # 基础滑点
        base_slip = self.base_slippage_bps / 10000
        
        # 市场冲击（交易量越大，冲击越大）
        market_impact = self.size_impact_factor * np.log(1 + size / 1000)
        
        total_slippage = base_slip + market_impact
        return price * (1 + total_slippage)
    
    def apply_to_sell(self, price: float, size: float = 1000) -> float:
        """卖出时价格下滑"""
        base_slip = self.base_slippage_bps / 10000
        market_impact = self.size_impact_factor * np.log(1 + size / 1000)
        
        total_slippage = base_slip + market_impact
        return price * (1 - total_slippage)


@dataclass
class VolumeBasedSlippage(SlippageModel):
    """
    基于成交量的滑点模型
    
    考虑实际市场流动性
    """
    daily_volume: float = 1_000_000  # 日均成交量
    impact_coefficient: float = 0.1  # 冲击系数
    
    def apply_to_buy(self, price: float, size: float, volume: Optional[float] = None) -> float:
        """
        买入时价格上滑
        
        Args:
            price: 原始价格
            size: 交易数量
            volume: 当日成交量（可选，默认使用日均值）
        """
        vol = volume if volume is not None else self.daily_volume
        
        # 交易量占比
        volume_ratio = size / vol
        
        # 市场冲击 = 系数 * sqrt(交易量占比)
        impact = self.impact_coefficient * np.sqrt(volume_ratio)
        
        return price * (1 + impact)
    
    def apply_to_sell(self, price: float, size: float, volume: Optional[float] = None) -> float:
        """卖出时价格下滑"""
        vol = volume if volume is not None else self.daily_volume
        volume_ratio = size / vol
        impact = self.impact_coefficient * np.sqrt(volume_ratio)
        
        return price * (1 - impact)


class NoSlippage(SlippageModel):
    """无滑点模型（用于测试）"""
    
    def apply_to_buy(self, price: float, **kwargs) -> float:
        return price
    
    def apply_to_sell(self, price: float, **kwargs) -> float:
        return price