"""
测试风险控制模块
"""
import pytest
from quant_system.backtest.risk_control import (
    RiskControl,
    RiskMonitor,
    ConservativeRiskControl,
    AggressiveRiskControl,
    NoRiskControl
)


class TestRiskControl:
    """RiskControl 配置测试"""
    
    def test_default_risk_control(self):
        """测试默认风控配置"""
        rc = RiskControl()
        
        assert rc.max_drawdown_limit == -0.2
        assert rc.max_position_ratio == 1.0
        assert rc.stop_loss_pct is None
        assert rc.take_profit_pct is None
        assert rc.enabled is True
    
    def test_custom_risk_control(self):
        """测试自定义风控配置"""
        rc = RiskControl(
            max_drawdown_limit=-0.15,
            max_position_ratio=0.8,
            stop_loss_pct=-0.05,
            take_profit_pct=0.10
        )
        
        assert rc.max_drawdown_limit == -0.15
        assert rc.max_position_ratio == 0.8
        assert rc.stop_loss_pct == -0.05
        assert rc.take_profit_pct == 0.10


class TestRiskMonitor:
    """RiskMonitor 测试"""
    
    def test_check_max_drawdown_no_trigger(self):
        """测试未触发最大回撤"""
        rc = RiskControl(max_drawdown_limit=-0.2)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        equity_curve = [100_000, 105_000, 110_000, 108_000]
        
        # 当前回撤只有 -1.8%，未触发 -20%
        assert monitor.check_max_drawdown(equity_curve) is False
    
    def test_check_max_drawdown_triggered(self):
        """测试触发最大回撤"""
        rc = RiskControl(max_drawdown_limit=-0.2)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        equity_curve = [100_000, 110_000, 85_000]  # -22.7% 回撤
        
        assert monitor.check_max_drawdown(equity_curve) is True
        assert monitor.force_exit_triggered is True
    
    def test_check_stop_loss_not_triggered(self):
        """测试止损未触发"""
        rc = RiskControl(stop_loss_pct=-0.05)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        entry_price = 100.0
        current_price = 98.0  # -2% 亏损
        
        assert monitor.check_stop_loss(entry_price, current_price) is False
    
    def test_check_stop_loss_triggered(self):
        """测试止损触发"""
        rc = RiskControl(stop_loss_pct=-0.05)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        entry_price = 100.0
        current_price = 94.0  # -6% 亏损
        
        assert monitor.check_stop_loss(entry_price, current_price) is True
    
    def test_check_take_profit_not_triggered(self):
        """测试止盈未触发"""
        rc = RiskControl(take_profit_pct=0.10)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        entry_price = 100.0
        current_price = 105.0  # +5% 盈利
        
        assert monitor.check_take_profit(entry_price, current_price) is False
    
    def test_check_take_profit_triggered(self):
        """测试止盈触发"""
        rc = RiskControl(take_profit_pct=0.10)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        entry_price = 100.0
        current_price = 115.0  # +15% 盈利
        
        assert monitor.check_take_profit(entry_price, current_price) is True
    
    def test_get_position_size_no_limit(self):
        """测试无仓位限制"""
        rc = RiskControl(max_position_ratio=1.0)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        size = monitor.get_position_size(cash=100_000, price=100.0, target_ratio=1.0)
        
        assert abs(size - 1000.0) < 0.01  # 100000 / 100 = 1000
    
    def test_get_position_size_with_limit(self):
        """测试有仓位限制"""
        rc = RiskControl(max_position_ratio=0.5)
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        size = monitor.get_position_size(cash=100_000, price=100.0, target_ratio=1.0)
        
        assert abs(size - 500.0) < 0.01  # 限制在 50%
    
    def test_disabled_risk_control(self):
        """测试禁用风控"""
        rc = RiskControl(
            max_drawdown_limit=-0.2,
            stop_loss_pct=-0.05,
            enabled=False
        )
        monitor = RiskMonitor(rc, initial_cash=100_000)
        
        # 即使触发条件，也应该返回 False
        equity_curve = [100_000, 110_000, 80_000]
        assert monitor.check_max_drawdown(equity_curve) is False
        
        assert monitor.check_stop_loss(entry_price=100.0, current_price=90.0) is False


class TestPredefinedRiskControls:
    """预定义风控配置测试"""
    
    def test_conservative_risk_control(self):
        """测试保守型风控"""
        rc = ConservativeRiskControl()
        
        assert rc.max_drawdown_limit == -0.1
        assert rc.max_position_ratio == 0.7
        assert rc.stop_loss_pct == -0.03
        assert rc.take_profit_pct == 0.08
    
    def test_aggressive_risk_control(self):
        """测试激进型风控"""
        rc = AggressiveRiskControl()
        
        assert rc.max_drawdown_limit == -0.3
        assert rc.max_position_ratio == 1.0
        assert rc.stop_loss_pct == -0.10
        assert rc.take_profit_pct == 0.20
    
    def test_no_risk_control(self):
        """测试无风控"""
        rc = NoRiskControl()
        
        assert rc.enabled is False
        assert rc.max_drawdown_limit == -1.0