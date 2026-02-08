from typing import Optional, List
import random
from .order import Order, Fill, OrderType, OrderSide, OrderStatus
from ..data.live_feed import BarData
from datetime import datetime

class MatchingEngine:
    """模拟撮合引擎"""
    
    def __init__(self, commission_rate: float = 0.0003, min_commission: float = 5.0):
        """
        Args:
            commission_rate: 佣金费率（默认万三）
            min_commission: 最小佣金（默认5元）
        """
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.pending_orders: List[Order] = []
        self._fill_counter = 0
    
    def add_order(self, order: Order):
        """添加订单到撮合队列"""
        self.pending_orders.append(order)
        print(f"📝 订单入队: {order}")
    
    def match_orders(self, current_bar: BarData) -> List[Fill]:
        """
        根据当前行情撮合订单
        
        模拟真实市场的撮合逻辑：
        - 市价单：立即成交（考虑滑点）
        - 限价单：价格满足时成交
        """
        fills = []
        matched_orders = []
        
        for order in self.pending_orders:
            if order.status != OrderStatus.SUBMITTED:
                continue
            
            if order.symbol != current_bar.symbol:
                continue
            
            fill = self._try_match(order, current_bar)
            if fill:
                fills.append(fill)
                matched_orders.append(order)
        
        # 移除已成交订单
        for order in matched_orders:
            self.pending_orders.remove(order)
        
        return fills
    
    def _try_match(self, order: Order, bar: BarData) -> Optional[Fill]:
        """尝试撮合单个订单"""
        
        # 市价单立即成交
        if order.order_type == OrderType.MARKET:
            fill_price = self._calculate_fill_price_market(order, bar)
            commission = self._calculate_commission(order.quantity, fill_price)
            
            self._fill_counter += 1
            fill_id = f"FILL_{datetime.now().strftime('%Y%m%d')}_{self._fill_counter:06d}"
            
            return Fill(
                fill_id=fill_id,
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                commission=commission,
                timestamp=bar.timestamp
            )
        
        # 限价单需要价格满足
        elif order.order_type == OrderType.LIMIT:
            if order.price is None:
                print(f"⚠️ 限价单缺少价格: {order.order_id}")
                return None
            
            can_fill = False
            fill_price = order.price
            
            if order.side == OrderSide.BUY:
                # 买单：当前价 <= 限价
                if bar.low <= order.price:
                    can_fill = True
            else:
                # 卖单：当前价 >= 限价
                if bar.high >= order.price:
                    can_fill = True
            
            if can_fill:
                commission = self._calculate_commission(order.quantity, fill_price)
                
                self._fill_counter += 1
                fill_id = f"FILL_{datetime.now().strftime('%Y%m%d')}_{self._fill_counter:06d}"
                
                return Fill(
                    fill_id=fill_id,
                    order_id=order.order_id,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=fill_price,
                    commission=commission,
                    timestamp=bar.timestamp
                )
        
        return None
    
    def _calculate_fill_price_market(self, order: Order, bar: BarData) -> float:
        """
        计算市价单成交价格（考虑滑点）
        
        简化模型：
        - 买入：在 [close, high] 之间随机
        - 卖出：在 [low, close] 之间随机
        """
        if order.side == OrderSide.BUY:
            # 买入时价格偏高（滑点）
            if bar.high > bar.close:
                slippage_range = bar.high - bar.close
                slippage = random.uniform(0, slippage_range * 0.5)  # 50%的滑点范围
                return bar.close + slippage
            return bar.close
        else:
            # 卖出时价格偏低（滑点）
            if bar.close > bar.low:
                slippage_range = bar.close - bar.low
                slippage = random.uniform(0, slippage_range * 0.5)
                return bar.close - slippage
            return bar.close
    
    def _calculate_commission(self, quantity: float, price: float) -> float:
        """计算手续费"""
        commission = price * quantity * self.commission_rate
        return max(commission, self.min_commission)
    
    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        for order in self.pending_orders:
            if order.order_id == order_id:
                order.status = OrderStatus.CANCELLED
                self.pending_orders.remove(order)
                return True
        return False