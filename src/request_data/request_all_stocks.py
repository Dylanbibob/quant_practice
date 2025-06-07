import akshare as ak
import pandas as pd

def request_all_stocks():
    #获取股票数据并进行清洗
    stock_data_pool = ak.stock_zh_a_spot_em() 
    stock_data_pool.dropna(inplace=True)
    stock_data_pool['总市值'] = (pd.to_numeric(stock_data_pool['总市值']) / 100000000).round(2)
    return stock_data_pool
    
if  __name__ == '__main__':
    request_all_stocks()
    stock_data_pool = request_all_stocks()
    print(stock_data_pool)