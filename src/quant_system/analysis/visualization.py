import matplotlib.pyplot as plt
from quant_system.backtest.trade import Trade
from typing import List


def plot_advanced_backtest(prices: List[float],
                           equity_curve: List[float],
                           trades: List[Trade],
                           title: str = "Backtest Result",
                           save_path: str = None):
    """
    高级回测可视化
    - 蓝色折线: equity_curve
    - 黑色折线: price
    - 橙色折线: 持仓量
    - 交易点标注: BUY/SELL/SELL_STOP
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # equity_curve
    ax1.plot(equity_curve, label="Equity Curve", color="blue")
    ax1.set_xlabel("Time Step")
    ax1.set_ylabel("Equity", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")

    # 价格曲线共用 X 轴
    ax2 = ax1.twinx()
    ax2.plot(prices, label="Price", color="black", alpha=0.5)
    ax2.set_ylabel("Price", color="black")
    ax2.tick_params(axis='y', labelcolor="black")

    # 持仓量曲线
    positions = []
    pos = 0
    for trade in trades:
        pos += trade.size
        positions.append(pos)
    # 如果 positions 长度不够，补最后一个值
    while len(positions) < len(prices):
        positions.append(positions[-1] if positions else 0)

    ax2.plot(positions, label="Position", color="orange", linestyle="--")

    # 标记交易点
    for trade in trades:
        idx = min(len(prices)-1, trades.index(trade))
        if trade.type == "BUY":
            ax2.scatter(idx, prices[idx], marker="^", color="green", s=100, label="BUY")
        elif trade.type in ["SELL", "SELL_STOP"]:
            ax2.scatter(idx, prices[idx], marker="v", color="red", s=100, label=trade.type)

    # 图例
    fig.legend(loc="upper left")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved backtest plot to {save_path}")

    plt.show()
