from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class OrderType(Enum):
    """订单类型"""
    MARKET = "market"      # 市价单
    LIMIT = "limit"        # 限价单
    STOP = "stop"          # 止损单
    STOP_LIMIT = "stop_limit"

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
    
    create_time: datetime = None
    update_time: datetime = None
    
    def __post_init__(self):
        if self.create_time is None:
            self.create_time = datetime.now()
        self.update_time = self.create_time


@dataclass
class Fill:
    """成交记录"""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    commission: float
    timestamp: datetime


class OrderManager:
    """订单管理器"""
    
    def __init__(self):
        self.orders: dict[str, Order] = {}
        self.fills: list[Fill] = []
        self._order_counter = 0
    
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
        # 风控检查在这里
        order.status = OrderStatus.SUBMITTED
        order.update_time = datetime.now()
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            self.orders[order_id].update_time = datetime.now()
            return True
        return False
    
    def on_fill(self, fill: Fill):
        """处理成交"""
        order = self.orders.get(fill.order_id)
        if not order:
            return
        
        order.filled_quantity += fill.quantity
        order.avg_fill_price = (
            (order.avg_fill_price * (order.filled_quantity - fill.quantity) + 
             fill.price * fill.quantity) / order.filled_quantity
        )
        
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL_FILLED
        
        order.update_time = datetime.now()
        self.fills.append(fill)