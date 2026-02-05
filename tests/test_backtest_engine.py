"""
测试 BacktestEngine 回测引擎
"""
import pytest
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.signal import SignalType
from quant_system.backtest.cost_model import CostModel, NoCostModel
from quant_system.enums.signal import SignalType as SignalEnum


@pytest.fixture
def simple_prices():
    """简单的价格序列"""
    return [100.0, 105.0, 110.0, 108.0, 115.0, 120.0, 118.0, 125.0]


@pytest.fixture
def buy_hold_signals(simple_prices):
    """买入并持有信号"""
    signals = [SignalEnum.BUY] + [SignalEnum.HOLD] * (len(simple_prices) - 1)
    return signals


@pytest.fixture
def buy_sell_signals(simple_prices):
    """买入-卖出信号"""
    signals = [
        SignalEnum.BUY,   # 100 买入
        SignalEnum.HOLD,
        SignalEnum.EXIT,  # 110 卖出
        SignalEnum.HOLD,
        SignalEnum.BUY,   # 115 买入
        SignalEnum.HOLD,
        SignalEnum.HOLD,
        SignalEnum.EXIT,  # 125 卖出
    ]
    return signals


class TestBacktestEngineBasic:
    """基础回测引擎测试"""
    
    def test_buy_and_hold(self, simple_prices, buy_hold_signals):
        """测试买入持有策略"""
        engine = BacktestEngine(
            prices=simple_prices,
            signals=buy_hold_signals,
            symbol="TEST",
            initial_cash=100_000,
            cost_model=NoCostModel()  # 无成本便于验证
        )
        
        result = engine.run()
        
        # 验证基本属性
        assert result.symbol == "TEST"
        assert result.initial_cash == 100_000
        
        # 买入价 100，卖出价（强制平仓）125
        # 收益率应该约为 25%
        assert result.total_return > 0.24
        assert result.total_return < 0.26
    
    def test_multiple_trades(self, simple_prices, buy_sell_signals):
        """测试多次交易"""
        engine = BacktestEngine(
            prices=simple_prices,
            signals=buy_sell_signals,
            symbol="TEST",
            initial_cash=100_000,
            cost_model=NoCostModel()
        )
        
        result = engine.run()
        
        # 应该有 2 次买入交易
        assert result.num_trades == 2
        
        # 应该有 4 条交易记录（2买2卖）
        assert len(result.trades) == 4
    
    def test_no_trades(self, simple_prices):
        """测试无交易（一直 HOLD）"""
        signals = [SignalEnum.HOLD] * len(simple_prices)
        
        engine = BacktestEngine(
            prices=simple_prices,
            signals=signals,
            symbol="TEST",
            initial_cash=100_000,
        )
        
        result = engine.run()
        
        # 应该无交易
        assert result.num_trades == 0
        # 资金应该不变
        assert result.final_equity == 100_000


class TestBacktestEngineWithCosts:
    """带成本的回测测试"""
    
    def test_cost_impact(self, simple_prices, buy_hold_signals):
        """测试成本影响"""
        # 无成本回测
        engine_no_cost = BacktestEngine(
            prices=simple_prices,
            signals=buy_hold_signals,
            symbol="TEST",
            initial_cash=100_000,
            cost_model=NoCostModel()
        )
        result_no_cost = engine_no_cost.run()
        
        # 有成本回测
        engine_with_cost = BacktestEngine(
            prices=simple_prices,
            signals=buy_hold_signals,
            symbol="TEST",
            initial_cash=100_000,
            cost_model=CostModel()
        )
        result_with_cost = engine_with_cost.run()
        
        # 有成本的收益应该更低
        assert result_with_cost.final_equity < result_no_cost.final_equity
        
        # 成本差异应该合理（不会太大）
        cost_diff = result_no_cost.final_equity - result_with_cost.final_equity
        assert cost_diff > 0
        assert cost_diff < 1000  # 假设成本不超过 1000 元


class TestBacktestEngineEdgeCases:
    """边界情况测试"""
    
    def test_single_price_point(self):
        """测试单个价格点"""
        engine = BacktestEngine(
            prices=[100.0],
            signals=[SignalEnum.BUY],
            symbol="TEST",
            initial_cash=100_000,
        )
        
        result = engine.run()
        # 应该能正常运行
        assert len(result.equity_curve) == 1
    
    def test_empty_signals_handling(self):
        """测试信号数量不匹配（应该有错误处理）"""
        # 这个测试取决于您的实际实现
        # 如果需要，可以添加参数验证
        pass