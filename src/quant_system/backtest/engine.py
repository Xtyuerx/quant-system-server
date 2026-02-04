from quant_system.backtest.result import BacktestResult
from quant_system.backtest.trade import Trade

class BacktestEngine:
    def __init__(
        self,
        prices: list[float],
        signals: list,
        symbol: str,
        initial_cash: float = 100_000,
    ):
        self.prices = prices
        self.signals = signals
        self.symbol = symbol

        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0  # 持有股数（必须是 float）

    def run(self) -> BacktestResult:
        """
        执行回测，返回标准结果对象
        """
        equity_curve: list[float] = []
        trades: list[Trade] = []  # ✅ 记录交易

        for i, price in enumerate(self.prices):
            signal = self.signals[i]

            # 买入：全仓
            if signal.name == "BUY" and self.position == 0:
                shares = self.cash / price
                self.position = shares
                self.cash = 0.0
                # ✅ 记录交易
                trades.append(Trade(
                    price=price,
                    size=shares,
                    cash_after=self.cash,
                    position_after=self.position,
                    type="BUY"
                ))

            # 卖出：清仓
            elif signal.name == "EXIT" and self.position > 0:
                shares_sold = self.position
                self.cash = self.position * price
                self.position = 0.0
                # ✅ 记录交易
                trades.append(Trade(
                    price=price,
                    size=-shares_sold,
                    cash_after=self.cash,
                    position_after=self.position,
                    type="EXIT"
                ))

            # 当前总资产
            equity = self.cash + self.position * price
            equity_curve.append(equity)

        # 强制平仓
        if self.position > 0:
            shares_sold = self.position
            self.cash = self.position * self.prices[-1]
            self.position = 0.0
            equity_curve[-1] = self.cash
            # ✅ 记录强制平仓
            trades.append(Trade(
                price=self.prices[-1],
                size=-shares_sold,
                cash_after=self.cash,
                position_after=0.0,
                type="FORCE_EXIT"
            ))

        # ✅ 返回标准结果对象
        return BacktestResult(
            symbol=self.symbol,
            initial_cash=self.initial_cash,
            final_equity=equity_curve[-1],
            equity_curve=equity_curve,
        )