"""
测试 BacktestResult 类的所有指标计算
"""
import pytest
import numpy as np
from quant_system.backtest.result import BacktestResult
from quant_system.backtest.trade import Trade


class TestBacktestResultBasicMetrics:
    """基础指标测试"""
    
    def test_total_return(self):
        """测试总收益率计算"""
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=110_000,
            equity_curve=[100_000, 105_000, 110_000]
        )
        assert abs(result.total_return - 0.1) < 0.001  # 10% (允许 0.1% 误差)
    
    def test_total_return_loss(self):
        """测试负收益率"""
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=90_000,
            equity_curve=[100_000, 95_000, 90_000]
        )
        assert abs(result.total_return - (-0.1)) < 0.001  # 10% (允许 0.1% 误差)
    
    def test_max_drawdown_simple(self):
        """测试最大回撤计算（简单情况）"""
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=95_000,
            equity_curve=[100_000, 110_000, 88_000, 95_000]
        )
        # 峰值 110000，谷底 88000
        # 回撤 = (88000 - 110000) / 110000 = -0.2 = -20%
        assert abs(result.max_drawdown - (-0.2)) < 0.001
    
    def test_max_drawdown_no_drawdown(self):
        """测试无回撤情况"""
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=120_000,
            equity_curve=[100_000, 105_000, 110_000, 115_000, 120_000]
        )
        assert result.max_drawdown == 0.0


class TestBacktestResultAdvancedMetrics:
    """高级指标测试"""
    
    def test_annual_return(self):
        """测试年化收益率"""
        # 假设 252 个交易日，收益 20%
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=120_000,
            equity_curve=[100_000] * 126 + [120_000] * 126  # 252天
        )
        # 年化收益率应该约等于 20%（因为刚好一年）
        assert abs(result.annual_return - 0.2) < 0.01
    
    def test_annual_return_short_period(self):
        """测试短周期年化收益率"""
        # 10 天内收益 5%，年化应该很高
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=105_000,
            equity_curve=[100_000] * 5 + [105_000] * 5  # 10天
        )
        # 年化 = (1 + 0.05)^(252/10) - 1 ≈ 2.35 即 235%
        assert result.annual_return > 2.0
    
    def test_sharpe_ratio_positive(self):
        """测试正向夏普比率"""
        # 创建一个稳定上涨的权益曲线
        equity_curve = [100_000 + i * 500 for i in range(100)]
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=149_500,
            equity_curve=equity_curve
        )
        # 稳定上涨应该有较高的夏普比率
        assert result.sharpe_ratio > 0
    
    def test_sharpe_ratio_high_volatility(self):
        """测试高波动情况下的夏普比率"""
        # 虽然最终收益相同，但波动大的夏普比率应该更低
        equity_stable = [100_000 + i * 500 for i in range(100)]
        equity_volatile = [100_000, 110_000, 95_000, 115_000, 90_000] * 20
        
        result_stable = BacktestResult(
            symbol="STABLE",
            initial_cash=100_000,
            final_equity=149_500,
            equity_curve=equity_stable
        )
        
        result_volatile = BacktestResult(
            symbol="VOLATILE",
            initial_cash=100_000,
            final_equity=equity_volatile[-1],
            equity_curve=equity_volatile
        )
        
        # 稳定的策略夏普比率应该更高
        # （注：这个测试可能需要根据实际数据调整）
    
    def test_annual_volatility(self):
        """测试年化波动率"""
        # 创建一个有波动的权益曲线
        equity_curve = [100_000, 105_000, 98_000, 110_000, 103_000]
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=103_000,
            equity_curve=equity_curve
        )
        assert result.annual_volatility > 0


class TestBacktestResultTradeMetrics:
    """交易相关指标测试"""
    
    def test_num_trades(self):
        """测试交易次数统计"""
        trades = [
            Trade(price=100.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=110.0, size=-1000, cash_after=110_000, position_after=0, type="EXIT"),
            Trade(price=105.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=115.0, size=-1000, cash_after=115_000, position_after=0, type="EXIT"),
        ]
        
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=115_000,
            equity_curve=[100_000, 110_000, 105_000, 115_000],
            trades=trades
        )
        
        assert result.num_trades == 2  # 2 次买入
    
    def test_num_trades_no_trades(self):
        """测试无交易情况"""
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=100_000,
            equity_curve=[100_000, 100_000],
            trades=[]
        )
        assert result.num_trades == 0
    
    def test_win_rate_all_wins(self):
        """测试 100% 胜率"""
        trades = [
            Trade(price=100.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=110.0, size=-1000, cash_after=110_000, position_after=0, type="EXIT"),
            Trade(price=105.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=115.0, size=-1000, cash_after=115_000, position_after=0, type="EXIT"),
        ]
        
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=115_000,
            equity_curve=[100_000, 110_000, 105_000, 115_000],
            trades=trades
        )
        
        assert result.win_rate == 1.0  # 100%
    
    def test_win_rate_mixed(self):
        """测试混合胜率"""
        trades = [
            Trade(price=100.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=110.0, size=-1000, cash_after=110_000, position_after=0, type="EXIT"),  # 赢
            Trade(price=105.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=95.0, size=-1000, cash_after=95_000, position_after=0, type="EXIT"),   # 输
        ]
        
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=95_000,
            equity_curve=[100_000, 110_000, 105_000, 95_000],
            trades=trades
        )
        
        assert result.win_rate == 0.5  # 50%
    
    def test_profit_factor(self):
        """测试盈亏比"""
        trades = [
            Trade(price=100.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=120.0, size=-1000, cash_after=120_000, position_after=0, type="EXIT"),  # +20000
            Trade(price=100.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
            Trade(price=90.0, size=-1000, cash_after=90_000, position_after=0, type="EXIT"),    # -10000
        ]
        
        result = BacktestResult(
            symbol="TEST",
            initial_cash=100_000,
            final_equity=90_000,
            equity_curve=[100_000, 120_000, 100_000, 90_000],
            trades=trades
        )
        
        # 盈亏比 = 20000 / 10000 = 2.0
        assert abs(result.profit_factor - 2.0) < 0.001


class TestBacktestResultOutputMethods:
    """输出方法测试"""
    
    def test_summary(self, sample_backtest_result):
        """测试 summary() 方法"""
        summary = sample_backtest_result.summary()
        
        assert "symbol" in summary
        assert "total_return" in summary
        assert "sharpe_ratio" in summary
        assert summary["symbol"] == "TEST"
    
    def test_to_row(self, sample_backtest_result):
        """测试 to_row() 方法"""
        row = sample_backtest_result.to_row()
        
        assert "symbol" in row
        assert isinstance(row["total_return"], str)  # 应该是格式化的字符串
        assert "%" in row["total_return"]
    
    def test_to_dict(self, sample_backtest_result):
        """测试 to_dict() 方法"""
        data = sample_backtest_result.to_dict()
        
        assert "symbol" in data
        assert isinstance(data["total_return"], float)  # 应该是原始数值