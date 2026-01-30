from typing import List
from quant_system.strategy.signal import Signal, SignalType
from quant_system.backtest.result import BacktestResult
from quant_system.backtest.trade import Trade

class SimpleBacktest:
    def __init__(self, prices, signals, initial_cash=100_000):
        self.prices = prices
        self.signals = signals
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0
        self.equity_curve = []
        self.trades: list[Trade] = []

    def run(self, max_drawdown_limit: float = -0.1):
        peak_equity = self.initial_cash

        for price, signal in zip(self.prices, self.signals):
            # === 正常交易逻辑 ===
            if signal.type == SignalType.BUY and self.cash > 0:
                size = self.cash / price
                self.position = size
                self.cash = 0
                self.trades.append(Trade(price, size, self.cash, self.position, "BUY"))

            elif signal.type == SignalType.SELL and self.position > 0:
                size = -self.position
                self.cash = self.position * price
                self.position = 0
                self.trades.append(Trade(price, size, self.cash, self.position, "SELL"))

            # === 计算权益 ===
            equity = self.cash + self.position * price
            self.equity_curve.append(equity)

            # === 风控止损 ===
            if equity > peak_equity:
                peak_equity = equity

            drawdown = (equity / peak_equity) - 1
            if drawdown <= max_drawdown_limit and self.position > 0:
                # 强制平仓
                size = -self.position
                self.cash = self.position * price
                self.position = 0
                self.trades.append(Trade(price, size, self.cash, self.position, "SELL_STOP"))
                # equity_curve 更新
                equity = self.cash
                self.equity_curve[-1] = equity

        return BacktestResult(equity_curve=self.equity_curve)