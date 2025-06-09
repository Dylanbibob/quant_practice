import akshare as ak
import sys
import os
import pandas as pd
import numpy as np
import datetime as dt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import filter.slope_shadow_cal as sf
from filter.volume_analyzer import VolumeAnalyzer
import glob
pd.set_option('display.float_format', lambda x: '%.2f' % x)

def analyze_stock_technical(df, stock_code):
    """
    综合技术分析（包含量能分析）
    """
    
    if df is None or len(df) == 0:
        return {
            'code': stock_code,
            'valid_data': False,
            'reason': '无数据'
        }
    
    # 基本信息
    latest_data = df.iloc[-1]
    
    # 技术指标判断
    downtrend = sf.is_downtrend(df)
    high_shadow = sf.has_high_shadow(df)
    
    # 量能分析
    volume_analyzer = VolumeAnalyzer()
    volume_analysis = volume_analyzer.is_moderate_volume_increase(df)
    
    # 计算一些辅助指标
    ma5 = df['收盘'].rolling(5).mean().iloc[-1] if len(df) >= 5 else None
    ma20 = df['收盘'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
    
    # 最近5天的平均成交量
    avg_volume_5d = df['成交量'].tail(5).mean()
    
    # 综合筛选条件：技术面 + 量能面
    pass_technical = not downtrend and not high_shadow
    pass_volume = volume_analysis['is_moderate_volume']
    
    return {
        'code': stock_code,
        'valid_data': True,
        'latest_price': latest_data['收盘'],
        'latest_date': latest_data['日期'],
        'is_downtrend': downtrend,
        'has_high_shadow': high_shadow,
        'is_moderate_volume': pass_volume,
        'volume_ratio': volume_analysis['volume_ratio'],
        'volume_reason': volume_analysis['reason'],
        'pass_filter': pass_technical and pass_volume,  # 技术面和量能面都要通过
        'pass_technical': pass_technical,  # 仅技术面是否通过
        'pass_volume': pass_volume,  # 仅量能面是否通过
        'ma5': ma5,
        'ma20': ma20,
        'avg_volume_5d': avg_volume_5d,
        'current_volume': volume_analysis['current_volume'],
        'avg_volume': volume_analysis['avg_volume'],
        'data_days': len(df)
    }
    
if __name__ == '__main__':
    
    ffdc_stock_data = ak.stock_zh_a_hist(symbol='300210', 
                                        period = "daily", 
                                        start_date = '20250526',  
                                        end_date =  '20250526',
                                        adjust = 'qfq'
                                        )
    
    result = analyze_stock_technical(ffdc_stock_data,'300210')
    
    print(result)
    
       

