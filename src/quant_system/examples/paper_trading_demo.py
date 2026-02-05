# examples/paper_trading_demo.py

from quant_system.trading.paper_trading_engine import PaperTradingEngine
from quant_system.data.live_feed import AKShareDataFeed
from quant_system.strategy.dual_ma import DualMAStrategy

# 1. 创建实时数据源
data_feed = AKShareDataFeed()

# 2. 创建策略
strategy = DualMAStrategy(fast_window=5, slow_window=20)

# 3. 创建模拟交易引擎
engine = PaperTradingEngine(
    strategy=strategy,
    data_feed=data_feed,
    initial_cash=100_000
)

# 4. 启动模拟交易
try:
    engine.start(symbols=['000001.SZ', '600519.SH'])  # 平安、茅台
except KeyboardInterrupt:
    engine.stop()