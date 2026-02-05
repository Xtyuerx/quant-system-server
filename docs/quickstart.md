# 快速开始指南

## 环境要求

- Python >= 3.12
- Poetry (推荐) 或 pip

## 安装步骤

### 方法 1：使用 Poetry（推荐）

\`\`\`bash
# 1. 克隆项目
git clone <repository-url>
cd quant-system-server

# 2. 安装依赖
poetry install

# 3. 激活虚拟环境
poetry shell

# 4. 验证安装
pytest
\`\`\`

### 方法 2：使用 pip

\`\`\`bash
pip install -r requirements.txt
\`\`\`

---

## 第一个回测

### 步骤 1：准备数据

数据格式（CSV）：
\`\`\`csv
date,price
2024-01-01,100.0
2024-01-02,101.5
2024-01-03,102.3
...
\`\`\`

将数据文件放在 `src/quant_system/data/` 目录下。

### 步骤 2：选择策略

使用内置的简单均线策略：

\`\`\`python
from quant_system.strategy.simple_ma import SimpleMAStrategy

strategy = SimpleMAStrategy(window=5)  # 5 日均线
\`\`\`

### 步骤 3：运行回测

\`\`\`python
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.backtest.engine import BacktestEngine

# 加载数据
prices = load_prices_from_csv("AAPL.csv")

# 生成信号
signals = strategy.generate_signals(prices)

# 创建回测引擎
engine = BacktestEngine(
    prices=prices,
    signals=signals,
    symbol="AAPL",
    initial_cash=100_000  # 初始资金 10 万
)

# 运行回测
result = engine.run()
\`\`\`

### 步骤 4：查看结果

\`\`\`python
# 打印关键指标
print(f"💰 总收益率: {result.total_return:.2%}")
print(f"📈 年化收益: {result.annual_return:.2%}")
print(f"📉 最大回撤: {result.max_drawdown:.2%}")
print(f"⚡ 夏普比率: {result.sharpe_ratio:.2f}")
print(f"🎯 胜率: {result.win_rate:.1%}")
print(f"🔄 交易次数: {result.num_trades}")
\`\`\`

### 步骤 5：生成可视化报告

\`\`\`python
from quant_system.visualization.backtest_report import plot_backtest_report

plot_backtest_report(result, save_path="my_first_backtest.png")
\`\`\`

---

## 完整示例代码

\`\`\`python
"""
我的第一个量化回测
"""
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.simple_ma import SimpleMAStrategy
from quant_system.backtest.engine import BacktestEngine
from quant_system.visualization.backtest_report import plot_backtest_report


def main():
    # 1. 加载数据
    print("📊 加载数据...")
    prices = load_prices_from_csv("AAPL.csv")
    print(f"   数据点数: {len(prices)}")
    
    # 2. 创建策略
    print("\n🎯 创建策略...")
    strategy = SimpleMAStrategy(window=5)
    signals = strategy.generate_signals(prices)
    
    # 3. 运行回测
    print("\n🚀 运行回测...")
    engine = BacktestEngine(
        prices=prices,
        signals=signals,
        symbol="AAPL",
        initial_cash=100_000
    )
    result = engine.run()
    
    # 4. 输出结果
    print("\n" + "=" * 60)
    print("📊 回测结果")
    print("=" * 60)
    print(f"总收益率: {result.total_return:>10.2%}")
    print(f"年化收益: {result.annual_return:>10.2%}")
    print(f"最大回撤: {result.max_drawdown:>10.2%}")
    print(f"夏普比率: {result.sharpe_ratio:>10.2f}")
    print(f"胜率:     {result.win_rate:>10.1%}")
    print(f"交易次数: {result.num_trades:>10}")
    print("=" * 60)
    
    # 5. 生成报告
    print("\n📈 生成可视化报告...")
    plot_backtest_report(result, save_path="my_first_backtest.png")
    print("✅ 完成！")


if __name__ == "__main__":
    main()
\`\`\`

---

## 下一步

- [用户指南](user_guide.md) - 了解完整功能
- [参数优化](examples/parameter_optimization.md) - 找到最优参数
- [风险管理](examples/risk_management.md) - 添加止损止盈