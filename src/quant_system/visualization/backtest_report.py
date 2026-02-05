import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
from quant_system.backtest.result import BacktestResult


def calculate_drawdown_series(equity_curve: list[float]) -> np.ndarray:
    """计算回撤序列"""
    equity_array = np.array(equity_curve)
    peak = np.maximum.accumulate(equity_array)
    drawdown = (equity_array - peak) / peak
    return drawdown


def calculate_daily_returns(equity_curve: list[float]) -> np.ndarray:
    """计算日收益率"""
    equity_array = np.array(equity_curve)
    returns = np.diff(equity_array) / equity_array[:-1]
    return returns


def plot_backtest_report(
    result: BacktestResult,
    save_path: Optional[str] = None,
    figsize=(15, 10)
):
    """
    生成综合回测报告（2x2 子图）
    
    Args:
        result: 回测结果对象
        save_path: 保存路径（如 "report.png"），None 则不保存
        figsize: 图表尺寸
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(f"Backtest Report: {result.symbol}", fontsize=16, fontweight='bold')
    
    # ==================== 1. 权益曲线 ====================
    ax1 = axes[0, 0]
    ax1.plot(result.equity_curve, linewidth=2, color='#2E86AB')
    ax1.axhline(y=result.initial_cash, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_title("Equity Curve", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Time (Days)")
    ax1.set_ylabel("Equity ($)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 标注最终收益
    final_y = result.equity_curve[-1]
    ax1.annotate(
        f'Final: ${final_y:,.0f}\n({result.total_return:.1%})',
        xy=(len(result.equity_curve)-1, final_y),
        xytext=(10, 10),
        textcoords='offset points',
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
        fontsize=9
    )
    
    # ==================== 2. 回撤曲线 ====================
    ax2 = axes[0, 1]
    drawdown_series = calculate_drawdown_series(result.equity_curve)
    ax2.fill_between(
        range(len(drawdown_series)),
        drawdown_series * 100,  # 转换为百分比
        0,
        alpha=0.3,
        color='red',
        label='Drawdown'
    )
    ax2.plot(drawdown_series * 100, linewidth=1.5, color='darkred')
    ax2.axhline(y=result.max_drawdown * 100, color='red', linestyle='--', linewidth=2, label=f'Max DD: {result.max_drawdown:.1%}')
    ax2.set_title("Drawdown Curve", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Time (Days)")
    ax2.set_ylabel("Drawdown (%)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # ==================== 3. 收益分布直方图 ====================
    ax3 = axes[1, 0]
    daily_returns = calculate_daily_returns(result.equity_curve)
    
    if len(daily_returns) > 0:
        ax3.hist(daily_returns * 100, bins=50, alpha=0.7, color='#A23B72', edgecolor='black')
        ax3.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
        ax3.set_title("Daily Returns Distribution", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Return (%)")
        ax3.set_ylabel("Frequency")
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 添加统计信息
        mean_ret = np.mean(daily_returns) * 100
        std_ret = np.std(daily_returns) * 100
        ax3.text(
            0.05, 0.95,
            f'Mean: {mean_ret:.3f}%\nStd: {std_ret:.3f}%',
            transform=ax3.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=9
        )
    
    # ==================== 4. 关键指标表格 ====================
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # 构建指标文本
    metrics_data = [
        ["Metric", "Value"],
        ["─" * 25, "─" * 15],
        ["Total Return", f"{result.total_return:.2%}"],
        ["Annual Return", f"{result.annual_return:.2%}"],
        ["Max Drawdown", f"{result.max_drawdown:.2%}"],
        ["Sharpe Ratio", f"{result.sharpe_ratio:.2f}"],
        ["Annual Volatility", f"{result.annual_volatility:.2%}"],
        ["─" * 25, "─" * 15],
        ["Number of Trades", f"{result.num_trades}"],
        ["Win Rate", f"{result.win_rate:.1%}"],
        ["Avg Trade Return", f"{result.avg_trade_return:.2%}"],
        ["Profit Factor", f"{result.profit_factor:.2f}"],
        ["─" * 25, "─" * 15],
        ["Initial Capital", f"${result.initial_cash:,.0f}"],
        ["Final Equity", f"${result.final_equity:,.0f}"],
    ]
    
    # 绘制表格
    table = ax4.table(
        cellText=metrics_data,
        cellLoc='left',
        loc='center',
        colWidths=[0.6, 0.4]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # 美化表头
    for i in range(2):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # 美化分隔行
    for row in [1, 7, 12]:
        for col in range(2):
            table[(row, col)].set_facecolor('#E8E8E8')
    
    ax4.set_title("Performance Metrics", fontsize=12, fontweight='bold', pad=20)
    
    # ==================== 保存和显示 ====================
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Report saved to: {save_path}")
    
    plt.show()


def plot_strategy_comparison(
    results: list[BacktestResult],
    metric: str = "equity_curve",
    title: str = "Strategy Comparison"
):
    """
    多策略对比图
    
    Args:
        results: 回测结果列表
        metric: 对比指标 ("equity_curve" 或 "sharpe_ratio")
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    
    if metric == "equity_curve":
        for result in results:
            label = result.symbol
            if result.params:
                label += " " + ", ".join(f"{k}={v}" for k, v in result.params.items())
            plt.plot(result.equity_curve, label=label, linewidth=2)
        
        plt.xlabel("Time (Days)")
        plt.ylabel("Equity ($)")
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    elif metric == "sharpe_ratio":
        symbols = [r.symbol for r in results]
        sharpe_ratios = [r.sharpe_ratio for r in results]
        
        colors = ['green' if sr > 1 else 'orange' if sr > 0 else 'red' for sr in sharpe_ratios]
        
        plt.bar(symbols, sharpe_ratios, color=colors, alpha=0.7, edgecolor='black')
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        plt.axhline(y=1, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Good (>1)')
        plt.ylabel("Sharpe Ratio")
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()