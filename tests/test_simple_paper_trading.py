"""
简单的模拟交易测试脚本（无需网络）
用于快速验证系统功能
"""

from quant_system.data.live_feed import CSVReplayFeed
from quant_system.trading.paper_trading_engine import PaperTradingEngine
from quant_system.trading.order import OrderType, OrderSide, OrderManager
from quant_system.trading.account import Account
from quant_system.data.live_feed import BarData
from typing import Optional
from quant_system.trading.order import Order
import time

def simple_strategy_test():
    """简单策略测试"""
    
    print("\n" + "="*70)
    print("🧪 模拟交易系统 - 快速测试")
    print("="*70)
    
    # 1. 创建CSV回放器（使用AAPL数据）
    try:
        feed = CSVReplayFeed(
            csv_path="src/quant_system/data/AAPL.csv",
            symbol="AAPL",
            speed=5.0  # 5倍速
        )
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        print("💡 请确保 src/quant_system/data/AAPL.csv 存在")
        return
    
    # 2. 创建模拟交易引擎
    engine = PaperTradingEngine(
        data_feed=feed,
        initial_cash=100_000
    )
    
    # 3. 简单的双均线策略
    price_history = []
    trade_count = 0
    
    def dual_ma_strategy(bar: BarData, account: Account) -> Optional[Order]:
        nonlocal trade_count
        
        # 记录价格
        price_history.append(bar.close)
        
        # 需要足够的历史数据
        if len(price_history) < 20:
            return None
        
        # 计算均线
        fast_ma = sum(price_history[-5:]) / 5
        slow_ma = sum(price_history[-20:]) / 20
        
        has_position = account.has_position("AAPL")
        
        # 金叉买入
        if fast_ma > slow_ma * 1.01 and not has_position and trade_count < 3:
            shares = int(account.cash / bar.close * 0.95)
            if shares > 0:
                om = OrderManager()
                order = om.create_order(
                    symbol="AAPL",
                    order_type=OrderType.MARKET,
                    side=OrderSide.BUY,
                    quantity=shares
                )
                trade_count += 1
                print(f"\n📈 策略信号: 买入 {shares} 股 @{bar.close:.2f} (金叉)")
                return order
        
        # 死叉卖出
        elif fast_ma < slow_ma * 0.99 and has_position:
            pos = account.get_position("AAPL")
            if pos:
                om = OrderManager()
                order = om.create_order(
                    symbol="AAPL",
                    order_type=OrderType.MARKET,
                    side=OrderSide.SELL,
                    quantity=pos.quantity
                )
                print(f"\n📉 策略信号: 卖出 {pos.quantity} 股 @{bar.close:.2f} (死叉)")
                return order
        
        return None
    
    # 4. 注册策略
    engine.set_strategy_callback(dual_ma_strategy)
    
    # 5. 启动
    print("\n⏰ 开始运行模拟交易...")
    engine.start(['AAPL'])
    
    # 6. 等待完成
    time.sleep(20)
    
    # 7. 停止并查看结果
    engine.stop()
    
    print("\n" + "="*70)
    print("✅ 测试完成！")
    print("="*70)


if __name__ == "__main__":
    simple_strategy_test()