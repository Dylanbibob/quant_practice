import pandas as pd
import os

# from gm.api import *
# set_token('9f9a31a3ba21ce1492ca28eb5beaa2243848909d')
# data_jj = get_instruments(
#     exchanges = 'SZSE,SHSE',
#     sec_types = 1,
#     df = True
# )
# print(data_jj)

# data_jj_columns = pd.DataFrame(data_jj.columns)
# print(data_jj_columns)

file_path = r'data/stock_pool_data/stock_data_pool20250607.csv'
file_name = os.path.basename(file_path)
print(file_name)

data_ak = pd.read_csv(file_path)
print(data_ak.columns)

column_mapping = {
    'sec_id': '代码',
    'sec_name': '名称',
    'pre_close': '昨收',
    'upper_limit': '最高',
    'lower_limit': '最低',
    'open': '今开',  # 假设 df2 中有 'open' 列
    'close': '最新价',  # 假设 df2 中有 'close' 列
    'change': '涨跌额',  # 假设 df2 中有 'change' 列
    'pct_chg': '涨跌幅',  # 假设 df2 中有 'pct_chg' 列
    'volume': '成交量',  # 假设 df2 中有 'volume' 列
    'amount': '成交额',  # 假设 df2 中有 'amount' 列
    'amplitude': '振幅',  # 假设 df2 中有 'amplitude' 列
    'turnover_rate': '换手率',  # 假设 df2 中有 'turnover_rate' 列
    'pe': '市盈率-动态',  # 假设 df2 中有 'pe' 列
    'pb': '市净率',  # 假设 df2 中有 'pb' 列
    'total_mv': '总市值',  # 假设 df2 中有 'total_mv' 列
    'circ_mv': '流通市值',  # 假设 df2 中有 'circ_mv' 列
    # 其他列可以根据需要添加
}
