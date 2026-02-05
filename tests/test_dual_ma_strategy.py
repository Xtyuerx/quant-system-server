"""
测试双均线策略
"""
import pytest
from quant_system.strategy.dual_ma import DualMAStrategy
from quant_system.enums.signal import SignalType


class TestDualMAStrategy:
    """双均线策略测试"""
    
    def test_strategy_initialization(self):
        """测试策略初始化"""
        strategy = DualMAStrategy(fast_window=5, slow_window=20)
        
        assert strategy.fast_window == 5
        assert strategy.slow_window == 20
        assert strategy.threshold == 0.0
    
    def test_invalid_window_combination(self):
        """测试无效的窗口组合"""
        with pytest.raises(ValueError):
            DualMAStrategy(fast_window=20, slow_window=10)
    
    def test_signal_generation_uptrend(self):
        """测试上升趋势信号"""
        strategy = DualMAStrategy(fast_window=3, slow_window=5)
        
        # 模拟上升趋势
        prices = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
        signals = strategy.generate_signals(prices)
        
        # 应该有买入信号
        assert SignalType.BUY in signals
        
        # 前 slow_window 个信号应该是 HOLD
        for i in range(strategy.slow_window):
            assert signals[i] == SignalType.HOLD
    
    def test_signal_generation_downtrend(self):
        """测试下降趋势信号"""
        strategy = DualMAStrategy(fast_window=3, slow_window=5)
        
        # 先上升再下降
        prices = [100, 105, 110, 115, 120, 115, 110, 105, 100, 95]
        signals = strategy.generate_signals(prices)
        
        # 应该有买入和卖出信号
        assert SignalType.BUY in signals
        assert SignalType.EXIT in signals
    
    def test_threshold_filter(self):
        """测试阈值过滤"""
        strategy_no_threshold = DualMAStrategy(
            fast_window=3, 
            slow_window=5,
            threshold=0.0
        )
        
        strategy_with_threshold = DualMAStrategy(
            fast_window=3,
            slow_window=5,
            threshold=0.05  # 5% 阈值
        )
        
        # 小幅波动的价格
        prices = [100, 101, 102, 103, 104, 103, 102, 101, 100, 99]
        
        signals_no_filter = strategy_no_threshold.generate_signals(prices)
        signals_with_filter = strategy_with_threshold.generate_signals(prices)
        
        # 有阈值的策略应该产生更少的交易信号
        buy_count_no_filter = signals_no_filter.count(SignalType.BUY)
        buy_count_with_filter = signals_with_filter.count(SignalType.BUY)
        
        assert buy_count_with_filter <= buy_count_no_filter
    
    def test_position_tracking(self):
        """测试持仓状态追踪"""
        strategy = DualMAStrategy(fast_window=3, slow_window=5)
        
        # 模拟价格序列
        prices = [100, 105, 110, 115, 120, 115, 110, 105, 100, 95]
        signals = strategy.generate_signals(prices)
        
        position = False
        for signal in signals:
            if signal == SignalType.BUY:
                assert not position  # 买入前应该空仓
                position = True
            elif signal == SignalType.EXIT:
                assert position  # 卖出前应该持仓
                position = False


class TestDualMAStrategyEdgeCases:
    """边界情况测试"""
    
    def test_short_price_series(self):
        """测试短价格序列"""
        strategy = DualMAStrategy(fast_window=3, slow_window=5)
        
        # 只有 3 个价格点
        prices = [100, 101, 102]
        signals = strategy.generate_signals(prices)
        
        # 所有信号应该是 HOLD
        assert all(s == SignalType.HOLD for s in signals)
    
    def test_flat_prices(self):
        """测试横盘价格"""
        strategy = DualMAStrategy(fast_window=3, slow_window=5)
        
        # 价格不变
        prices = [100] * 10
        signals = strategy.generate_signals(prices)
        
        # 不应该产生交易信号（除了前 slow_window 个 HOLD）
        assert signals.count(SignalType.BUY) == 0
        assert signals.count(SignalType.EXIT) == 0
    
    def test_extreme_volatility(self):
        """测试极端波动"""
        strategy = DualMAStrategy(fast_window=3, slow_window=5)
        
        # 剧烈波动
        prices = [100, 200, 50, 150, 75, 125, 100, 150, 100, 120]
        signals = strategy.generate_signals(prices)
        
        # 应该能正常生成信号
        assert len(signals) == len(prices)