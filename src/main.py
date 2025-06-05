import akshare as ak
import pandas as pd
import numpy as np
import datetime as dt
import time
import os
from filter.analyze import analyze_stock_technical,load_csv_files_from_data
# from local_process.local_process import process_csv_files
import filter.second_filter as sf
import sys
pd.set_option('display.float_format', lambda x: '%.2f' % x)


# #获取股票数据并进行清洗
# stock_data_pool = ak.stock_zh_a_spot_em() 
# stock_data_pool.dropna(inplace=True)
# stock_data_pool['总市值'] = (pd.to_numeric(stock_data_pool['总市值']) / 100000000).round(2)
# print(stock_data_pool)

# #保存为CSV测试用
# stock_data_pool.to_csv(f'data\\stock_data_pool{dt.datetime.now().strftime("%Y%m%d")}.csv', index=False,coding='utf-8-sig')
# stock_data_pool = pd.read_csv(f'data\\stock_data_pool{dt.datetime.now().strftime("%Y%m%d")}.csv')

# #筛选出涨幅在3%~5%之间的股票 
# first_filtered_data = stock_data_pool[(stock_data_pool['涨跌幅'] > 3) & (stock_data_pool['涨跌幅'] < 5)]
# #筛选出换手率在4%~10%之间的股票
# first_filtered_data = first_filtered_data[(first_filtered_data['换手率'] > 4) & (first_filtered_data['换手率'] < 10)]
# #删除量比小于1的股票
# first_filtered_data = first_filtered_data[first_filtered_data['量比'] > 1]
# # 选出市值在50亿到100亿之间的股票
# first_filtered_data = first_filtered_data[(first_filtered_data['总市值'] > 50) & (first_filtered_data['总市值'] < 100)]

# # file_path = f'e:\\desktop\\stock.csv'
# # data.to_csv(f'e:\\desktop\\stock.csv', index=False,encoding ='utf-8-sig')
# # print(len(first_filtered_data))

# # 主程序
# first_filtered_data_codes = first_filtered_data['代码'].tolist()
# today = dt.datetime.now().strftime('%Y%m%d')
# start_date = (dt.datetime.now() - dt.timedelta(days=60)).strftime('%Y%m%d')  # 增加到60天获取更多数据

# print(f"准备分析初次筛选出的{len(first_filtered_data_codes)} 只股票")
# print(f"股票代码: {first_filtered_data_codes}")
# print(f"数据日期范围: {start_date} 到 {today}")
# print("="*60)

# # 存储分析结果
# analysis_results = []

# for i, ffdc in enumerate(first_filtered_data_codes):
#     print(f"\n({i+1}/{len(first_filtered_data_codes)}) 正在分析股票: {ffdc}")
    
#     try:
#         # 获取股票数据
#         ffdc_stock_data = ak.stock_zh_a_hist(symbol=ffdc, 
#                                              period="daily", 
#                                              start_date=start_date,  
#                                              end_date=today, 
#                                              adjust="qfq")
        
#         if ffdc_stock_data is not None and not ffdc_stock_data.empty:
#             print(f"  📊 获取到 {len(ffdc_stock_data)} 天的数据")
            
#             # 保存原始数据到相对路径下的data文件夹
            
#             file_path = f'data\\ffdc{ffdc}.csv'
#             ffdc_stock_data.to_csv(file_path, index=False, encoding='utf-8-sig')
#             print(f"  💾 已保存原始数据到: {file_path}")
            
#             # 进行技术分析
#             analysis = analyze_stock_technical(ffdc_stock_data, ffdc)
#             analysis_results.append(analysis)
            
#             # 显示分析结果
#             print(f"  📈 技术分析结果:")
#             print(f"    最新价格: {analysis['latest_price']:.2f}")
#             print(f"    最新日期: {analysis['latest_date']}")
#             print(f"    下跌趋势: {'是' if analysis['is_downtrend'] else '否'}")
#             print(f"    高位上影线: {'是' if analysis['has_high_shadow'] else '否'}")
#             print(f"    MA5: {analysis['ma5']:.2f}" if analysis['ma5'] else "    MA5: 数据不足")
#             print(f"    MA20: {analysis['ma20']:.2f}" if analysis['ma20'] else "    MA20: 数据不足")
            
#             if analysis['pass_filter']:
#                 print(f"  ✅ {ffdc} 通过技术分析筛选!")
#             else:
#                 reasons = []
#                 if analysis['is_downtrend']:
#                     reasons.append("下跌趋势")
#                 if analysis['has_high_shadow']:
#                     reasons.append("高位上影线")
#                 print(f"  ❌ {ffdc} 未通过筛选，原因: {', '.join(reasons)}")
#         else:
#             print(f"  ❌ 未获取到数据")
#             analysis_results.append({
#                 'code': ffdc,
#                 'valid_data': False,
#                 'reason': '未获取到数据'
#             })
            
#     except Exception as e:
#         print(f"  ❌ 分析过程出错: {e}")
#         analysis_results.append({
#             'code': ffdc,
#             'valid_data': False,
#             'reason': f'错误: {e}'
#         })
    
#     # 避免请求过快
#     time.sleep(1)

# # 汇总结果
# print("\n" + "="*60)
# print("技术分析汇总结果:")
# print("="*60)

# passed_stocks = []
# for result in analysis_results:
#     if result.get('valid_data', False):
#         if result.get('pass_filter', False):
#             passed_stocks.append(result)
#             print(f"✅ {result['code']} - 通过筛选")
#         else:
#             reasons = []
#             if result.get('is_downtrend'):
#                 reasons.append("下跌趋势")
#             if result.get('has_high_shadow'):
#                 reasons.append("高位上影线")
#             print(f"❌ {result['code']} - 未通过: {', '.join(reasons)}")
#     else:
#         print(f"⚠️  {result['code']} - {result.get('reason', '未知错误')}")

# print(f"\n最终结果: {len(passed_stocks)} 只股票通过技术分析筛选")

# if passed_stocks:
#     print("\n符合条件的股票详情:")
#     for stock in passed_stocks:
#         print(f"代码: {stock['code']}")
#         print(f"  最新价格: {stock['latest_price']:.2f}")
#         print(f"  MA5: {stock['ma5']:.2f}" if stock['ma5'] else "  MA5: 数据不足")
#         print(f"  MA20: {stock['ma20']:.2f}" if stock['ma20'] else "  MA20: 数据不足")
#         print(f"  数据天数: {stock['data_days']}")

#主程序（本地CSV处理）
def process_csv_files():
    """
    处理data目录下的所有CSV文件，走原来的分析流程
    """
    from filter.analyze import load_csv_files_from_data, analyze_stock_technical
    
    # 加载所有CSV文件
    csv_dataframes = load_csv_files_from_data()
    
    if not csv_dataframes:
        print("❌ 未找到任何CSV文件")
        return
    
    print(f"📁 找到 {len(csv_dataframes)} 个CSV文件")
    print("="*60)
    
    # 存储分析结果
    analysis_results = []
    
    for i, (filename, df) in enumerate(csv_dataframes):
        print(f"\n({i+1}/{len(csv_dataframes)}) 正在分析文件: {filename}")
        
        # 从文件名提取股票代码（假设文件名包含股票代码）
        stock_code = filename.replace('.csv', '').replace('ffdc', '')
        
        try:
            if df is not None and not df.empty:
                print(f"  📊 数据量: {len(df)} 条记录")
                
                # 显示数据基本信息
                if '日期' in df.columns:
                    print(f"  📅 数据日期范围: {df['日期'].min()} 到 {df['日期'].max()}")
                
                # 进行技术分析
                analysis = analyze_stock_technical(df, stock_code)
                analysis_results.append(analysis)
                
                # 显示分析结果
                print(f"  📈 技术分析结果:")
                if analysis.get('valid_data', False):
                    print(f"    最新价格: {analysis['latest_price']:.2f}")
                    print(f"    最新日期: {analysis['latest_date']}")
                    print(f"    下跌趋势: {'是' if analysis['is_downtrend'] else '否'}")
                    print(f"    高位上影线: {'是' if analysis['has_high_shadow'] else '否'}")
                    print(f"    MA5: {analysis['ma5']:.2f}" if analysis['ma5'] else "    MA5: 数据不足")
                    print(f"    MA20: {analysis['ma20']:.2f}" if analysis['ma20'] else "    MA20: 数据不足")
                    
                    if analysis['pass_filter']:
                        print(f"  ✅ {stock_code} 通过技术分析筛选!")
                    else:
                        reasons = []
                        if analysis['is_downtrend']:
                            reasons.append("下跌趋势")
                        if analysis['has_high_shadow']:
                            reasons.append("高位上影线")
                        print(f"  ❌ {stock_code} 未通过筛选，原因: {', '.join(reasons)}")
                else:
                    print(f"  ❌ 数据无效: {analysis.get('reason', '未知原因')}")
            else:
                print(f"  ❌ 文件为空或无效")
                
        except Exception as e:
            print(f"  ❌ 分析过程出错: {e}")
            analysis_results.append({
                'code': stock_code,
                'valid_data': False,
                'reason': f'错误: {e}'
            })
    
    # 汇总结果
    print("\n" + "="*60)
    print("CSV文件技术分析汇总结果:")
    print("="*60)
    
    passed_stocks = []
    for result in analysis_results:
        if result.get('valid_data', False):
            if result.get('pass_filter', False):
                passed_stocks.append(result)
                print(f"✅ {result['code']} - 通过筛选")
            else:
                reasons = []
                if result.get('is_downtrend'):
                    reasons.append("下跌趋势")
                if result.get('has_high_shadow'):
                    reasons.append("高位上影线")
                print(f"❌ {result['code']} - 未通过: {', '.join(reasons)}")
        else:
            print(f"⚠️  {result['code']} - {result.get('reason', '未知错误')}")
    
    print(f"\n最终结果: {len(passed_stocks)} 只股票通过技术分析筛选")
    
    if passed_stocks:
        print("\n符合条件的股票详情:")
        for stock in passed_stocks:
            print(f"代码: {stock['code']}")
            print(f"  最新价格: {stock['latest_price']:.2f}")
            print(f"  MA5: {stock['ma5']:.2f}" if stock['ma5'] else "  MA5: 数据不足")
            print(f"  MA20: {stock['ma20']:.2f}" if stock['ma20'] else "  MA20: 数据不足")
            print(f"  数据天数: {stock['data_days']}")
    
    return analysis_results
        
if __name__ == "__main__":
    import sys
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == 'csv':
        print("🔄 处理CSV文件模式")
        process_csv_files()
    else:
        print("🔄 在线获取数据模式")
        # 原来的代码逻辑
        # ... 你原来main.py中的代码 ...