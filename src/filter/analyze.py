import akshare as ak
import pandas as pd
import numpy as np
import datetime as dt
import os
import filter.second_filter as sf
import glob
pd.set_option('display.float_format', lambda x: '%.2f' % x)

def analyze_stock_technical(df, stock_code):
    """
    综合技术分析
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
    
    # 计算一些辅助指标
    ma5 = df['收盘'].rolling(5).mean().iloc[-1] if len(df) >= 5 else None
    ma20 = df['收盘'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
    
    # 最近5天的平均成交量
    avg_volume_5d = df['成交量'].tail(5).mean()
    
    return {
        'code': stock_code,
        'valid_data': True,
        'latest_price': latest_data['收盘'],
        'latest_date': latest_data['日期'],
        'is_downtrend': downtrend,
        'has_high_shadow': high_shadow,
        'pass_filter': not downtrend and not high_shadow,  # 通过筛选的条件
        'ma5': ma5,
        'ma20': ma20,
        'avg_volume_5d': avg_volume_5d,
        'data_days': len(df)
    }
    
def load_csv_files_from_data(data_dir='../../data'):
    """
    从data目录加载所有CSV文件并转换为DataFrame列表
    
    Args:
        data_dir: data目录的相对路径
        
    Returns:
        list: 包含(文件名, DataFrame)元组的列表
    """
    # 获取当前文件的绝对路径，然后构建data目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, data_dir)
    
    # 查找所有CSV文件
    csv_files = glob.glob(os.path.join(data_path, "*.csv"))
    
    dataframes = []
    for csv_file in csv_files:
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            filename = os.path.basename(csv_file)
            dataframes.append((filename, df))
            print(f"✅ 成功加载: {filename}, 数据量: {len(df)}")
        except Exception as e:
            print(f"❌ 加载失败: {csv_file}, 错误: {e}")
    
    return dataframes

if __name__ == '__main__':
    
    ffdc_stock_data = ak.stock_zh_a_hist(symbol='600900', 
                                    period = "daily", 
                                    start_date = '20240524',  
                                    end_date =  '20250524', )
    result = analyze_stock_technical(ffdc_stock_data,'600900')
    
    print(result)   

