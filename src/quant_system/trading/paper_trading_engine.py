class PaperTradingEngine:
    """
    模拟交易引擎（Paper Trading）
    
    特点：
    - 实时数据驱动
    - 事件驱动架构
    - 接近真实交易流程
    """
    
    def __init__(
        self,
        strategy,
        data_feed: LiveDataFeed,
        initial_cash: float = 100_000,
        risk_control=None
    ):
        self.strategy = strategy
        self.data_feed = data_feed
        
        self.account = Account(initial_cash)
        self.order_manager = OrderManager()
        self.matching_engine = MatchingEngine()
        self.risk_control = risk_control
        
        self.is_running = False
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """设置数据回调"""
        self.data_feed.on_bar(self._on_bar)
    
    def _on_bar(self, bar: BarData):
        """
        K线更新回调（核心事件处理）
        """
        if not self.is_running:
            return
        
        # 1. 更新持仓市价
        self.account.update_prices({bar.symbol: bar.close})
        
        # 2. 撮合挂单
        fills = self.matching_engine.match_orders(bar)
        for fill in fills:
            self.account.update_position(fill)
            self.order_manager.on_fill(fill)
            print(f"✅ 成交: {fill.symbol} {fill.side.value} "
                  f"{fill.quantity}@{fill.price:.2f}")
        
        # 3. 策略生成信号
        signal = self.strategy.on_bar(bar, self.account)
        
        # 4. 根据信号下单
        if signal:
            order = self._create_order_from_signal(signal, bar)
            if order:
                # 风控检查
                if self._risk_check(order):
                    self.order_manager.submit_order(order)
                    self.matching_engine.add_order(order)
                    print(f"📝 下单: {order.symbol} {order.side.value} "
                          f"{order.quantity}@{order.order_type.value}")
                else:
                    print(f"🚨 风控拒绝: {order.symbol}")
        
        # 5. 记录状态
        self._log_status(bar)
    
    def _create_order_from_signal(self, signal, bar) -> Optional[Order]:
        """根据信号创建订单"""
        # 具体逻辑根据策略实现
        pass
    
    def _risk_check(self, order: Order) -> bool:
        """风控检查"""
        # 检查资金是否足够
        if order.side == OrderSide.BUY:
            required_cash = order.quantity * order.price if order.price else 0
            if required_cash > self.account.cash:
                return False
        
        # 检查仓位限制
        if self.risk_control:
            return self.risk_control.check(order, self.account)
        
        return True
    
    def _log_status(self, bar: BarData):
        """记录状态"""
        print(f"\n[{bar.timestamp}] {bar.symbol} @ {bar.close:.2f}")
        print(f"账户: 总资产={self.account.total_equity:,.2f}, "
              f"现金={self.account.cash:,.2f}, "
              f"收益率={self.account.total_pnl_pct:.2f}%")
    
    def start(self, symbols: list[str]):
        """启动模拟交易"""
        print("🚀 启动模拟交易...")
        self.is_running = True
        self.data_feed.subscribe(symbols)
        self.data_feed.start()
    
    def stop(self):
        """停止模拟交易"""
        print("⏸️ 停止模拟交易")
        self.is_running = False
        self.data_feed.stop()
        self._print_summary()
    
    def _print_summary(self):
        """打印总结"""
        summary = self.account.get_summary()
        print("\n" + "="*50)
        print("模拟交易总结")
        print("="*50)
        print(f"初始资金: {self.account.initial_cash:,.2f}")
        print(f"最终资产: {summary['total_equity']:,.2f}")
        print(f"总盈亏: {summary['total_pnl']:,.2f}")
        print(f"收益率: {summary['total_pnl_pct']:.2f}%")
        print(f"交易次数: {summary['trades']}")
        print("="*50)