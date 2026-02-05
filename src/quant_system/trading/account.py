from dataclasses import dataclass
from typing import Dict

@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float
    
    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_cost) * self.quantity
    
    @property
    def unrealized_pnl_pct(self) -> float:
        return (self.current_price / self.avg_cost - 1) if self.avg_cost > 0 else 0


class Account:
    """模拟账户"""
    
    def __init__(self, initial_cash: float = 100_000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        
        # 历史记录
        self.equity_curve = [initial_cash]
        self.trade_history = []
    
    @property
    def total_equity(self) -> float:
        """总资产"""
        position_value = sum(p.market_value for p in self.positions.values())
        return self.cash + position_value
    
    @property
    def total_pnl(self) -> float:
        """总盈亏"""
        return self.total_equity - self.initial_cash
    
    @property
    def total_pnl_pct(self) -> float:
        """总收益率"""
        return (self.total_equity / self.initial_cash - 1) * 100
    
    def update_position(self, fill: Fill):
        """更新持仓"""
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
            self.cash -= fill.quantity * fill.price + fill.commission
        
        else:
            # 卖出
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.quantity -= fill.quantity
                
                # 增加资金
                self.cash += fill.quantity * fill.price - fill.commission
                
                # 如果持仓清零，移除
                if pos.quantity <= 0:
                    del self.positions[symbol]
        
        self.trade_history.append(fill)
    
    def update_prices(self, prices: Dict[str, float]):
        """更新持仓市价"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price
        
        self.equity_curve.append(self.total_equity)
    
    def get_summary(self) -> dict:
        """账户摘要"""
        return {
            'cash': self.cash,
            'total_equity': self.total_equity,
            'total_pnl': self.total_pnl,
            'total_pnl_pct': self.total_pnl_pct,
            'positions': len(self.positions),
            'trades': len(self.trade_history)
        }