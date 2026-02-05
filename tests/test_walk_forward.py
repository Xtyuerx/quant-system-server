"""
测试 Walk-Forward 分析
"""
import pytest
from quant_system.runner.walk_forward import (
    WalkForwardConfig,
    WalkForwardResult,
    run_walk_forward_analysis
)
from quant_system.strategy.simple_ma import SimpleMAStrategy


@pytest.fixture
def long_price_series():
    """生成足够长的价格序列"""
    import numpy as np
    np.random.seed(42)
    
    # 生成 200 个价格点
    prices = [100.0]
    for _ in range(199):
        change = np.random.normal(0, 2)
        prices.append(prices[-1] + change)
    
    return prices


class TestWalkForwardConfig:
    """Walk-Forward 配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = WalkForwardConfig(
            train_window=100,
            test_window=20,
            step_size=20
        )
        
        assert config.train_window == 100
        assert config.test_window == 20
        assert config.step_size == 20


class TestWalkForwardResult:
    """Walk-Forward 结果测试"""
    
    def test_result_properties(self):
        """测试结果属性计算"""
        # 这个测试需要实际运行 walk-forward 才能验证
        # 这里只测试数据结构
        result = WalkForwardResult(
            train_results=[],
            test_results=[],
            best_params_history=[],
            combined_equity_curve=[100_000, 105_000, 110_000]
        )
        
        assert abs(result.total_return - 0.1) < 0.001  # 允许误差


class TestWalkForwardAnalysis:
    """Walk-Forward 分析集成测试"""
    
    def test_basic_walk_forward(self, long_price_series):
        """测试基础 Walk-Forward 分析"""
        config = WalkForwardConfig(
            train_window=50,
            test_window=20,
            step_size=20
        )
        
        result = run_walk_forward_analysis(
            prices=long_price_series,
            strategy_cls=SimpleMAStrategy,
            param_grid={"window": [3, 5, 10]},
            config=config,
            optimization_metric="sharpe_ratio"
        )
        
        # 验证结果结构
        assert len(result.train_results) > 0
        assert len(result.test_results) > 0
        assert len(result.best_params_history) > 0
        assert len(result.combined_equity_curve) > 0
        
        # 验证训练和测试结果数量一致
        assert len(result.train_results) == len(result.test_results)
    
    def test_walk_forward_params_tracking(self, long_price_series):
        """测试参数追踪"""
        config = WalkForwardConfig(
            train_window=50,
            test_window=20,
            step_size=20
        )
        
        result = run_walk_forward_analysis(
            prices=long_price_series,
            strategy_cls=SimpleMAStrategy,
            param_grid={"window": [3, 5, 10]},
            config=config
        )
        
        # 每轮应该记录最优参数
        for params in result.best_params_history:
            assert "window" in params
            assert params["window"] in [3, 5, 10]
    
    def test_insufficient_data(self):
        """测试数据不足的情况"""
        short_prices = [100.0] * 30  # 只有 30 个点
        
        config = WalkForwardConfig(
            train_window=50,
            test_window=20,
            step_size=20
        )
        
        result = run_walk_forward_analysis(
            prices=short_prices,
            strategy_cls=SimpleMAStrategy,
            param_grid={"window": [3, 5]},
            config=config
        )
        
        # 数据不足，不应该有结果
        assert len(result.train_results) == 0
        assert len(result.test_results) == 0