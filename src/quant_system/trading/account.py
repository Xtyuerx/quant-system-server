from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float
    update_time: datetime = None
    
    def __post_init__(self):
        if self.update_time is None:
            self.update_time = datetime.now()
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """成本"""
        return self.quantity * self.avg_cost
    
    @property
    def unrealized_pnl(self) -> float:
        """浮动盈亏"""
        return (self.current_price - self.avg_cost) * self.quantity
    
    @property
    def unrealized_pnl_pct(self) -> float:
        """浮动盈亏率"""
        if self.avg_cost == 0:
            return 0.0
        return (self.current_price / self.avg_cost - 1) * 100
    
    def __repr__(self):
        return (f"Position({self.symbol}: {self.quantity}@{self.avg_cost:.2f}, "
                f"PnL={self.unrealized_pnl:.2f}({self.unrealized_pnl_pct:.2f}%))")


class Account:
    """模拟账户"""
    
    def __init__(self, initial_cash: float = 100_000, account_id: str = "PAPER001"):
        self.account_id = account_id
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        
        # 历史记录
        self.equity_curve: List[float] = [initial_cash]
        self.trade_history: List = []
        self.daily_pnl: List[float] = []
        
        # 统计
        self.total_commission = 0.0
        self.num_trades = 0
        self.num_wins = 0
        self.num_losses = 0
    
    @property
    def total_position_value(self) -> float:
        """持仓总市值"""
        return sum(pos.market_value for pos in self.positions.values())
    
    @property
    def total_equity(self) -> float:
        """总资产"""
        return self.cash + self.total_position_value
    
    @property
    def total_pnl(self) -> float:
        """总盈亏"""
        return self.total_equity - self.initial_cash
    
    @property
    def total_pnl_pct(self) -> float:
        """总收益率 (%)"""
        return (self.total_equity / self.initial_cash - 1) * 100
    
    @property
    def buying_power(self) -> float:
        """可用购买力"""
        return self.cash
    
    def update_position(self, fill):
        """根据成交更新持仓"""
        from .order import OrderSide
        
        symbol = fill.symbol
        
        if fill.side == OrderSide.BUY:
            # 买入
            if symbol in self.positions:
                pos = self.positions[symbol]
                new_quantity = pos.quantity + fill.quantity
                new_avg_cost = (
                    (pos.avg_cost * pos.quantity + fill.price * fill.quantity) 
                    / new_quantity
                )
                pos.quantity = new_quantity
                pos.avg_cost = new_avg_cost
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=fill.quantity,
                    avg_cost=fill.price,
                    current_price=fill.price
                )
            
            # 扣除资金
            cost = fill.quantity * fill.price + fill.commission
            self.cash -= cost
            
        else:
            # 卖出
            if symbol not in self.positions:
                print(f"⚠️ 警告: 卖出不存在的持仓 {symbol}")
                return
            
            pos = self.positions[symbol]
            pos.quantity -= fill.quantity
            
            # 增加资金
            proceeds = fill.quantity * fill.price - fill.commission
            self.cash += proceeds
            
            # 计算已实现盈亏
            realized_pnl = (fill.price - pos.avg_cost) * fill.quantity - fill.commission
            if realized_pnl > 0:
                self.num_wins += 1
            else:
                self.num_losses += 1
            
            # 如果持仓清零，移除
            if pos.quantity <= 0.001:  # 浮点数比较
                del self.positions[symbol]
        
        # 统计
        self.total_commission += fill.commission
        self.num_trades += 1
        self.trade_history.append(fill)
    
    def update_prices(self, prices: Dict[str, float]):
        """更新持仓市价"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price
                self.positions[symbol].update_time = datetime.now()
        
        # 记录权益曲线
        self.equity_curve.append(self.total_equity)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取持仓"""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """是否持有仓位"""
        return symbol in self.positions
    
    def get_summary(self) -> dict:
        """账户摘要"""
        return {
            'account_id': self.account_id,
            'cash': self.cash,
            'position_value': self.total_position_value,
            'total_equity': self.total_equity,
            'total_pnl': self.total_pnl,
            'total_pnl_pct': self.total_pnl_pct,
            'num_positions': len(self.positions),
            'num_trades': self.num_trades,
            'total_commission': self.total_commission,
            'win_rate': self.num_wins / max(self.num_trades, 1) * 100,
        }
    
    def print_summary(self):
        """打印账户摘要"""
        summary = self.get_summary()
        print("\n" + "="*60)
        print(f"📊 账户摘要 [{summary['account_id']}]")
        print("="*60)
        print(f"💰 现金: {summary['cash']:,.2f}")
        print(f"📈 持仓市值: {summary['position_value']:,.2f}")
        print(f"💎 总资产: {summary['total_equity']:,.2f}")
        print(f"📊 总盈亏: {summary['total_pnl']:+,.2f} ({summary['total_pnl_pct']:+.2f}%)")
        print(f"🎯 持仓数: {summary['num_positions']}")
        print(f"📝 交易次数: {summary['num_trades']}")
        print(f"💸 手续费: {summary['total_commission']:.2f}")
        print(f"🏆 胜率: {summary['win_rate']:.1f}%")
        print("="*60)
        
        if self.positions:
            print("\n持仓明细:")
            for pos in self.positions.values():
                print(f"  {pos}")