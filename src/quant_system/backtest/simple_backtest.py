from typing import List
from quant_system.backtest.result import BacktestResult
from quant_system.backtest.trade import Trade
from quant_system.backtest.signal import Signal, SignalType

def calculate_max_drawdown(equity_curve):
        peak = equity_curve[0]
        max_drawdown = 0.0

        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (value - peak) / peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

class SimpleBacktest:
    def __init__(self, prices: List[float], signals: List[Signal], initial_cash: float = 100_000):
        self.prices = prices
        self.signals = signals
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0
        self.equity_curve: List[float] = []
        self.trades: list[Trade] = []

    def run(self, max_drawdown_limit: float = -0.1) -> BacktestResult:
        peak_equity = self.initial_cash
        max_drawdown = 0.0

        for price, signal in zip(self.prices, self.signals):
            # === 正常交易逻辑 ===
            if signal.type == SignalType.BUY and self.cash > 0 and self.position == 0:
                size = self.cash / price
                self.position = size
                self.cash = 0
                self.trades.append(Trade(price, size, self.cash, self.position, SignalType.BUY))

            elif signal.type == SignalType.SELL and self.position > 0 and self.position > 0:
                size = -self.position
                self.cash = self.position * price
                self.position = 0
                self.trades.append(Trade(price, size, self.cash, self.position, SignalType.SELL))

            # === 计算权益 ===
            equity = self.cash + self.position * price
            self.equity_curve.append(equity)

            # === 风控止损 ===
            if equity > peak_equity:
                peak_equity = equity

            drawdown = (equity / peak_equity) - 1
            if drawdown < max_drawdown:
                max_drawdown = drawdown

            if drawdown <= max_drawdown_limit and self.position > 0:
                # 强制平仓
                size = -self.position
                self.cash = self.position * price
                self.position = 0
                self.trades.append(Trade(price, size, self.cash, self.position, SignalType.SELL_STOP))
                equity = self.cash
                self.equity_curve[-1] = equity

        total_return = (self.equity_curve[-1] - self.initial_cash) / self.initial_cash
        max_drawdown = calculate_max_drawdown(self.equity_curve)

        # 如果还有持仓，则强制平仓
        if self.position > 0:
            last_price = self.prices[-1]
            self.cash = self.position * last_price
            self.position = 0
            self.equity_curve[-1] = self.cash
            
        # 打印当前价格、信号、现金、持仓、权益
        print(
            f"price={price:.2f}, signal={signal.type}, "
            f"cash={self.cash:.2f}, position={self.position:.4f}, "
            f"equity={equity:.2f}"
        )

        print("FINAL position:", self.position, "cash:", self.cash)

        return BacktestResult(
            equity_curve=self.equity_curve,
            total_return=total_return,
            max_drawdown=max_drawdown
        )
