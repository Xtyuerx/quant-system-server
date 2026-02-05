# 📈 Quant System Server - 使用文档

欢迎使用 Quant System Server！这是一个专业的量化交易回测框架，专注于可扩展、可验证、可复盘的量化研究。

## 🎯 核心特性

### ✅ 已实现功能

#### 1. 回测引擎
- ✅ 单策略回测
- ✅ 多策略对比
- ✅ 完整的交易记录
- ✅ 权益曲线追踪

#### 2. 性能指标（9 个核心指标）
- 总收益率 (Total Return)
- 年化收益率 (Annual Return)
- 最大回撤 (Max Drawdown)
- **夏普比率 (Sharpe Ratio)** ⭐
- 年化波动率 (Annual Volatility)
- 交易次数 (Number of Trades)
- 胜率 (Win Rate)
- 平均单笔收益 (Avg Trade Return)
- 盈亏比 (Profit Factor)

#### 3. 现实交易约束
- ✅ **交易成本**：万三佣金 + 千一印花税
- ✅ **滑点模型**：固定/比例/成交量滑点
- ✅ **风险控制**：止损/止盈/最大回撤限制

#### 4. 高级分析工具
- ✅ 参数扫描与优化
- ✅ 参数热力图可视化
- ✅ Walk-Forward 分析（防过拟合）
- ✅ 综合回测报告（2x2 子图）

#### 5. 测试覆盖
- ✅ 86 个单元测试
- ✅ 94%+ 代码覆盖率
- ✅ 持续集成就绪

---

## 🚀 快速开始

### 安装

\`\`\`bash
# 克隆项目
git clone <repository-url>
cd quant-system-server

# 安装依赖
poetry install

# 验证安装
poetry run pytest
\`\`\`

### 5 分钟快速示例

\`\`\`python
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.simple_ma import SimpleMAStrategy
from quant_system.backtest.engine import BacktestEngine
from quant_system.visualization.backtest_report import plot_backtest_report

# 1️⃣ 加载数据
prices = load_prices_from_csv("AAPL.csv")

# 2️⃣ 创建策略
strategy = SimpleMAStrategy(window=5)
signals = strategy.generate_signals(prices)

# 3️⃣ 运行回测
engine = BacktestEngine(
    prices=prices,
    signals=signals,
    symbol="AAPL",
    initial_cash=100_000
)
result = engine.run()

# 4️⃣ 查看结果
print(f"收益率: {result.total_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")

# 5️⃣ 生成报告
plot_backtest_report(result, save_path="report.png")
\`\`\`

**输出**：
\`\`\`
收益率: 3.92%
夏普比率: 2.15
最大回撤: -0.62%
📊 Report saved to: report.png
\`\`\`

---

## 📑 文档导航

### 基础教程
- [快速开始](quickstart.md) - 5 分钟上手
- [用户指南](user_guide.md) - 完整功能介绍
- [API 参考](api_reference.md) - 详细 API 文档

### 进阶教程
- [参数优化](examples/parameter_optimization.md)
- [风险管理](examples/risk_management.md)
- [Walk-Forward 分析](examples/walk_forward_analysis.md)

### 最佳实践
- [策略开发规范](best_practices.md#策略开发)
- [性能优化技巧](best_practices.md#性能优化)
- [常见陷阱避免](best_practices.md#常见陷阱)

---

## 🎓 核心概念

### 1. 信号系统
\`\`\`python
from quant_system.enums.signal import SignalType

# 四种信号类型
SignalType.BUY    # 买入
SignalType.SELL   # 卖出（暂未使用）
SignalType.EXIT   # 平仓
SignalType.HOLD   # 持有
\`\`\`

### 2. 回测结果
\`\`\`python
result = engine.run()

# 访问指标
result.total_return      # 总收益率
result.sharpe_ratio      # 夏普比率
result.max_drawdown      # 最大回撤
result.equity_curve      # 权益曲线
result.trades            # 交易记录

# 输出方法
result.summary()         # 字典格式
result.to_row()          # 格式化字符串（表格）
result.to_dict()         # 原始数值
\`\`\`

### 3. 策略开发
\`\`\`python
from quant_system.strategy.base import Strategy
from quant_system.enums.signal import SignalType

class MyStrategy(Strategy):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, prices: List[float]) -> List[SignalType]:
        signals = []
        for i, price in enumerate(prices):
            # 实现你的策略逻辑
            if condition:
                signals.append(SignalType.BUY)
            else:
                signals.append(SignalType.HOLD)
        return signals
\`\`\`

---

## 🔧 配置选项

### 交易成本
\`\`\`python
from quant_system.backtest.cost_model import CostModel

# 自定义成本
cost_model = CostModel(
    commission_rate=0.0003,  # 万三
    min_commission=5.0,      # 最低 5 元
    stamp_duty_rate=0.001    # 千一印花税
)

engine = BacktestEngine(..., cost_model=cost_model)
\`\`\`

### 滑点模型
\`\`\`python
from quant_system.backtest.slippage import FixedSlippage

slippage = FixedSlippage(slippage_bps=5)  # 5 个基点
engine = BacktestEngine(..., slippage_model=slippage)
\`\`\`

### 风险控制
\`\`\`python
from quant_system.backtest.risk_control import ConservativeRiskControl

risk_control = ConservativeRiskControl()  # 保守型风控
engine = BacktestEngine(..., risk_control=risk_control)
\`\`\`

---

## 📊 可视化

### 综合回测报告
\`\`\`python
from quant_system.visualization.backtest_report import plot_backtest_report

plot_backtest_report(result, save_path="report.png")
\`\`\`

生成 2x2 子图报告：
- 左上：权益曲线
- 右上：回撤曲线
- 左下：收益分布
- 右下：指标表格

### 参数热力图
\`\`\`python
from quant_system.visualization.param_heatmap import plot_param_heatmap
from quant_system.runner.param_scan import run_param_scan

results = run_param_scan(...)
plot_param_heatmap(
    results,
    x_param="fast_window",
    y_param="slow_window",
    metric="sharpe_ratio"
)
\`\`\`

---

## ❓ 常见问题

### Q: 如何添加自定义数据源？
A: 实现 `load_prices_from_csv` 的类似函数，返回 `List[float]` 即可。

### Q: 支持日内交易吗？
A: 当前版本主要面向日线级别，但架构支持任意时间粒度。

### Q: 如何处理停牌数据？
A: 在数据预处理时填充或跳过停牌日期。

### Q: 测试覆盖率如何？
A: 94%+ 代码覆盖率，86 个单元测试。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
\`\`\`bash
poetry install --with dev
poetry run pytest --cov
\`\`\`

### 代码规范
- 使用 Black 格式化
- 遵循 PEP 8
- 添加类型注解
- 编写单元测试

---

## 📞 联系方式

- **作者**: xtyuerx
- **邮箱**: xiangtaiyua06299@biaoguoworks.com
- **GitHub**: [项目地址]

---

## 📄 许可证

[待添加]

---

⭐ 如果这个项目对你有帮助，欢迎 Star！