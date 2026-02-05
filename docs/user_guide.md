# 用户指南

## 目录
- [数据管理](#数据管理)
- [策略开发](#策略开发)
- [回测执行](#回测执行)
- [性能分析](#性能分析)
- [参数优化](#参数优化)
- [风险控制](#风险控制)
- [可视化](#可视化)

---

## 数据管理

### 数据格式要求

标准 CSV 格式：
\`\`\`csv
date,price
2024-01-01,100.50
2024-01-02,101.20
2024-01-03,99.80
\`\`\`

### 加载数据

\`\`\`python
from quant_system.data.price_feed import load_prices_from_csv

# 基础加载
prices = load_prices_from_csv("AAPL.csv")

# 加载特定列
from quant_system.data.price_feed import load_series_from_csv
close_prices = load_series_from_csv("AAPL.csv", column="close")

# 加载多列
from quant_system.data.price_feed import load_columns_from_csv
data = load_columns_from_csv("AAPL.csv", columns=["close", "volume"])
\`\`\`

### 数据预处理

\`\`\`python
# 处理缺失值
prices = [p for p in prices if p > 0]  # 移除无效价格

# 数据归一化（可选）
import numpy as np
prices_normalized = (np.array(prices) - np.mean(prices)) / np.std(prices)
\`\`\`

---

## 策略开发

### 策略基类

\`\`\`python
from quant_system.strategy.base import Strategy
from quant_system.enums.signal import SignalType
from typing import List

class MyCustomStrategy(Strategy):
    """自定义策略"""
    
    def __init__(self, param1: int, param2: float):
        """初始化参数"""
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, prices: List[float]) -> List[SignalType]:
        """
        生成交易信号
        
        Args:
            prices: 价格序列
            
        Returns:
            信号序列（与 prices 长度相同）
        """
        signals = []
        
        for i, price in enumerate(prices):
            # 实现你的策略逻辑
            if i < 10:
                signals.append(SignalType.HOLD)
            elif self._should_buy(prices, i):
                signals.append(SignalType.BUY)
            elif self._should_exit(prices, i):
                signals.append(SignalType.EXIT)
            else:
                signals.append(SignalType.HOLD)
        
        return signals
    
    def _should_buy(self, prices: List[float], index: int) -> bool:
        """买入条件"""
        # 示例：价格突破 N 日高点
        lookback = prices[max(0, index-self.param1):index]
        return price > max(lookback) if lookback else False
    
    def _should_exit(self, prices: List[float], index: int) -> bool:
        """卖出条件"""
        # 实现你的逻辑
        return False
\`\`\`

### 内置策略

#### 1. 简单均线策略

\`\`\`python
from quant_system.strategy.simple_ma import SimpleMAStrategy

strategy = SimpleMAStrategy(window=20)
\`\`\`

**逻辑**：价格高于均线买入，低于均线持有。

#### 2. 双均线策略

\`\`\`python
from quant_system.strategy.dual_ma import DualMAStrategy

strategy = DualMAStrategy(
    fast_window=5,
    slow_window=20,
    threshold=0.01  # 1% 阈值，过滤虚假信号
)
\`\`\`

**逻辑**：快线上穿慢线买入，下穿卖出。

---

## 回测执行

### 基础回测

\`\`\`python
from quant_system.backtest.engine import BacktestEngine

engine = BacktestEngine(
    prices=prices,
    signals=signals,
    symbol="AAPL",
    initial_cash=100_000
)

result = engine.run()
\`\`\`

### 完整配置回测

\`\`\`python
from quant_system.backtest.cost_model import CostModel
from quant_system.backtest.slippage import FixedSlippage
from quant_system.backtest.risk_control import ConservativeRiskControl

engine = BacktestEngine(
    prices=prices,
    signals=signals,
    symbol="AAPL",
    initial_cash=100_000,
    
    # 交易成本
    cost_model=CostModel(
        commission_rate=0.0003,
        min_commission=5.0,
        stamp_duty_rate=0.001
    ),
    
    # 滑点
    slippage_model=FixedSlippage(slippage_bps=5),
    
    # 风控
    risk_control=ConservativeRiskControl()
)

result = engine.run()
\`\`\`

---

## 性能分析

### 查看所有指标

\`\`\`python
# 字典格式
summary = result.summary()
print(summary)

# 格式化输出
row = result.to_row()
for key, value in row.items():
    print(f"{key}: {value}")
\`\`\`

### 单个指标访问

\`\`\`python
print(f"总收益率: {result.total_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")
print(f"胜率: {result.win_rate:.1%}")
\`\`\`

### 交易明细

\`\`\`python
for trade in result.trades:
    print(f"{trade.type}: ${trade.price:.2f} x {trade.size:.0f}")
\`\`\`

---

## 参数优化

### 网格搜索

\`\`\`python
from quant_system.runner.param_scan import run_param_scan

results = run_param_scan(
    symbol="AAPL",
    prices=prices,
    strategy_cls=DualMAStrategy,
    param_grid={
        "fast_window": [3, 5, 10, 20],
        "slow_window": [20, 30, 50, 100],
        "threshold": [0.0, 0.01, 0.02]
    }
)

# 查看最佳结果
best = results.sort_by("sharpe_ratio").best("sharpe_ratio")
print(f"最优参数: {best.params}")
print(f"夏普比率: {best.sharpe_ratio:.2f}")
\`\`\`

### Walk-Forward 分析

\`\`\`python
from quant_system.runner.walk_forward import (
    run_walk_forward_analysis,
    WalkForwardConfig
)

config = WalkForwardConfig(
    train_window=252,  # 1 年训练
    test_window=63,    # 3 个月测试
    step_size=63       # 滑动 3 个月
)

result = run_walk_forward_analysis(
    prices=prices,
    strategy_cls=SimpleMAStrategy,
    param_grid={"window": [5, 10, 20, 50]},
    config=config,
    optimization_metric="sharpe_ratio"
)

print(f"平均训练期表现: {result.avg_train_performance:.2%}")
print(f"平均测试期表现: {result.avg_test_performance:.2%}")
print(f"性能衰减: {result.performance_decay:.2%}")
\`\`\`

---

## 风险控制

### 止损止盈

\`\`\`python
from quant_system.backtest.risk_control import RiskControl

risk_control = RiskControl(
    stop_loss_pct=-0.05,      # -5% 止损
    take_profit_pct=0.10,     # 10% 止盈
    max_position_ratio=0.8    # 80% 最大仓位
)
\`\`\`

### 最大回撤限制

\`\`\`python
risk_control = RiskControl(
    max_drawdown_limit=-0.15  # -15% 强制平仓
)
\`\`\`

### 预定义配置

\`\`\`python
from quant_system.backtest.risk_control import (
    ConservativeRiskControl,  # 保守型
    AggressiveRiskControl,    # 激进型
    NoRiskControl            # 无风控
)

risk_control = ConservativeRiskControl()
\`\`\`

---

## 可视化

### 综合报告

\`\`\`python
from quant_system.visualization.backtest_report import plot_backtest_report

plot_backtest_report(
    result,
    save_path="report.png",
    figsize=(15, 10)
)
\`\`\`

### 参数热力图

\`\`\`python
from quant_system.visualization.param_heatmap import plot_param_heatmap

plot_param_heatmap(
    results,
    x_param="fast_window",
    y_param="slow_window",
    metric="sharpe_ratio",
    title="Sharpe Ratio Heatmap",
    save_path="heatmap.png"
)
\`\`\`

### 策略对比

\`\`\`python
from quant_system.visualization.backtest_report import plot_strategy_comparison

plot_strategy_comparison(
    results=[result1, result2, result3],
    metric="equity_curve",
    title="Strategy Comparison"
)
\`\`\`