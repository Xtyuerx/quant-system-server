from quant_system.backtest.result import BacktestResult
from quant_system.backtest.trade import Trade
from quant_system.backtest.cost_model import CostModel
from quant_system.backtest.slippage import SlippageModel, NoSlippage
from quant_system.backtest.risk_control import RiskControl, RiskMonitor, NoRiskControl
from typing import Optional


class BacktestEngine:
    def __init__(
        self,
        prices: list[float],
        signals: list,
        symbol: str,
        initial_cash: float = 100_000,
        cost_model: Optional[CostModel] = None,
        slippage_model: Optional[SlippageModel] = None,
        risk_control: Optional[RiskControl] = None,
    ):
        self.prices = prices
        self.signals = signals
        self.symbol = symbol

        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0
        
        # 成本模型（默认万三）
        self.cost_model = cost_model if cost_model is not None else CostModel()
        
        # 滑点模型（默认无滑点）
        self.slippage_model = slippage_model if slippage_model is not None else NoSlippage()
        
        # 风控模块（默认无风控）
        self.risk_control = risk_control if risk_control is not None else NoRiskControl()
        self.risk_monitor = RiskMonitor(self.risk_control, initial_cash)

    def run(self) -> BacktestResult:
        """
        执行回测，返回标准结果对象
        """
        equity_curve: list[float] = []
        trades: list[Trade] = []
        entry_price: Optional[float] = None

        for i, price in enumerate(self.prices):
            signal = self.signals[i]
            
            # 检查是否触发最大回撤强平
            if self.risk_monitor.check_max_drawdown(equity_curve):
                if self.position > 0:
                    # 强制平仓
                    actual_price = self.slippage_model.apply_to_sell(price)
                    cost = self.cost_model.calculate_sell_cost(actual_price, self.position)
                    
                    self.cash = self.position * actual_price - cost
                    trades.append(Trade(
                        price=actual_price,
                        size=-self.position,
                        cash_after=self.cash,
                        position_after=0.0,
                        type="RISK_EXIT"
                    ))
                    self.position = 0.0
                    entry_price = None
                
                # 触发风控后不再交易
                equity = self.cash + self.position * price
                equity_curve.append(equity)
                continue

            # 买入逻辑
            if signal.name == "BUY" and self.position == 0:
                # 应用滑点
                actual_price = self.slippage_model.apply_to_buy(price)
                
                # 应用风控仓位限制
                max_shares = self.risk_monitor.get_position_size(
                    self.cash, actual_price, target_ratio=1.0
                )
                
                # 计算买入成本
                cost = self.cost_model.calculate_buy_cost(actual_price, max_shares)
                
                # 实际可买入股数
                actual_shares = (self.cash - cost) / actual_price
                self.position = actual_shares
                self.cash = 0.0
                entry_price = actual_price
                
                self.risk_monitor.set_entry_price(actual_price)
                
                trades.append(Trade(
                    price=actual_price,
                    size=actual_shares,
                    cash_after=self.cash,
                    position_after=self.position,
                    type="BUY"
                ))

            # 卖出逻辑
            elif signal.name == "EXIT" and self.position > 0:
                should_exit = True
                exit_type = "EXIT"
                
                # 检查是否触发止损/止盈
                if entry_price is not None:
                    if self.risk_monitor.check_stop_loss(entry_price, price):
                        exit_type = "STOP_LOSS"
                    elif self.risk_monitor.check_take_profit(entry_price, price):
                        exit_type = "TAKE_PROFIT"
                
                if should_exit:
                    # 应用滑点
                    actual_price = self.slippage_model.apply_to_sell(price)
                    
                    proceeds = self.position * actual_price
                    cost = self.cost_model.calculate_sell_cost(actual_price, self.position)
                    
                    self.cash = proceeds - cost
                    trades.append(Trade(
                        price=actual_price,
                        size=-self.position,
                        cash_after=self.cash,
                        position_after=0.0,
                        type=exit_type
                    ))
                    self.position = 0.0
                    entry_price = None
                    self.risk_monitor.clear_position()
            
            # 持仓时检查止损/止盈
            elif self.position > 0 and entry_price is not None:
                if self.risk_monitor.check_stop_loss(entry_price, price):
                    # 触发止损
                    actual_price = self.slippage_model.apply_to_sell(price)
                    proceeds = self.position * actual_price
                    cost = self.cost_model.calculate_sell_cost(actual_price, self.position)
                    
                    self.cash = proceeds - cost
                    trades.append(Trade(
                        price=actual_price,
                        size=-self.position,
                        cash_after=self.cash,
                        position_after=0.0,
                        type="STOP_LOSS"
                    ))
                    self.position = 0.0
                    entry_price = None
                    self.risk_monitor.clear_position()
                
                elif self.risk_monitor.check_take_profit(entry_price, price):
                    # 触发止盈
                    actual_price = self.slippage_model.apply_to_sell(price)
                    proceeds = self.position * actual_price
                    cost = self.cost_model.calculate_sell_cost(actual_price, self.position)
                    
                    self.cash = proceeds - cost
                    trades.append(Trade(
                        price=actual_price,
                        size=-self.position,
                        cash_after=self.cash,
                        position_after=0.0,
                        type="TAKE_PROFIT"
                    ))
                    self.position = 0.0
                    entry_price = None
                    self.risk_monitor.clear_position()

            # 当前总资产
            equity = self.cash + self.position * price
            equity_curve.append(equity)

        # 强制平仓
        if self.position > 0:
            actual_price = self.slippage_model.apply_to_sell(self.prices[-1])
            proceeds = self.position * actual_price
            cost = self.cost_model.calculate_sell_cost(actual_price, self.position)
            
            self.cash = proceeds - cost
            self.position = 0.0
            equity_curve[-1] = self.cash
            
            trades.append(Trade(
                price=actual_price,
                size=-self.position,
                cash_after=self.cash,
                position_after=0.0,
                type="FORCE_EXIT"
            ))

        return BacktestResult(
            symbol=self.symbol,
            initial_cash=self.initial_cash,
            final_equity=equity_curve[-1],
            equity_curve=equity_curve,
            trades=trades,
        )