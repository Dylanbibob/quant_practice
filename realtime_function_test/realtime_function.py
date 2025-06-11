import os
import time
import datetime
import pandas as pd
import numpy as np
import tushare as ts
import logging
from threading import Thread

# 导入绘图模块
from plotting import plot_realtime_chart

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stock_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Tushare配置
TOKEN = '00e414e1e675fe57036110eb1f115cb501a6a418a5278b261b86f948'
ts.set_token(TOKEN)

# 股票配置
STOCK_CODE = '600900.SH'
DATA_FOLDER = 'stock_data'
REFRESH_INTERVAL = 60  # 请求间隔，单位秒

# 策略参数配置
TIME_POINT = datetime.time(14, 30)  # 检查新高的时间点(2:30)
MA_PERIODS = 20  # 均线周期

# 策略状态
strategy_state = {
    'high_at_time_point': None,  # 时间点的最高价
    'new_high_detected': False,  # 是否检测到新高
    'pullback_started': False,  # 回踩是否已开始
    'pullback_price': None,  # 回踩价格
}

# 确保数据文件夹存在
os.makedirs(DATA_FOLDER, exist_ok=True)

def is_trading_time():
    """
    判断当前是否为A股交易时间
    
    交易时间: 9:30-11:30, 13:00-15:00
    """
    now = datetime.datetime.now()
    # 判断是否为工作日
    if now.weekday() >= 5:  # 0-4为周一至周五
        return False
    
    current_time = now.time()
    morning_start = datetime.time(9, 30, 0)
    morning_end = datetime.time(11, 30, 0)
    afternoon_start = datetime.time(13, 0, 0)
    afternoon_end = datetime.time(15, 0, 0)
    
    # 判断是否在交易时段
    if (morning_start <= current_time <= morning_end) or \
       (afternoon_start <= current_time <= afternoon_end):
        return True
    return False

def get_next_trading_time():
    """计算距离下一个交易时间还有多少秒"""
    now = datetime.datetime.now()
    current_time = now.time()
    current_date = now.date()
    
    # 今日的交易时间点
    today_morning_start = datetime.datetime.combine(current_date, datetime.time(9, 30, 0))
    today_afternoon_start = datetime.datetime.combine(current_date, datetime.time(13, 0, 0))
    
    # 如果当前是工作日
    if now.weekday() < 5:
        # 上午交易前
        if current_time < datetime.time(9, 30, 0):
            return (today_morning_start - now).total_seconds()
        # 午休时间
        elif datetime.time(11, 30, 0) < current_time < datetime.time(13, 0, 0):
            return (today_afternoon_start - now).total_seconds()
    
    # 计算距离下一个工作日
    days_ahead = 1
    while True:
        next_day = now + datetime.timedelta(days=days_ahead)
        if next_day.weekday() < 5:  # 找到下一个工作日
            next_trading_start = datetime.datetime.combine(
                next_day.date(), datetime.time(9, 30, 0)
            )
            return (next_trading_start - now).total_seconds()
        days_ahead += 1

def fetch_stock_data():
    """获取实时股票数据"""
    try:
        df = ts.realtime_quote(ts_code=STOCK_CODE)
        df['fetch_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 确保价格列为数值型
        for col in ['OPEN', 'PRE_CLOSE', 'PRICE', 'HIGH', 'LOW']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        logger.error(f"获取股票数据失败: {e}")
        return None

def calculate_ma(data, period=MA_PERIODS):
    """计算均线"""
    if len(data) >= period:
        return np.mean(data[-period:])
    return None

def check_new_high_and_pullback(all_data):
    """
    检查是否在指定时间点(14:30)附近创下新高，后续是否有回踩但未跌破均线
    
    Args:
        all_data: 包含所有历史数据的DataFrame
        
    Returns:
        pullback_price: 如果检测到回踩但未跌破均线，返回回踩价格，否则返回None
    """
    global strategy_state
    
    # 如果数据不足，直接返回
    if len(all_data) < MA_PERIODS + 5:
        return None
    
    # 确保数据已排序
    all_data = all_data.sort_values('fetch_time')
    all_data['fetch_time'] = pd.to_datetime(all_data['fetch_time'])
    all_data['PRICE'] = pd.to_numeric(all_data['PRICE'], errors='coerce')
    
    # 当前时间
    now = datetime.datetime.now()
    current_time = now.time()
    today_date = now.date()
    
    # 过滤今天的数据
    today_data = all_data[all_data['fetch_time'].dt.date == today_date].copy()
    
    if len(today_data) == 0:
        return None

    # 计算今日最高价
    today_high = today_data['PRICE'].max()
    
    # 计算移动平均线
    today_data['MA'] = today_data['PRICE'].rolling(window=MA_PERIODS).mean()
    
    # 获取最新价格和均线值
    latest_price = today_data['PRICE'].iloc[-1]
    latest_ma = today_data['MA'].iloc[-1] if not pd.isna(today_data['MA'].iloc[-1]) else None
    
    # 时间点(14:30)的数据点
    time_point_datetime = datetime.datetime.combine(today_date, TIME_POINT)
    
    # 寻找时间最接近14:30的数据点
    if strategy_state['high_at_time_point'] is None:
        close_to_time_point = today_data[
            (today_data['fetch_time'] >= time_point_datetime - datetime.timedelta(minutes=2)) & 
            (today_data['fetch_time'] <= time_point_datetime + datetime.timedelta(minutes=2))
        ]
        
        if not close_to_time_point.empty:
            # 找到14:30附近的最高价
            high_at_time_point = close_to_time_point['PRICE'].max()
            strategy_state['high_at_time_point'] = high_at_time_point
            
            # 判断这个价格是否是当日新高
            if high_at_time_point >= today_high * 0.995:  # 允许0.5%的误差范围
                strategy_state['new_high_detected'] = True
                logger.info(f"⚠️ 14:30附近检测到新高: {high_at_time_point:.2f}")
    
    # 如果已经检测到新高，观察后续回踩
    if strategy_state['new_high_detected'] and not strategy_state['pullback_started']:
        # 找到14:30之后的数据
        after_time_point = today_data[today_data['fetch_time'] > time_point_datetime]
        
        # 如果后续有价格回落至少1%，则标记为回踩开始
        if not after_time_point.empty and latest_price < strategy_state['high_at_time_point'] * 0.99:
            strategy_state['pullback_started'] = True
            logger.info(f"⚠️ 检测到价格回踩开始: {latest_price:.2f}")
    
    # 如果回踩已开始，检查是否未跌破均线
    if strategy_state['pullback_started'] and latest_ma is not None:
        if latest_price >= latest_ma and strategy_state['pullback_price'] is None:
            strategy_state['pullback_price'] = latest_price
            logger.info(f"✅ 回踩未跌破均线! 回踩价格: {latest_price:.2f}, 均线: {latest_ma:.2f}")
            return latest_price
    
    return strategy_state['pullback_price']

def main():
    """主函数：定时获取股票数据并保存，同时进行策略分析"""
    # 存储所有获取的数据
    all_data = pd.DataFrame()
    
    # 文件名使用当天日期
    today_str = datetime.datetime.now().strftime('%Y%m%d')
    csv_filename = os.path.join(DATA_FOLDER, f"{STOCK_CODE.replace('.', '_')}_{today_str}.csv")
    
    # 如果文件已存在，加载已有数据
    if os.path.exists(csv_filename):
        all_data = pd.read_csv(csv_filename)
        logger.info(f"加载已有数据: {len(all_data)}条记录")
    
    # 启动绘图线程
    plot_thread = Thread(target=plot_realtime_chart, args=(csv_filename, STOCK_CODE))
    plot_thread.daemon = True
    plot_thread.start()
    
    logger.info(f"开始监控股票: {STOCK_CODE}")
    
    try:
        while True:
            if is_trading_time():
                logger.info("当前为交易时间，获取股票数据...")
                
                # 获取实时数据
                start_time = time.time()
                df = fetch_stock_data()
                request_time = time.time() - start_time
                
                if df is not None:
                    # 合并数据
                    all_data = pd.concat([all_data, df], ignore_index=True)
                    
                    # 保存到CSV
                    all_data.to_csv(csv_filename, index=False)
                    
                    logger.info(f"数据更新成功，请求耗时: {request_time:.2f}秒，累计记录数: {len(all_data)}")
                    
                    # 检查新高与回踩策略
                    pullback_price = check_new_high_and_pullback(all_data)
                    if pullback_price is not None and strategy_state['pullback_price'] is not None:
                        logger.info(f"🔔 交易信号: 检测到回踩未跌破均线! 回踩价格: {pullback_price:.2f}")
                
                # 等待到下一个间隔
                sleep_time = max(1, REFRESH_INTERVAL - request_time)
                logger.debug(f"等待{sleep_time:.2f}秒后进行下一次请求")
                time.sleep(sleep_time)
            else:
                # 非交易时间，计算至下次交易还需等待的时间
                wait_seconds = get_next_trading_time()
                next_time = datetime.datetime.now() + datetime.timedelta(seconds=wait_seconds)
                
                logger.info(f"当前非交易时间，等待至下次交易开始: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 每日交易开始时重置策略状态
                if datetime.datetime.now().hour < 9:
                    strategy_state['high_at_time_point'] = None
                    strategy_state['new_high_detected'] = False
                    strategy_state['pullback_started'] = False
                    strategy_state['pullback_price'] = None
                    logger.info("新的交易日，重置策略状态")
                
                # 最多等待1小时，然后重新检查
                time.sleep(min(wait_seconds, 3600))
    
    except KeyboardInterrupt:
        logger.info("程序被用户终止")
    except Exception as e:
        logger.error(f"程序出现异常: {e}")
    finally:
        logger.info(f"程序退出，共收集{len(all_data)}条数据")
        logger.info(f"数据已保存至: {csv_filename}")

if __name__ == "__main__":
    main()
