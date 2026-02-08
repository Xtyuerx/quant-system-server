# examples/paper_trading_demo.py

from quant_system.data.live_feed import AKShareDataFeed, HistoricalSimulator
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.trading.paper_trading_engine import PaperTradingEngine
from quant_system.trading.order import OrderType, OrderSide
from quant_system.trading.account import Account
from quant_system.data.live_feed import BarData
from typing import Optional
from quant_system.trading.order import Order

# ============================================
# 示例1: 简单的双均线策略
# ============================================

class SimpleMAStrategy:
    """简单双均线策略"""
    
    def __init__(self, fast_window=5, slow_window=20):
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.price_history = {}
    
    def __call__(self, bar: BarData, account: Account) -> Optional[Order]:
        """策略逻辑"""
        symbol = bar.symbol
        
        # 记录价格历史
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(bar.close)
        
        prices = self.price_history[symbol]
        
        # 数据不足
        if len(prices) < self.slow_window:
            return None
        
        # 计算均线
        fast_ma = sum(prices[-self.fast_window:]) / self.fast_window
        slow_ma = sum(prices[-self.slow_window:]) / self.slow_window
        
        # 交易逻辑
        has_position = account.has_position(symbol)
        
        # 金叉买入
        if fast_ma > slow_ma and not has_position:
            # 全仓买入
            shares = int(account.cash / bar.close * 0.95)  # 95%仓位
            if shares > 0:
                from quant_system.trading.order import OrderManager, OrderType, OrderSide
                order_manager = OrderManager()
                order = order_manager.create_order(
                    symbol=symbol,
                    order_type=OrderType.MARKET,
                    side=OrderSide.BUY,
                    quantity=shares
                )
                print(f"📈 策略信号: 买入 {symbol} {shares}股 (金叉)")
                return order
        
        # 死叉卖出
        elif fast_ma < slow_ma and has_position:
            pos = account.get_position(symbol)
            if pos:
                from quant_system.trading.order import OrderManager, OrderType, OrderSide
                order_manager = OrderManager()
                order = order_manager.create_order(
                    symbol=symbol,
                    order_type=OrderType.MARKET,
                    side=OrderSide.SELL,
                    quantity=pos.quantity
                )
                print(f"📉 策略信号: 卖出 {symbol} {pos.quantity}股 (死叉)")
                return order
        
        return None


def demo_historical_simulation():
    """示例1: 用历史数据模拟（快速测试）"""
    print("=" * 60)
    print("示例1: 历史数据模拟")
    print("=" * 60)
    
    # 1. 加载历史数据
    prices = load_prices_from_csv("AAPL.csv")
    
    # 2. 创建历史模拟器
    simulator = HistoricalSimulator(prices, symbol="AAPL", speed=10.0)  # 10倍速
    
    # 3. 创建模拟交易引擎
    engine = PaperTradingEngine(
        data_feed=simulator,
        initial_cash=100_000
    )
    
    # 4. 设置策略
    strategy = SimpleMAStrategy(fast_window=5, slow_window=20)
    engine.set_strategy_callback(strategy)
    
    # 5. 启动
    engine.start(['AAPL'])
    
    # 等待回放完成（或手动停止）
    import time
    time.sleep(30)  # 运行30秒
    
    engine.stop()


def demo_live_akshare():
    """示例2: 真实的AKShare实时数据"""
    print("=" * 60)
    print("示例2: AKShare实时数据流")
    print("=" * 60)
    
    # 1. 创建实时数据源
    live_feed = AKShareDataFeed(interval=5)  # 每5秒更新
    
    # 2. 创建引擎
    engine = PaperTradingEngine(
        data_feed=live_feed,
        initial_cash=100_000
    )
    
    # 3. 设置策略
    strategy = SimpleMAStrategy(fast_window=3, slow_window=10)
    engine.set_strategy_callback(strategy)
    
    # 4. 启动（订阅平安银行、贵州茅台）
    try:
        engine.start(['000001', '600519'])
        
        # 持续运行（Ctrl+C停止）
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        engine.stop()


def demo_manual_trading():
    """示例3: 手动交易"""
    print("=" * 60)
    print("示例3: 手动下单")
    print("=" * 60)
    
    simulator = HistoricalSimulator(
        load_prices_from_csv("AAPL.csv"),
        symbol="AAPL",
        speed=5.0
    )
    
    engine = PaperTradingEngine(
        data_feed=simulator,
        initial_cash=100_000
    )
    
    # 不设置自动策略，手动下单
    engine.start(['AAPL'])
    
    import time
    time.sleep(2)
    
    # 手动买入
    print("\n🖱️ 手动下单: 买入100股")
    engine.submit_order('AAPL', OrderSide.BUY, 100, OrderType.MARKET)
    
    time.sleep(10)
    
    # 手动卖出
    print("\n🖱️ 手动下单: 卖出50股")
    engine.submit_order('AAPL', OrderSide.SELL, 50, OrderType.MARKET)
    
    time.sleep(10)
    
    engine.stop()


def main():
    # 选择运行哪个示例
    print("选择示例:")
    print("1. 历史数据模拟（快速）")
    print("2. AKShare实时数据")
    print("3. 手动交易")
    
    choice = input("\n输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        demo_historical_simulation()
    elif choice == "2":
        demo_live_akshare()
    elif choice == "3":
        demo_manual_trading()
    else:
        print("运行默认示例...")
        demo_historical_simulation()

if __name__ == "__main__":
    main()