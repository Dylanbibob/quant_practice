import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import datetime
import logging

logger = logging.getLogger()

def plot_realtime_chart(data_file, stock_code):
    """
    实时绘制股票分时图
    
    Args:
        data_file: 数据文件路径
        stock_code: 股票代码
    """
    plt.style.use('ggplot')
    
    # 创建图形和子图
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.canvas.manager.set_window_title(f'{stock_code} 实时分时图')
    
    # 数据线
    line, = ax.plot([], [], 'b-', linewidth=1.5, label='价格')
    
    # 设置图表标题和轴标签
    ax.set_title(f'{stock_code} 实时行情', fontsize=14)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('价格 (元)', fontsize=12)
    
    # 添加图例
    ax.legend(loc='upper left')
    
    # 设置时间格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 配置自适应坐标轴
    plt.tight_layout()
    
    def init():
        """初始化画布"""
        return line,
    
    def update(frame):
        """更新图表数据"""
        try:
            if os.path.exists(data_file):
                # 读取CSV数据
                df = pd.read_csv(data_file)
                
                if len(df) == 0:
                    return line,
                
                # 转换时间列为datetime对象
                df['fetch_time'] = pd.to_datetime(df['fetch_time'])
                
                # 获取价格数据
                times = df['fetch_time']
                prices = df['price'].astype(float)
                
                # 更新数据
                line.set_data(times, prices)
                
                # 动态调整x轴范围
                ax.set_xlim(times.min(), times.max())
                
                # 动态调整y轴范围，增加一些边距
                min_price = prices.min() * 0.998
                max_price = prices.max() * 1.002
                ax.set_ylim(min_price, max_price)
                
                # 更新标题，显示当前价格
                current_price = prices.iloc[-1]
                ax.set_title(f'{stock_code} 实时行情 - 当前价格: {current_price:.2f}元', fontsize=14)
                
                # 旋转x轴标签，防止重叠
                plt.xticks(rotation=45)
                
                fig.canvas.draw_idle()
        except Exception as e:
            logger.error(f"绘图更新出错: {e}")
        
        return line,
    
    # 创建动画，每5秒更新一次
    ani = FuncAnimation(
        fig, update, init_func=init, interval=5000, blit=True
    )
    
    # 显示图表
    plt.show()
