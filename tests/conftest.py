"""
pytest 配置文件和共享 fixtures
"""
import pytest
import numpy as np
from quant_system.backtest.result import BacktestResult
from quant_system.backtest.trade import Trade


@pytest.fixture
def sample_equity_curve():
    """样本权益曲线"""
    return [100_000, 105_000, 110_000, 108_000, 115_000, 112_000, 120_000]


@pytest.fixture
def sample_trades():
    """样本交易记录"""
    return [
        Trade(price=100.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
        Trade(price=110.0, size=-1000, cash_after=110_000, position_after=0, type="EXIT"),
        Trade(price=105.0, size=1000, cash_after=0, position_after=1000, type="BUY"),
        Trade(price=115.0, size=-1000, cash_after=115_000, position_after=0, type="EXIT"),
    ]


@pytest.fixture
def sample_backtest_result(sample_equity_curve, sample_trades):
    """样本回测结果"""
    return BacktestResult(
        symbol="TEST",
        initial_cash=100_000,
        final_equity=120_000,
        equity_curve=sample_equity_curve,
        trades=sample_trades,
    )


@pytest.fixture
def simple_prices():
    """简单的价格序列（用于回测测试）"""
    return [100.0, 102.0, 98.0, 105.0, 103.0, 108.0, 110.0, 107.0, 112.0, 115.0]


# P3 相关 fixtures

@pytest.fixture
def trending_prices():
    """趋势性价格序列"""
    np.random.seed(42)
    prices = [100.0]
    for _ in range(99):
        trend = 0.1  # 上升趋势
        noise = np.random.normal(0, 1)
        prices.append(prices[-1] + trend + noise)
    return prices


@pytest.fixture
def volatile_prices():
    """高波动价格序列"""
    np.random.seed(42)
    prices = [100.0]
    for _ in range(99):
        change = np.random.normal(0, 5)  # 高波动
        prices.append(prices[-1] + change)
    return prices


@pytest.fixture
def long_price_series():
    """长价格序列（用于 Walk-Forward）"""
    np.random.seed(42)
    prices = [100.0]
    for _ in range(199):
        change = np.random.normal(0.1, 2)
        prices.append(max(prices[-1] + change, 50))  # 防止价格过低
    return prices