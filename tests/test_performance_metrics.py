"""
测试性能指标计算函数
"""
import pytest
from quant_system.metrics.performance import total_return, max_drawdown


class TestTotalReturn:
    """总收益率测试"""
    
    def test_positive_return(self):
        """测试正收益"""
        equity_curve = [100_000, 105_000, 110_000]
        result = total_return(equity_curve)
        assert abs(result - 0.1) < 0.001  # 10%
    
    def test_negative_return(self):
        """测试负收益"""
        equity_curve = [100_000, 95_000, 90_000]
        result = total_return(equity_curve)
        assert abs(result - (-0.1)) < 0.001  # -10%
    
    def test_no_change(self):
        """测试无变化"""
        equity_curve = [100_000, 100_000, 100_000]
        result = total_return(equity_curve)
        assert result == 0.0
    
    def test_empty_curve(self):
        """测试空曲线"""
        equity_curve = []
        result = total_return(equity_curve)
        assert result == 0.0


class TestMaxDrawdown:
    """最大回撤测试"""
    
    def test_simple_drawdown(self):
        """测试简单回撤"""
        equity_curve = [100_000, 110_000, 88_000, 95_000]
        result = max_drawdown(equity_curve)
        # 峰值 110000，谷底 88000，回撤 -20%
        expected = (88_000 - 110_000) / 110_000
        assert abs(result - expected) < 0.001
    
    def test_no_drawdown(self):
        """测试无回撤（持续上涨）"""
        equity_curve = [100_000, 105_000, 110_000, 115_000]
        result = max_drawdown(equity_curve)
        assert result == 0.0
    
    def test_multiple_drawdowns(self):
        """测试多次回撤（返回最大的）"""
        equity_curve = [
            100_000,  # 起点
            110_000,  # 峰值1
            105_000,  # 回撤1: -4.5%
            115_000,  # 峰值2
            92_000,   # 回撤2: -20% ← 最大
            100_000   # 恢复
        ]
        result = max_drawdown(equity_curve)
        expected = (92_000 - 115_000) / 115_000  # -20%
        assert abs(result - expected) < 0.001