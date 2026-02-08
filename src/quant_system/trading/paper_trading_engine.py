from typing import Optional, List
from datetime import datetime
from .account import Account
from .order import OrderManager, Order, OrderType, OrderSide
from .simulator import MatchingEngine
from ..data.live_feed import LiveDataFeed, BarData

class PaperTradingEngine:
    """
    模拟交易引擎（Paper Trading）
    
    功能：
    - 实时数据驱动
    - 事件驱动架构
    - 接近真实交易流程
    - 自动撮合与账户更新
    
    使用示例：
        engine = PaperTradingEngine(
            strategy=my_strategy,
            data_feed=live_feed,
            initial_cash=100_000
        )
        engine.start(['000001', '600519'])
    """
    
    def __init__(
        self,
        data_feed: LiveDataFeed,
        initial_cash: float = 100_000,
        account_id: str = "PAPER001",
        commission_rate: float = 0.0003,
    ):
        self.data_feed = data_feed
        
        # 核心组件
        self.account = Account(initial_cash, account_id)
        self.order_manager = OrderManager()
        self.matching_engine = MatchingEngine(commission_rate=commission_rate)
        
        # 状态
        self.is_running = False
        self.bar_count = 0
        
        # 策略回调（由外部注册）
        self.on_bar_callback = None
        
        # 设置数据回调
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """设置数据回调"""
        self.data_feed.on_bar(self._on_bar)
    
    def set_strategy_callback(self, callback):
        """
        注册策略回调函数
        
        回调签名: callback(bar: BarData, account: Account) -> Optional[Order]
        """
        self.on_bar_callback = callback
    
    def _on_bar(self, bar: BarData):
        """
        K线更新回调（核心事件处理）
        
        流程：
        1. 更新持仓市价
        2. 撮合挂单
        3. 调用策略生成信号
        4. 下单
        """
        if not self.is_running:
            return
        
        self.bar_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Bar #{self.bar_count} | {bar.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   {bar.symbol}: O={bar.open:.2f} H={bar.high:.2f} "
              f"L={bar.low:.2f} C={bar.close:.2f} V={bar.volume:.0f}")
        
        # 1. 更新持仓市价
        self.account.update_prices({bar.symbol: bar.close})
        
        # 2. 撮合挂单
        fills = self.matching_engine.match_orders(bar)
        for fill in fills:
            print(f"✅ 成交: {fill}")
            self.account.update_position(fill)
            self.order_manager.on_fill(fill)
        
        # 3. 调用策略
        if self.on_bar_callback:
            order = self.on_bar_callback(bar, self.account)
            
            # 4. 处理订单
            if order:
                if self._validate_order(order):
                    self.order_manager.submit_order(order)
                    self.matching_engine.add_order(order)
                else:
                    print(f"🚨 订单验证失败: {order}")
        
        # 5. 打印状态
        self._print_status()
    
    def _validate_order(self, order: Order) -> bool:
        """订单验证（风控）"""
        # 检查资金是否足够
        if order.side == OrderSide.BUY:
            if order.order_type == OrderType.MARKET:
                # 市价单无法精确估算，使用最新价
                # 实际应该预留buffer
                return True
            elif order.order_type == OrderType.LIMIT and order.price:
                required_cash = order.quantity * order.price * 1.001  # 1.001倍buffer
                if required_cash > self.account.cash:
                    print(f"⚠️ 资金不足: 需要{required_cash:.2f}, 可用{self.account.cash:.2f}")
                    return False
        
        # 检查是否有足够持仓卖出
        if order.side == OrderSide.SELL:
            pos = self.account.get_position(order.symbol)
            if not pos or pos.quantity < order.quantity:
                print(f"⚠️ 持仓不足: {order.symbol}")
                return False
        
        return True
    
    def _print_status(self):
        """打印当前状态"""
        print(f"\n账户状态:")
        print(f"  💰 现金: {self.account.cash:,.2f}")
        print(f"  📈 持仓市值: {self.account.total_position_value:,.2f}")
        print(f"  💎 总资产: {self.account.total_equity:,.2f}")
        print(f"  📊 盈亏: {self.account.total_pnl:+,.2f} ({self.account.total_pnl_pct:+.2f}%)")
        
        if self.account.positions:
            print(f"\n持仓:")
            for pos in self.account.positions.values():
                print(f"  {pos}")
    
    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Optional[Order]:
        """
        手动下单接口
        
        Args:
            symbol: 股票代码
            side: 买卖方向
            quantity: 数量
            order_type: 订单类型
            price: 价格（限价单需要）
        """
        order = self.order_manager.create_order(
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price
        )
        
        if self._validate_order(order):
            self.order_manager.submit_order(order)
            self.matching_engine.add_order(order)
            return order
        
        return None
    
    def start(self, symbols: List[str]):
        """启动模拟交易"""
        print("\n" + "="*60)
        print("🚀 启动模拟交易引擎")
        print("="*60)
        print(f"账户ID: {self.account.account_id}")
        print(f"初始资金: {self.account.initial_cash:,.2f}")
        print(f"订阅股票: {', '.join(symbols)}")
        print("="*60 + "\n")
        
        self.is_running = True
        self.data_feed.subscribe(symbols)
        self.data_feed.start()
    
    def stop(self):
        """停止模拟交易"""
        print("\n⏹️ 停止模拟交易...")
        self.is_running = False
        self.data_feed.stop()
        self._print_final_summary()
    
    def _print_final_summary(self):
        """打印最终总结"""
        self.account.print_summary()
        
        print("\n交易历史:")
        if self.account.trade_history:
            for i, fill in enumerate(self.account.trade_history[-10:], 1):  # 最近10笔
                print(f"  {i}. {fill}")
        else:
            print("  无交易记录")