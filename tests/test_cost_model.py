"""
测试 CostModel 交易成本计算
"""
import pytest
from quant_system.backtest.cost_model import (
    CostModel,
    NoCostModel,
    LowCostModel,
    HighCostModel
)


class TestCostModelBasic:
    """基础成本模型测试"""
    
    def test_buy_cost_normal(self):
        """测试正常买入成本"""
        model = CostModel(commission_rate=0.0003, min_commission=5.0)
        
        # 大额交易：10万元
        cost = model.calculate_buy_cost(price=100.0, size=1000)
        expected = 100.0 * 1000 * 0.0003  # 30元
        assert abs(cost - expected) < 0.01
    
    def test_buy_cost_minimum(self):
        """测试最低佣金限制"""
        model = CostModel(commission_rate=0.0003, min_commission=5.0)
        
        # 小额交易：1000元（佣金只有 0.3元，应取最低 5元）
        cost = model.calculate_buy_cost(price=10.0, size=100)
        assert cost == 5.0
    
    def test_sell_cost_with_stamp_duty(self):
        """测试卖出成本（含印花税）"""
        model = CostModel(
            commission_rate=0.0003,
            min_commission=5.0,
            stamp_duty_rate=0.001
        )
        
        # 卖出 10万元
        cost = model.calculate_sell_cost(price=100.0, size=1000)
        commission = 100.0 * 1000 * 0.0003  # 30元
        stamp_duty = 100.0 * 1000 * 0.001   # 100元
        expected = commission + stamp_duty   # 130元
        
        assert abs(cost - expected) < 0.01
    
    def test_get_total_cost_buy(self):
        """测试统一接口 - 买入"""
        model = CostModel()
        cost_buy = model.get_total_cost(price=100.0, size=1000, side="BUY")
        cost_calculate = model.calculate_buy_cost(price=100.0, size=1000)
        assert cost_buy == cost_calculate
    
    def test_get_total_cost_sell(self):
        """测试统一接口 - 卖出"""
        model = CostModel()
        cost_sell = model.get_total_cost(price=100.0, size=1000, side="SELL")
        cost_calculate = model.calculate_sell_cost(price=100.0, size=1000)
        assert cost_sell == cost_calculate
    
    def test_get_total_cost_invalid_side(self):
        """测试无效的交易方向"""
        model = CostModel()
        with pytest.raises(ValueError):
            model.get_total_cost(price=100.0, size=1000, side="INVALID")


class TestCostModelVariants:
    """不同成本模型测试"""
    
    def test_no_cost_model(self):
        """测试无成本模型"""
        model = NoCostModel()
        
        buy_cost = model.calculate_buy_cost(price=100.0, size=1000)
        sell_cost = model.calculate_sell_cost(price=100.0, size=1000)
        
        assert buy_cost == 0.0
        assert sell_cost == 0.0
    
    def test_low_cost_model(self):
        """测试低成本模型（万一）"""
        model = LowCostModel()
        
        # 10万元交易
        cost = model.calculate_buy_cost(price=100.0, size=1000)
        expected = 100.0 * 1000 * 0.0001  # 10元（万一）
        assert abs(cost - expected) < 0.01
    
    def test_high_cost_model(self):
        """测试高成本模型（万五）"""
        model = HighCostModel()
        
        # 10万元交易
        cost = model.calculate_buy_cost(price=100.0, size=1000)
        expected = 100.0 * 1000 * 0.0005  # 50元（万五）
        assert abs(cost - expected) < 0.01
    
    def test_cost_comparison(self):
        """测试不同成本模型对比"""
        no_cost = NoCostModel()
        low_cost = LowCostModel()
        standard_cost = CostModel()
        high_cost = HighCostModel()
        
        price, size = 100.0, 1000
        
        cost_no = no_cost.calculate_buy_cost(price, size)
        cost_low = low_cost.calculate_buy_cost(price, size)
        cost_std = standard_cost.calculate_buy_cost(price, size)
        cost_high = high_cost.calculate_buy_cost(price, size)
        
        # 成本应该递增
        assert cost_no < cost_low < cost_std < cost_high


class TestCostModelEdgeCases:
    """边界情况测试"""
    
    def test_zero_size(self):
        """测试零数量交易"""
        model = CostModel()
        cost = model.calculate_buy_cost(price=100.0, size=0)
        assert cost == 5.0  # 应该返回最低佣金
    
    def test_very_large_transaction(self):
        """测试大额交易"""
        model = CostModel()
        # 1亿元交易
        cost = model.calculate_buy_cost(price=100.0, size=1_000_000)
        expected = 100.0 * 1_000_000 * 0.0003  # 30000元
        assert abs(cost - expected) < 0.01
    
    def test_fractional_shares(self):
        """测试小数股数"""
        model = CostModel()
        cost = model.calculate_buy_cost(price=100.0, size=100.5)
        assert cost > 0  # 应该能处理小数