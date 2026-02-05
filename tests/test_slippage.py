"""
测试滑点模型
"""
import pytest
from quant_system.backtest.slippage import (
    FixedSlippage,
    ProportionalSlippage,
    VolumeBasedSlippage,
    NoSlippage
)


class TestFixedSlippage:
    """固定滑点测试"""
    
    def test_default_slippage(self):
        """测试默认滑点（5 bps）"""
        slippage = FixedSlippage()
        
        original_price = 100.0
        buy_price = slippage.apply_to_buy(original_price)
        sell_price = slippage.apply_to_sell(original_price)
        
        # 5 bps = 0.05%
        assert abs(buy_price - 100.05) < 0.01
        assert abs(sell_price - 99.95) < 0.01
    
    def test_custom_slippage(self):
        """测试自定义滑点（10 bps）"""
        slippage = FixedSlippage(slippage_bps=10)
        
        original_price = 100.0
        buy_price = slippage.apply_to_buy(original_price)
        sell_price = slippage.apply_to_sell(original_price)
        
        # 10 bps = 0.1%
        assert abs(buy_price - 100.10) < 0.01
        assert abs(sell_price - 99.90) < 0.01
    
    def test_slippage_symmetry(self):
        """测试滑点对称性"""
        slippage = FixedSlippage(slippage_bps=5)
        
        price = 100.0
        buy_slip = slippage.apply_to_buy(price) - price
        sell_slip = price - slippage.apply_to_sell(price)
        
        # 买入和卖出的滑点应该相等
        assert abs(buy_slip - sell_slip) < 0.001


class TestProportionalSlippage:
    """比例滑点测试"""
    
    def test_small_trade(self):
        """测试小额交易"""
        slippage = ProportionalSlippage(
            base_slippage_bps=5,
            size_impact_factor=0.01
        )
        
        price = 100.0
        buy_price = slippage.apply_to_buy(price, size=100)
        
        # 小额交易，市场冲击很小
        assert buy_price > price
        assert buy_price < 100.20  # 放宽到 0.2%
    
    def test_large_trade(self):
        """测试大额交易"""
        slippage = ProportionalSlippage(
            base_slippage_bps=5,
            size_impact_factor=0.01
        )
        
        price = 100.0
        buy_price_small = slippage.apply_to_buy(price, size=100)
        buy_price_large = slippage.apply_to_buy(price, size=10000)
        
        # 大额交易滑点应该更大
        assert buy_price_large > buy_price_small
    
    def test_sell_slippage(self):
        """测试卖出滑点"""
        slippage = ProportionalSlippage()
        
        price = 100.0
        sell_price = slippage.apply_to_sell(price, size=1000)
        
        # 卖出价格应该低于原价
        assert sell_price < price


class TestVolumeBasedSlippage:
    """成交量滑点测试"""
    
    def test_normal_volume(self):
        """测试正常成交量"""
        slippage = VolumeBasedSlippage(
            daily_volume=1_000_000,
            impact_coefficient=0.1
        )
        
        price = 100.0
        size = 10_000  # 1% 的日均量
        buy_price = slippage.apply_to_buy(price, size)
        
        # 应该有一定滑点
        assert buy_price > price
        assert buy_price <= 101.0
    
    def test_high_volume_ratio(self):
        """测试高交易量占比"""
        slippage = VolumeBasedSlippage(
            daily_volume=1_000_000,
            impact_coefficient=0.1
        )
        
        price = 100.0
        small_size = 10_000
        large_size = 100_000  # 10% 的日均量
        
        buy_price_small = slippage.apply_to_buy(price, small_size)
        buy_price_large = slippage.apply_to_buy(price, large_size)
        
        # 大额交易冲击更大
        assert buy_price_large > buy_price_small
    
    def test_custom_volume(self):
        """测试自定义当日成交量"""
        slippage = VolumeBasedSlippage(daily_volume=1_000_000)
        
        price = 100.0
        size = 10_000
        
        # 当日成交量较大，冲击小
        buy_price_high_vol = slippage.apply_to_buy(price, size, volume=2_000_000)
        
        # 当日成交量较小，冲击大
        buy_price_low_vol = slippage.apply_to_buy(price, size, volume=500_000)
        
        assert buy_price_low_vol > buy_price_high_vol


class TestNoSlippage:
    """无滑点测试"""
    
    def test_no_slippage_buy(self):
        """测试无滑点买入"""
        slippage = NoSlippage()
        
        price = 100.0
        buy_price = slippage.apply_to_buy(price)
        
        assert buy_price == price
    
    def test_no_slippage_sell(self):
        """测试无滑点卖出"""
        slippage = NoSlippage()
        
        price = 100.0
        sell_price = slippage.apply_to_sell(price)
        
        assert sell_price == price