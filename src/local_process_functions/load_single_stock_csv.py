import akshare as ak
import pandas as pd
import numpy as np
import datetime as dt
import os
import glob
pd.set_option('display.float_format', lambda x: '%.2f' % x)

def load_single_stock_csv(data_dir='../../data/single_stock_data'):
    """
    从single_stock_data目录加载所有CSV文件并转换为DataFrame列表
    
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
    
    single_stock_dataframes = []
    for csv_file in csv_files:
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            filename = os.path.basename(csv_file)
            single_stock_dataframes.append((filename, df))
            print(f"✅ 成功加载: {filename}, 数据量: {len(df)}")
        except Exception as e:
            print(f"❌ 加载失败: {csv_file}, 错误: {e}")
    
    return single_stock_dataframes

if __name__ == '__main__':
    
    pool_dataframes = load_single_stock_csv()
    print(pool_dataframes)