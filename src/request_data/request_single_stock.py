import sys
import os
import pandas as pd
import akshare as ak
import requests
import time
import datetime as dt

def load_stock_data(ffdc, file_path, start_date, today, max_retries=3,verbose=True):
    """单个标的数据加载函数"""
    
    # 1. 检查本地文件的完整性
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # 验证数据完整性
            if len(data) > 0 and '日期' in data.columns:
                # 检查数据是否是今天的（可选）
                latest_date = pd.to_datetime(data['日期']).max()
                if latest_date.strftime('%Y%m%d') == today:
                    print(f"  📁 使用本地数据（{len(data)}天）")
                    return data, True
                else:
                    print(f"  ⚠️ 本地数据过期，重新获取")
            else:
                print(f"  ⚠️ 本地数据不完整，重新获取")
        except Exception as e:
            print(f"  ⚠️ 本地文件读取失败: {e}")
    
    # 2. 网络获取，带重试机制
    for attempt in range(max_retries):
        try:
            print(f"  🌐 网络获取数据（尝试 {attempt + 1}/{max_retries}）")
            data = ak.stock_zh_a_hist(symbol=str(ffdc), period="daily", 
                                    start_date=start_date, end_date=today, adjust="qfq")
            
            if data is not None and not data.empty:
                # 保存前验证数据
                if len(data) > 5:  # 至少有5天数据
                    data.to_csv(file_path, index=False, encoding='utf-8-sig')
                    print(f"  💾 保存数据到本地（{len(data)}天）")
                    return data, False
                else:
                    print(f"  ⚠️ 数据量过少（{len(data)}天），重试")
            else:
                print(f"  ⚠️ 获取到空数据，重试")
                
        except Exception as e:
            print(f"  ❌ 第{attempt + 1}次尝试失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
    
    return None, False

if __name__ == "__main__":
    
    today = dt.datetime.now().strftime("%Y%m%d")
    ffdc = "600900"
    file_path = f'test\single_stock_data_test\{ffdc}{today}.csv'
    start_date = "20240524"
    load_stock_data(ffdc, file_path, start_date, today, max_retries=3,verbose=False)