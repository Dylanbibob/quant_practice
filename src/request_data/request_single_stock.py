import sys
import os
import pandas as pd
import akshare as ak
import requests
import time
import datetime as dt
import re
from datetime import datetime, timedelta

def get_latest_trade_dates():
    """获取最近的交易日"""
    try:
        # 获取全部交易日历
        trade_date_df = ak.tool_trade_date_hist_sina()
        # 转换为datetime格式
        trade_date_df['trade_date'] = pd.to_datetime(trade_date_df['trade_date'])
        
        # 获取今天的日期
        today = dt.datetime.now().date()
        
        # 筛选出今天及之前的交易日
        past_trade_dates = trade_date_df[trade_date_df['trade_date'].dt.date <= today]
        
        if past_trade_dates.empty:
            return None, None
        
        # 找出最近的交易日（降序排序后取第一个）
        past_trade_dates = past_trade_dates.sort_values('trade_date', ascending=False)
        latest_trade_date = past_trade_dates.iloc[0]['trade_date']
        
        # 如果有两个或更多交易日，获取倒数第二个
        previous_trade_date = None
        if len(past_trade_dates) > 1:
            previous_trade_date = past_trade_dates.iloc[1]['trade_date']
            
        return latest_trade_date, previous_trade_date
    except Exception as e:
        print(f"获取交易日历失败: {e}")
        return None, None

def check_trade_date_validity(date_to_check):
    """检查给定日期是否为最新交易日或上一交易日"""
    latest_trade_date, previous_trade_date = get_latest_trade_dates()
    if latest_trade_date is None:
        return False, None, None
    
    date_to_check = pd.to_datetime(date_to_check).date()
    
    is_latest = date_to_check == latest_trade_date.date()
    is_previous = previous_trade_date is not None and date_to_check == previous_trade_date.date()
    
    return is_latest or is_previous, latest_trade_date, previous_trade_date

def load_stock_data(ffdc, file_path, start_date, today, max_retries=3, verbose=True):
    """单个标的数据加载函数"""
    
    # 1. 检查本地文件的完整性
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # 验证数据完整性
            if len(data) > 0 and '日期' in data.columns:
                # 从文件名中提取日期
                date_match = re.search(r'(\d{8})', file_path)
                
                if date_match:
                    file_date_str = date_match.group(1)
                    file_date = datetime.strptime(file_date_str, '%Y%m%d').date()
                    is_valid, latest_trade_date, previous_trade_date = check_trade_date_validity(file_date)
                    
                    if is_valid:
                        if verbose:
                            print(f"  📁 使用有效交易日数据（{len(data)}天）")
                            if file_date == latest_trade_date.date():
                                print(f"     文件日期与最新交易日匹配：{file_date}")
                            else:
                                print(f"     文件日期与上一交易日匹配：{file_date}")
                        return data, True
                    else:
                        if verbose:
                            print(f"  ⚠️ 本地数据不是最新交易日，重新获取")
                            print(f"     文件日期: {file_date}")
                            print(f"     最新交易日: {latest_trade_date.date()}")
                            if previous_trade_date:
                                print(f"     上一交易日: {previous_trade_date.date()}")
                else:
                    # 如果文件名中没有日期，检查数据内容中的最新日期
                    latest_date = pd.to_datetime(data['日期']).max().date()
                    is_valid, latest_trade_date, previous_trade_date = check_trade_date_validity(latest_date)
                    
                    if is_valid:
                        if verbose:
                            print(f"  📁 使用有效交易日数据（{len(data)}天）")
                            if latest_date == latest_trade_date.date():
                                print(f"     数据最新日期与最新交易日匹配：{latest_date}")
                            else:
                                print(f"     数据最新日期与上一交易日匹配：{latest_date}")
                        return data, True
                    else:
                        if verbose:
                            print(f"  ⚠️ 本地数据过期，重新获取")
                            print(f"     数据最新日期: {latest_date}")
                            print(f"     最新交易日: {latest_trade_date.date()}")
                            if previous_trade_date:
                                print(f"     上一交易日: {previous_trade_date.date()}")
            else:
                if verbose:
                    print(f"  ⚠️ 本地数据不完整，重新获取")
        except Exception as e:
            if verbose:
                print(f"  ⚠️ 本地文件读取失败: {e}")
    
    # 2. 网络获取，带重试机制
    for attempt in range(max_retries):
        try:
            if verbose:
                print(f"  🌐 网络获取数据（尝试 {attempt + 1}/{max_retries}）")
            data = ak.stock_zh_a_hist(symbol=str(ffdc), period="daily", 
                                    start_date=start_date, end_date=today, adjust="qfq")
            
            if data is not None and not data.empty:
                # 保存前验证数据
                if len(data) > 5:  # 至少有5天数据
                    # 确保保存的文件名包含当前最新交易日
                    latest_trade_date, _ = get_latest_trade_dates()
                    if latest_trade_date is not None:
                        latest_trade_date_str = latest_trade_date.strftime('%Y%m%d')
                        # 创建新的文件路径，包含最新交易日
                        dir_path = os.path.dirname(file_path)
                        file_name = os.path.basename(file_path)
                        # 替换文件名中的日期或添加日期
                        if re.search(r'\d{8}', file_name):
                            new_file_name = re.sub(r'\d{8}', latest_trade_date_str, file_name)
                        else:
                            new_file_name = f"{ffdc}_{latest_trade_date_str}.csv"
                        new_file_path = os.path.join(dir_path, new_file_name)
                        
                        data.to_csv(new_file_path, index=False, encoding='utf-8-sig')
                        if verbose:
                            print(f"  💾 保存数据到本地（{len(data)}天）- 使用最新交易日 {latest_trade_date_str}")
                    else:
                        data.to_csv(file_path, index=False, encoding='utf-8-sig')
                        if verbose:
                            print(f"  💾 保存数据到本地（{len(data)}天）")
                    return data, False
                else:
                    if verbose:
                        print(f"  ⚠️ 数据量过少（{len(data)}天），重试")
            else:
                if verbose:
                    print(f"  ⚠️ 获取到空数据，重试")
                
        except Exception as e:
            if verbose:
                print(f"  ❌ 第{attempt + 1}次尝试失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
    
    return None, False

if __name__ == "__main__":
    today = dt.datetime.now().strftime("%Y%m%d")
    ffdc = "600900"
    
    # 获取最新交易日
    latest_trade_date, _ = get_latest_trade_dates()
    if latest_trade_date is not None:
        latest_trade_date_str = latest_trade_date.strftime('%Y%m%d')
        print(f"最新交易日: {latest_trade_date.strftime('%Y-%m-%d')}")
        
        # 使用最新交易日作为文件名
        file_path = f'test/single_stock_data_test/{ffdc}_{latest_trade_date_str}.csv'
    else:
        file_path = f'test/single_stock_data_test/{ffdc}_{today}.csv'
        print(f"无法获取最新交易日，使用今日日期: {today}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 获取30天前的日期作为起始日期
    start_date = (dt.datetime.now() - dt.timedelta(days=30)).strftime("%Y%m%d")
    
    data, from_cache = load_stock_data(ffdc, file_path, start_date, today, max_retries=3, verbose=True)
    
    if data is not None:
        print(f"成功加载数据，共{len(data)}条记录，来源：{'缓存' if from_cache else '网络'}")
    else:
        print("加载数据失败")
        
    today = dt.datetime.now().strftime("%Y%m%d")
    result = get_latest_trade_dates()
    print(result)
    