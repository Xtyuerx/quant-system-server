from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

class OrderType(Enum):
    """订单类型"""
    MARKET = "market"          # 市价单
    LIMIT = "limit"            # 限价单
    STOP = "stop"              # 止损单
    STOP_LIMIT = "stop_limit"  # 止损限价单

class OrderSide(Enum):
    """买卖方向"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"          # 待提交
    SUBMITTED = "submitted"      # 已提交
    PARTIAL_FILLED = "partial"   # 部分成交
    FILLED = "filled"            # 全部成交
    CANCELLED = "cancelled"      # 已撤销
    REJECTED = "rejected"        # 被拒绝

@dataclass
class Order:
    """订单对象"""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None  # 限价单需要
    status: OrderStatus = OrderStatus.PENDING
    
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    
    create_time: datetime = field(default_factory=datetime.now)
    update_time: datetime = field(default_factory=datetime.now)
    
    # 可选字段
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"  # GTC=Good Till Cancel
    
    def __repr__(self):
        return (f"Order({self.order_id}: {self.side.value} {self.quantity} "
                f"{self.symbol}@{self.order_type.value}, status={self.status.value})")


@dataclass
class Fill:
    """成交记录"""
    fill_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    commission: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __repr__(self):
        return (f"Fill({self.symbol}: {self.side.value} {self.quantity}@{self.price:.2f}, "
                f"commission={self.commission:.2f})")


class OrderManager:
    """订单管理器"""
    
    def __init__(self):
        self.orders: dict[str, Order] = {}
        self.fills: list[Fill] = []
        self._order_counter = 0
        self._fill_counter = 0
    
    def create_order(
        self,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: float,
        price: Optional[float] = None
    ) -> Order:
        """创建订单"""
        self._order_counter += 1
        order_id = f"ORD_{datetime.now().strftime('%Y%m%d')}_{self._order_counter:06d}"
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price
        )
        
        self.orders[order_id] = order
        return order
    
    def submit_order(self, order: Order) -> bool:
        """提交订单"""
        if order.status != OrderStatus.PENDING:
            print(f"⚠️ 订单 {order.order_id} 状态异常: {order.status}")
            return False
        
        order.status = OrderStatus.SUBMITTED
        order.update_time = datetime.now()
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.update_time = datetime.now()
        return True
    
    def on_fill(self, fill: Fill):
        """处理成交"""
        order = self.orders.get(fill.order_id)
        if not order:
            print(f"⚠️ 未找到订单: {fill.order_id}")
            return
        
        # 更新订单成交信息
        order.filled_quantity += fill.quantity
        
        # 计算平均成交价
        total_value = order.avg_fill_price * (order.filled_quantity - fill.quantity)
        total_value += fill.price * fill.quantity
        order.avg_fill_price = total_value / order.filled_quantity
        
        # 更新状态
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL_FILLED
        
        order.update_time = datetime.now()
        self.fills.append(fill)
    
    def get_active_orders(self) -> list[Order]:
        """获取活跃订单"""
        return [o for o in self.orders.values() 
                if o.status in [OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]]
    
    def get_order_history(self, symbol: Optional[str] = None) -> list[Order]:
        """获取订单历史"""
        if symbol:
            return [o for o in self.orders.values() if o.symbol == symbol]
        return list(self.orders.values())