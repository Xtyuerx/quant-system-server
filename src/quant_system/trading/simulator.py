# src/quant_system/trading/simulator.py

from typing import Optional
import random

class MatchingEngine:
    """模拟撮合引擎"""
    
    def __init__(self, slippage_model=None):
        self.slippage_model = slippage_model
        self.pending_orders: list[Order] = []
    
    def add_order(self, order: Order):
        """添加订单到撮合队列"""
        self.pending_orders.append(order)
    
    def match_orders(self, current_bar: BarData) -> list[Fill]:
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
            fill_price = self._calculate_fill_price(order, bar)
            commission = self._calculate_commission(order, fill_price)
            
            return Fill(
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
            if order.side == OrderSide.BUY:
                # 买单：当前价 <= 限价
                if bar.close <= order.price:
                    fill_price = order.price
                else:
                    return None
            else:
                # 卖单：当前价 >= 限价
                if bar.close >= order.price:
                    fill_price = order.price
                else:
                    return None
            
            commission = self._calculate_commission(order, fill_price)
            
            return Fill(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                commission=commission,
                timestamp=bar.timestamp
            )
        
        return None
    
    def _calculate_fill_price(self, order: Order, bar: BarData) -> float:
        """
        计算成交价格（考虑滑点）
        
        市价单成交逻辑：
        - 买入：在 [close, high] 之间随机
        - 卖出：在 [low, close] 之间随机
        """
        if order.side == OrderSide.BUY:
            # 买入时价格偏高
            base_price = bar.close
            slippage = random.uniform(0, bar.high - bar.close)
            return base_price + slippage
        else:
            # 卖出时价格偏低
            base_price = bar.close
            slippage = random.uniform(0, bar.close - bar.low)
            return base_price - slippage
    
    def _calculate_commission(self, order: Order, price: float) -> float:
        """计算手续费"""
        # 万三佣金
        commission_rate = 0.0003
        min_commission = 5.0
        
        commission = price * order.quantity * commission_rate
        return max(commission, min_commission)