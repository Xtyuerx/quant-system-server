from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class BacktestResult:
    symbol: str
    initial_cash: float
    final_equity: float
    equity_curve: List[float]
    trades: Optional[List] = None  # ✅ 新增：交易记录
    params: Optional[dict] = None

    # 内部缓存字段
    _total_return: Optional[float] = None
    _max_drawdown: Optional[float] = None
    _sharpe_ratio: Optional[float] = None
    _annual_return: Optional[float] = None
    _annual_volatility: Optional[float] = None
    _win_rate: Optional[float] = None
    _num_trades: Optional[int] = None
    _avg_trade_return: Optional[float] = None
    _profit_factor: Optional[float] = None

    @property
    def total_return(self) -> float:
        """总收益率"""
        if self._total_return is None:
            self._total_return = (self.final_equity / self.initial_cash) - 1
        return self._total_return

    @property
    def max_drawdown(self) -> float:
        """最大回撤（返回负值，如 -0.2 表示 -20%）"""
        if self._max_drawdown is None:
            peak = self.equity_curve[0]
            max_dd = 0.0

            for equity in self.equity_curve:
                peak = max(peak, equity)
                drawdown = (equity - peak) / peak
                max_dd = min(max_dd, drawdown)

            self._max_drawdown = max_dd

        return self._max_drawdown

    @property
    def sharpe_ratio(self) -> float:
        """
        夏普比率
        公式：(年化收益 - 无风险利率) / 年化波动率
        """
        if self._sharpe_ratio is None:
            if len(self.equity_curve) < 2:
                return 0.0

            # 计算日收益率
            equity_array = np.array(self.equity_curve)
            daily_returns = np.diff(equity_array) / equity_array[:-1]

            if len(daily_returns) == 0:
                return 0.0

            # 年化波动率
            annual_vol = np.std(daily_returns, ddof=1) * np.sqrt(252)

            if annual_vol == 0:
                return 0.0

            # 无风险利率（假设 3%）
            risk_free_rate = 0.03

            # Sharpe = (年化收益 - 无风险利率) / 年化波动率
            self._sharpe_ratio = (self.annual_return - risk_free_rate) / annual_vol

        return self._sharpe_ratio

    @property
    def annual_return(self) -> float:
        """
        年化收益率
        假设 equity_curve 是日线数据
        """
        if self._annual_return is None:
            n_days = len(self.equity_curve)
            if n_days == 0:
                return 0.0

            # 年化公式：(1 + 总收益率)^(252/天数) - 1
            self._annual_return = (1 + self.total_return) ** (252 / n_days) - 1

        return self._annual_return

    @property
    def annual_volatility(self) -> float:
        """年化波动率"""
        if self._annual_volatility is None:
            if len(self.equity_curve) < 2:
                return 0.0

            equity_array = np.array(self.equity_curve)
            daily_returns = np.diff(equity_array) / equity_array[:-1]

            # 年化波动率 = 日波动率 * sqrt(252)
            self._annual_volatility = np.std(daily_returns, ddof=1) * np.sqrt(252)

        return self._annual_volatility

    @property
    def num_trades(self) -> int:
        """交易次数"""
        if self._num_trades is None:
            if self.trades is None:
                return 0
            # 只统计开仓交易（BUY）
            self._num_trades = sum(1 for t in self.trades if t.type == "BUY")
        return self._num_trades

    @property
    def win_rate(self) -> float:
        """
        胜率（盈利交易 / 总交易）
        需要配对买卖计算
        """
        if self._win_rate is None:
            if self.trades is None or len(self.trades) == 0:
                return 0.0

            # 简化实现：配对买入和卖出
            buy_trades = [t for t in self.trades if t.type == "BUY"]
            sell_trades = [t for t in self.trades if t.type in ["EXIT", "FORCE_EXIT"]]

            if len(buy_trades) == 0 or len(sell_trades) == 0:
                return 0.0

            wins = 0
            for i, (buy, sell) in enumerate(zip(buy_trades, sell_trades)):
                profit = (sell.price - buy.price) * buy.size
                if profit > 0:
                    wins += 1

            self._win_rate = wins / min(len(buy_trades), len(sell_trades))

        return self._win_rate

    @property
    def avg_trade_return(self) -> float:
        """平均单笔收益率"""
        if self._avg_trade_return is None:
            if self.trades is None or len(self.trades) == 0:
                return 0.0

            buy_trades = [t for t in self.trades if t.type == "BUY"]
            sell_trades = [t for t in self.trades if t.type in ["EXIT", "FORCE_EXIT"]]

            if len(buy_trades) == 0 or len(sell_trades) == 0:
                return 0.0

            returns = []
            for buy, sell in zip(buy_trades, sell_trades):
                ret = (sell.price - buy.price) / buy.price
                returns.append(ret)

            self._avg_trade_return = np.mean(returns)

        return self._avg_trade_return

    @property
    def profit_factor(self) -> float:
        """
        盈亏比（总盈利 / 总亏损）
        > 1 表示盈利大于亏损
        """
        if self._profit_factor is None:
            if self.trades is None or len(self.trades) == 0:
                return 0.0

            buy_trades = [t for t in self.trades if t.type == "BUY"]
            sell_trades = [t for t in self.trades if t.type in ["EXIT", "FORCE_EXIT"]]

            if len(buy_trades) == 0 or len(sell_trades) == 0:
                return 0.0

            total_profit = 0.0
            total_loss = 0.0

            for buy, sell in zip(buy_trades, sell_trades):
                pnl = (sell.price - buy.price) * buy.size
                if pnl > 0:
                    total_profit += pnl
                else:
                    total_loss += abs(pnl)

            if total_loss == 0:
                return float('inf') if total_profit > 0 else 0.0

            self._profit_factor = total_profit / total_loss

        return self._profit_factor

    def summary(self) -> dict:
        """返回所有关键指标"""
        return {
            "symbol": self.symbol,
            "final_equity": self.final_equity,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "annual_volatility": self.annual_volatility,
            "num_trades": self.num_trades,
            "win_rate": self.win_rate,
            "avg_trade_return": self.avg_trade_return,
            "profit_factor": self.profit_factor,
        }

    def to_row(self) -> dict:
        """格式化输出（用于表格显示）"""
        row = {
            "symbol": self.symbol,
            "final_equity": f"{self.final_equity:,.2f}",
            "total_return": f"{self.total_return * 100:.2f}%",
            "annual_return": f"{self.annual_return * 100:.2f}%",
            "max_drawdown": f"{self.max_drawdown * 100:.2f}%",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "win_rate": f"{self.win_rate * 100:.1f}%",
            "num_trades": self.num_trades,
        }
        if self.params:
            row.update(self.params)
        return row

    def to_dict(self) -> dict:
        """返回原始数值（用于程序处理）"""
        row = {
            "symbol": self.symbol,
            "final_equity": self.final_equity,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "annual_volatility": self.annual_volatility,
            "num_trades": self.num_trades,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
        }
        if self.params:
            row.update(self.params)
        return row