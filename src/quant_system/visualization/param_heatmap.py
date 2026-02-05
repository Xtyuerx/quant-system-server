"""
参数优化结果热力图可视化

用于展示参数扫描的结果，帮助找到最优参数组合
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Optional
from quant_system.report.result_table import ResultTable


def plot_param_heatmap(
    results: ResultTable,
    x_param: str,
    y_param: str,
    metric: str = "sharpe_ratio",
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    figsize=(10, 8)
):
    """
    绘制参数优化热力图
    
    Args:
        results: 参数扫描结果
        x_param: X 轴参数名（如 "window"）
        y_param: Y 轴参数名（如 "threshold"）
        metric: 要展示的指标（如 "sharpe_ratio", "total_return"）
        title: 图表标题
        save_path: 保存路径
        figsize: 图表尺寸
    
    Example:
        >>> results = run_param_scan(...)
        >>> plot_param_heatmap(results, "window", "threshold", "sharpe_ratio")
    """
    # 提取数据
    data = [r.to_dict() for r in results.results]
    df = pd.DataFrame(data)
    
    # 检查参数是否存在
    if x_param not in df.columns or y_param not in df.columns:
        raise ValueError(f"参数 {x_param} 或 {y_param} 不在结果中")
    
    if metric not in df.columns:
        raise ValueError(f"指标 {metric} 不在结果中")
    
    # 创建透视表
    pivot_table = df.pivot_table(
        values=metric,
        index=y_param,
        columns=x_param,
        aggfunc='mean'  # 如果有重复，取平均
    )
    
    # 绘制热力图
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(pivot_table.values, cmap='RdYlGn', aspect='auto')
    
    # 设置坐标轴标签
    ax.set_xticks(np.arange(len(pivot_table.columns)))
    ax.set_yticks(np.arange(len(pivot_table.index)))
    ax.set_xticklabels(pivot_table.columns)
    ax.set_yticklabels(pivot_table.index)
    
    # 标签
    ax.set_xlabel(x_param, fontsize=12)
    ax.set_ylabel(y_param, fontsize=12)
    
    if title is None:
        title = f"{metric.replace('_', ' ').title()} Heatmap"
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # 在每个格子中显示数值
    for i in range(len(pivot_table.index)):
        for j in range(len(pivot_table.columns)):
            value = pivot_table.values[i, j]
            if not np.isnan(value):
                text = ax.text(j, i, f'{value:.2f}',
                             ha="center", va="center",
                             color="black", fontsize=9)
    
    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(metric.replace('_', ' ').title(), rotation=270, labelpad=20)
    
    # 标注最优参数组合
    max_value = pivot_table.values.max()
    max_pos = np.where(pivot_table.values == max_value)
    if len(max_pos[0]) > 0:
        max_y, max_x = max_pos[0][0], max_pos[1][0]
        ax.plot(max_x, max_y, 'r*', markersize=20, 
                markeredgewidth=2, markeredgecolor='white')
        
        best_x = pivot_table.columns[max_x]
        best_y = pivot_table.index[max_y]
        ax.text(0.02, 0.98, 
                f'Best: {x_param}={best_x}, {y_param}={best_y}\n{metric}={max_value:.2f}',
                transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
                fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 热力图已保存到: {save_path}")
    
    plt.show()


def plot_param_surface_3d(
    results: ResultTable,
    x_param: str,
    y_param: str,
    metric: str = "sharpe_ratio",
    title: Optional[str] = None,
    save_path: Optional[str] = None
):
    """
    绘制 3D 参数曲面图
    
    Args:
        results: 参数扫描结果
        x_param: X 轴参数
        y_param: Y 轴参数
        metric: Z 轴指标
    """
    from mpl_toolkits.mplot3d import Axes3D
    
    data = [r.to_dict() for r in results.results]
    df = pd.DataFrame(data)
    
    pivot_table = df.pivot_table(
        values=metric,
        index=y_param,
        columns=x_param
    )
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    X, Y = np.meshgrid(pivot_table.columns, pivot_table.index)
    Z = pivot_table.values
    
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    
    ax.set_xlabel(x_param)
    ax.set_ylabel(y_param)
    ax.set_zlabel(metric)
    
    if title is None:
        title = f"{metric} vs {x_param} & {y_param}"
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 3D 曲面图已保存到: {save_path}")
    
    plt.show()


def plot_param_comparison_bar(
    results: ResultTable,
    param: str,
    metrics: List[str] = ["sharpe_ratio", "total_return", "max_drawdown"],
    save_path: Optional[str] = None
):
    """
    绘制参数对比柱状图（多指标）
    
    Args:
        results: 参数扫描结果
        param: 要对比的参数
        metrics: 要展示的指标列表
    """
    data = [r.to_dict() for r in results.results]
    df = pd.DataFrame(data)
    
    # 按参数分组，计算指标均值
    grouped = df.groupby(param)[metrics].mean()
    
    fig, axes = plt.subplots(1, len(metrics), figsize=(5*len(metrics), 5))
    
    if len(metrics) == 1:
        axes = [axes]
    
    for i, metric in enumerate(metrics):
        ax = axes[i]
        grouped[metric].plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_title(f"{metric.replace('_', ' ').title()}", fontsize=12, fontweight='bold')
        ax.set_xlabel(param)
        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 对比图已保存到: {save_path}")
    
    plt.show()