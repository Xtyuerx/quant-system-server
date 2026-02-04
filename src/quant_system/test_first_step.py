from quant_system.data.price_feed import load_series_from_csv
from quant_system.strategy.simple_ma import SimpleMA
from quant_system.backtest.engine import BacktestEngine

# 1. 加载数据
prices = load_series_from_csv("AAPL.csv", "price")

# 2. 生成信号
strategy = SimpleMA(window=5)
signals = strategy.generate_signals(list(prices))

# 3. 运行回测
bt = BacktestEngine(
    symbol="AAPL",
    prices=list(prices),
    signals=signals,
)
result = bt.run()

# 4. 输出结果
print("=" * 50)
print(f"Symbol: {result.symbol}")
print(f"Initial Cash: ${result.initial_cash:,.2f}")
print(f"Final Equity: ${result.final_equity:,.2f}")
print(f"Total Return: {result.total_return * 100:.2f}%")
print(f"Max Drawdown: {result.max_drawdown * 100:.2f}%")
print("=" * 50)