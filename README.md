```markdown
# 📈 Quant System Server

一个基于 Python 的量化交易回测系统，支持多策略、多标的同时回测，并提供丰富的可视化分析功能。

## ✨ 特性

- 🚀 **多策略回测框架**：支持同时运行多个交易策略
- 📊 **多标的支持**：可对多个股票/资产同时进行回测
- 📈 **高级可视化**：生成专业的回测结果图表和权益曲线
- 🎯 **风险管理**：内置最大回撤限制功能
- 🔧 **模块化设计**：易于扩展和自定义策略
- 📉 **性能指标**：自动计算总收益率、最大回撤等关键指标

## 📦 项目结构

```
quant-system-server/
├── src/
│   └── quant_system/
│       ├── strategy/          # 交易策略模块
│       │   ├── base_strategy.py    # 策略基类
│       │   └── buy_and_hold.py     # 买入持有策略
│       ├── backtest/          # 回测引擎
│       │   ├── simple_backtest.py  # 单策略回测
│       │   ├── multi_backtest.py   # 多策略回测框架
│       │   ├── signal.py           # 交易信号定义
│       │   └── trade.py            # 交易记录
│       ├── data/              # 数据管理
│       │   ├── price_feed.py       # 价格数据加载
│       │   ├── AAPL.csv           # 示例数据
│       │   └── MSFT.csv           # 示例数据
│       ├── analysis/          # 分析与可视化
│       │   ├── visualization.py           # 单策略可视化
│       │   ├── multi_visualization.py     # 多策略对比可视化
│       │   └── performance.py             # 性能指标计算
│       └── main.py            # 主程序入口
├── tests/                     # 测试文件
├── pyproject.toml            # 项目配置
└── README.md
```

## 🛠️ 环境要求

- Python >= 3.12
- Poetry (包管理工具)

## 📥 安装

1. **克隆项目**

```bash
git clone <repository-url>
cd quant-system-server
```

2. **安装依赖**

```bash
poetry install
```

## 🚀 快速开始

### 方式一：使用命令行工具

安装完成后，直接运行：

```bash
poetry run quant
```

或者在 poetry shell 中：

```bash
poetry shell
quant
```

### 方式二：运行 Python 模块

```bash
python -m quant_system.main
```

## 📊 使用示例

### 基本回测

```python
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy
from quant_system.backtest.simple_backtest import SimpleBacktest

# 加载价格数据
prices = load_prices_from_csv("AAPL.csv")

# 创建策略
strategy = BuyAndHoldStrategy()
signals = strategy.generate_signals(prices)

# 运行回测
backtest = SimpleBacktest(prices, signals, initial_cash=100_000)
backtest.run()

print(f"最终权益: {backtest.equity_curve[-1]}")
```

### 多策略多标的回测

```python
from quant_system.backtest.multi_backtest import MultiBacktest
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy

# 多标的价格数据
price_data = {
    "AAPL": load_prices_from_csv("AAPL.csv"),
    "MSFT": load_prices_from_csv("MSFT.csv")
}

# 多策略
strategies = {
    "BuyAndHold": BuyAndHoldStrategy(),
    # 可以添加更多策略...
}

# 运行多策略回测
multi_bt = MultiBacktest(
    price_data=price_data,
    strategies=strategies,
    initial_cash=100_000,
    max_drawdown_limit=-0.1  # 最大回撤限制 10%
)

results = multi_bt.run()
```

## 📈 性能指标

系统自动计算以下性能指标：

- **总收益率 (Total Return)**：投资期间的总收益百分比
- **最大回撤 (Max Drawdown)**：从峰值到谷底的最大跌幅
- **权益曲线 (Equity Curve)**：资产价值随时间的变化

## 🎨 可视化功能

系统提供多种可视化图表：

1. **单策略回测图表**：包含价格走势、买卖点、权益曲线
2. **多策略对比图表**：对比不同策略在不同标的上的表现
3. **回撤分析图**：展示策略的风险特征

生成的图表会自动保存为 PNG 文件。

## 🔧 自定义策略

创建自定义策略非常简单：

```python
from quant_system.strategy.base_strategy import BaseStrategy
from quant_system.backtest.signal import Signal, SignalType

class MyCustomStrategy(BaseStrategy):
    def generate_signals(self, prices: List[float]):
        signals = []
        for i, price in enumerate(prices):
            # 实现你的策略逻辑
            if i == 0:
                signals.append(Signal(type=SignalType.BUY))
            else:
                signals.append(Signal(type=SignalType.HOLD))
        return signals
```

## 📝 数据格式

价格数据应为 CSV 格式，包含以下列：

```csv
date,price
2024-01-01,100.0
2024-01-02,101.5
2024-01-03,102.3
...
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[请添加您的许可证信息]

## 👤 作者

- **xtyuerx** - xiangtaiyua06299@biaoguoworks.com

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- Email: xiangtaiyua06299@biaoguoworks.com
- GitHub Issues: [项目 Issues 页面]

---

⭐ 如果这个项目对你有帮助，欢迎 Star！
```

这是一个完整的 README.md 内容，包含了：

1. **项目简介**：清晰说明项目用途
2. **特性列表**：突出核心功能
3. **项目结构**：完整的目录说明
4. **安装指南**：详细的安装步骤
5. **使用示例**：包含基本和高级用例
6. **自定义扩展**：说明如何添加自定义策略
7. **数据格式**：明确数据要求
8. **可视化功能**：说明图表生成功能

你目前处于 **ask 模式**，如果需要我帮你将这个内容写入 README.md 文件，请切换到 **agent 模式**。

```markdown
# 📈 Quant System Server

一个基于 Python 的量化交易回测系统，支持多策略、多标的同时回测，并提供丰富的可视化分析功能。

## ✨ 特性

- 🚀 **多策略回测框架**：支持同时运行多个交易策略
- 📊 **多标的支持**：可对多个股票/资产同时进行回测
- 📈 **高级可视化**：生成专业的回测结果图表和权益曲线
- 🎯 **风险管理**：内置最大回撤限制功能
- 🔧 **模块化设计**：易于扩展和自定义策略
- 📉 **性能指标**：自动计算总收益率、最大回撤等关键指标

## 📦 项目结构

```

```plaintext

## 🛠️ 环境要求

- Python >= 3.12
- Poetry (包管理工具)

## 📥 安装

1. **克隆项目**

git clone <repository-url>
cd quant-system-server2. **安装依赖**

poetry install## 🚀 快速开始

### 方式一：使用命令行工具

安装完成后，直接运行：

poetry run quant或者在 poetry shell 中：

poetry shell
quant### 方式二：运行 Python 模块

python -m quant_system.main## 📊 使用示例

### 基本回测

from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy
from quant_system.backtest.simple_backtest import SimpleBacktest

# 加载价格数据
prices = load_prices_from_csv("AAPL.csv")

# 创建策略
strategy = BuyAndHoldStrategy()
signals = strategy.generate_signals(prices)

# 运行回测
backtest = SimpleBacktest(prices, signals, initial_cash=100_000)
backtest.run()

print(f"最终权益: {backtest.equity_curve[-1]}")### 多策略多标的回测

from quant_system.backtest.multi_backtest import MultiBacktest
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy

# 多标的价格数据
price_data = {
    "AAPL": load_prices_from_csv("AAPL.csv"),
    "MSFT": load_prices_from_csv("MSFT.csv")
}

# 多策略
strategies = {
    "BuyAndHold": BuyAndHoldStrategy(),
    # 可以添加更多策略...
}

# 运行多策略回测
multi_bt = MultiBacktest(
    price_data=price_data,
    strategies=strategies,
    initial_cash=100_000,
    max_drawdown_limit=-0.1  # 最大回撤限制 10%
)

results = multi_bt.run()## 📈 性能指标

系统自动计算以下性能指标：

- **总收益率 (Total Return)**：投资期间的总收益百分比
- **最大回撤 (Max Drawdown)**：从峰值到谷底的最大跌幅
- **权益曲线 (Equity Curve)**：资产价值随时间的变化

## 🎨 可视化功能

系统提供多种可视化图表：

1. **单策略回测图表**：包含价格走势、买卖点、权益曲线
2. **多策略对比图表**：对比不同策略在不同标的上的表现
3. **回撤分析图**：展示策略的风险特征

生成的图表会自动保存为 PNG 文件。

## 🔧 自定义策略

创建自定义策略非常简单：

from quant_system.strategy.base_strategy import BaseStrategy
from quant_system.backtest.signal import Signal, SignalType

class MyCustomStrategy(BaseStrategy):
    def generate_signals(self, prices: List[float]):
        signals = []
        for i, price in enumerate(prices):
            # 实现你的策略逻辑
            if i == 0:
                signals.append(Signal(type=SignalType.BUY))
            else:
                signals.append(Signal(type=SignalType.HOLD))
        return signals## 📝 数据格式

价格数据应为 CSV 格式，包含以下列：

date,price
2024-01-01,100.0
2024-01-02,101.5
2024-01-03,102.3
...## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[请添加您的许可证信息]

## 👤 作者

- **xtyuerx** - xiangtaiyua06299@biaoguoworks.com

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- Email: xiangtaiyua06299@biaoguoworks.com
- GitHub Issues: [项目 Issues 页面]

---

⭐ 如果这个项目对你有帮助，欢迎 Star！
```

```shellscript
poetry install
```

```shellscript
poetry run quant
```

```shellscript
poetry shell
quant
```

```shellscript
python -m quant_system.main
```

```python
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy
from quant_system.backtest.simple_backtest import SimpleBacktest

# 加载价格数据
prices = load_prices_from_csv("AAPL.csv")

# 创建策略
strategy = BuyAndHoldStrategy()
signals = strategy.generate_signals(prices)

# 运行回测
backtest = SimpleBacktest(prices, signals, initial_cash=100_000)
backtest.run()

print(f"最终权益: {backtest.equity_curve[-1]}")
```

```python
from quant_system.backtest.multi_backtest import MultiBacktest
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy

# 多标的价格数据
price_data = {
    "AAPL": load_prices_from_csv("AAPL.csv"),
    "MSFT": load_prices_from_csv("MSFT.csv")
}

# 多策略
strategies = {
    "BuyAndHold": BuyAndHoldStrategy(),
    # 可以添加更多策略...
}

# 运行多策略回测
multi_bt = MultiBacktest(
    price_data=price_data,
    strategies=strategies,
    initial_cash=100_000,
    max_drawdown_limit=-0.1  # 最大回撤限制 10%
)

results = multi_bt.run()
```

```python
from quant_system.strategy.base_strategy import BaseStrategy
from quant_system.backtest.signal import Signal, SignalType

class MyCustomStrategy(BaseStrategy):
    def generate_signals(self, prices: List[float]):
        signals = []
        for i, price in enumerate(prices):
            # 实现你的策略逻辑
            if i == 0:
                signals.append(Signal(type=SignalType.BUY))
            else:
                signals.append(Signal(type=SignalType.HOLD))
        return signals
```

```csv
date,price
2024-01-01,100.0
2024-01-02,101.5
2024-01-03,102.3
...
```