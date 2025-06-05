import akshare as ak
import pandas as pd
import numpy as np
import datetime as dt
pd.set_option('display.float_format', lambda x: '%.2f' % x)

def is_downtrend(df, period=20):
    """
    判断是否处于下跌趋势
    使用移动平均线判断：短期均线在长期均线下方且均线向下
    """
    if len(df) < period:
        return True  # 数据不足，保守起见认为是下跌趋势
    
    # 计算5日和20日移动平均线
    ma5 = df['收盘'].rolling(window=5).mean()
    ma20 = df['收盘'].rolling(window=20).mean()
    
    # 最新的均线值
    latest_ma5 = ma5.iloc[-1]
    latest_ma20 = ma20.iloc[-1]
    
    # 判断均线趋势（最近5天的斜率）
    if len(ma5) >= 5:
        ma5_slope = (ma5.iloc[-1] - ma5.iloc[-5]) / 5
        ma20_slope = (ma20.iloc[-1] - ma20.iloc[-5]) / 5
    else:
        ma5_slope = 0
        ma20_slope = 0
    
    # 下跌趋势条件：短期均线在长期均线下方，且均线向下
    is_down = (latest_ma5 < latest_ma20) and (ma5_slope < 0 or ma20_slope < 0)
    
    return is_down

def has_high_shadow(df, days=5, shadow_ratio=0.03):
    """
    判断最近几天是否出现高位上影线
    """
    if len(df) < days:
        return True  # 数据不足，保守起见认为有上影线
    
    recent_data = df.tail(days)
    
    for _, row in recent_data.iterrows():
        high = row['最高']
        low = row['最低']
        open_price = row['开盘']
        close = row['收盘']
        
        # K线总长度
        total_range = high - low
        if total_range == 0:
            continue
            
        # 上影线长度
        upper_shadow = high - max(open_price, close)
        
        # 上影线比例
        if total_range > 0:
            shadow_ratio_actual = upper_shadow / total_range
            
            # 判断是否是高位上影线：上影线比例大于阈值，且收盘价在相对高位
            if shadow_ratio_actual > shadow_ratio and close > (high + low) / 2:
                return True
    
    return False
    

if __name__ == '__main__':
    
    ffdc_stock_data = ak.stock_zh_a_hist(symbol='600900', 
                                        period = "daily", 
                                        start_date = '20240524',  
                                        end_date =  '20250524', )
    downtrend = is_downtrend(ffdc_stock_data)
    high_shadow = has_high_shadow(ffdc_stock_data)
    
    print(downtrend)
    print(high_shadow)
    