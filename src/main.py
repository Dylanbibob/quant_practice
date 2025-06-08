import logging
import akshare as ak
import pandas as pd
import numpy as np
import datetime as dt
import time
import os
from filter.analyze import analyze_stock_technical
from request_data.request_all_stocks import request_all_stocks
from request_data.request_single_stock import load_stock_data,get_latest_trade_dates
from local_process_functions.process_csv_files import process_csv_files
# from local_process.local_process import process_csv_files
import filter.slope_shadow_cal as sf
import sys
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# 在文件开头添加日志配置
def setup_logging():
    """设置日志配置"""
    # 确保logs目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成日志文件名
    log_filename = f"logs\\stock_analysis_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),  # 文件输出
            logging.StreamHandler(sys.stdout)  # 控制台输出
        ]
    )
    
    return log_filename

# 替换所有 print() 为 logging.info()
def main():
    log_file = setup_logging()
    logger = logging.getLogger()
    
    logger.info(f"📁 日志将保存到: {log_file}")


    today_market_filename = f'data\\stock_pool_data\\stock_data_pool{dt.datetime.now().strftime("%Y%m%d")}.csv'

    # 检查当天的股票池CSV文件数据是否存在
    if os.path.exists(today_market_filename):
        logger.info(f"📁 发现已存在的数据文件: {today_market_filename}")
        logger.info("🔄 直接加载本地CSV文件")
        stock_data_pool = pd.read_csv(today_market_filename,encoding='utf-8-sig',dtype={'代码': str})
    else:
        logger.info(f"❌ 未找到当天数据文件: {today_market_filename}")
        logger.info("🌐 正在从网络获取股票池数据...")
        # 获取股票池数据
        stock_data_pool = request_all_stocks()  # 注意这里应该是函数调用，不是to_csv
        # 保存为CSV文件
        stock_data_pool.to_csv(today_market_filename, index=False, encoding='utf-8-sig')
        logger.info(f"💾 数据已保存到: {today_market_filename}")
    
    
    # 第一次标的筛选 
    first_filtered_data = stock_data_pool[(stock_data_pool['涨跌幅'] > 3) &
                                        (stock_data_pool['涨跌幅'] < 5) & 
                                        (stock_data_pool['换手率'] > 4) & 
                                        (stock_data_pool['换手率'] < 10) & 
                                        (stock_data_pool['量比'] > 1) &
                                        (stock_data_pool['总市值'] > 50) & 
                                        (stock_data_pool['总市值'] < 100)]

    # file_path = f'e:\\desktop\\stock.csv'
    # data.to_csv(f'e:\\desktop\\stock.csv', index=False,encoding ='utf-8-sig')
    # logger.info(len(first_filtered_data))

    # 第二次标的筛选
    first_filtered_data_codes = first_filtered_data['代码'].tolist()
    today = dt.datetime.now().strftime('%Y%m%d')
    start_date = (dt.datetime.now() - dt.timedelta(days=60)).strftime('%Y%m%d')  # 增加到60天获取更多数据
    
    latest_trade_date, _ = get_latest_trade_dates()
    
    if latest_trade_date is not None:
        latest_trade_date_str = latest_trade_date.strftime('%Y%m%d')
        logger.info(f"最新交易日: {latest_trade_date.strftime('%Y-%m-%d')}")
    else:
        latest_trade_date_str = today
        logger.info(f"无法获取最新交易日，使用当前日期: {today}")

    logger.info(f"准备分析初次筛选出的{len(first_filtered_data_codes)} 只股票")
    logger.info(f"股票代码: {first_filtered_data_codes}")
    logger.info(f"数据日期范围: {start_date} 到 {today}")
    logger.info("="*60)

    # 存储分析结果
    analysis_results = []

    for i, ffdc in enumerate(first_filtered_data_codes):
        logger.info(f"\n({i+1}/{len(first_filtered_data_codes)}) 正在分析股票: {ffdc}")
        
        try:
            # 构建文件路径
            file_path = f'data\\single_stock_data\\{ffdc}_{latest_trade_date_str}.csv'
            
            # 使用函数获取股票数据（优先本地，否则网络获取）
            ffdc_stock_data, from_local = load_stock_data(ffdc, file_path, start_date, today)
            
            if ffdc_stock_data is not None and not ffdc_stock_data.empty:
                logger.info(f"  📊 数据量: {len(ffdc_stock_data)} 天")
                
                # 进行技术分析
                analysis = analyze_stock_technical(ffdc_stock_data, ffdc)
                analysis_results.append(analysis)
                
                # 显示分析结果
                logger.info(f"  📈 技术分析结果:")
                logger.info(f"    最新价格: {analysis['latest_price']:.2f}")
                logger.info(f"    最新日期: {analysis['latest_date']}")
                logger.info(f"    下跌趋势: {'是' if analysis['is_downtrend'] else '否'}")
                logger.info(f"    高位上影线: {'有' if analysis['has_high_shadow'] else '无'}")
                logger.info(f"    MA5: {analysis['ma5']:.2f}" if analysis['ma5'] else "    MA5: 数据不足")
                logger.info(f"    MA20: {analysis['ma20']:.2f}" if analysis['ma20'] else "    MA20: 数据不足")
                
                if analysis['pass_filter']:
                    logger.info(f"  ✅ {ffdc} 通过技术分析筛选!")
                else:
                    reasons = []
                    if analysis['is_downtrend']:
                        reasons.append("下跌趋势")
                    if analysis['has_high_shadow']:
                        reasons.append("高位上影线")
                    logger.info(f"  ❌ {ffdc} 未通过筛选，原因: {', '.join(reasons)}")
            else:
                logger.info(f"  ❌ 未获取到有效数据")
                analysis_results.append({
                    'code': ffdc,
                    'valid_data': False,
                    'reason': '未获取到有效数据'
                })
                
        except Exception as e:
            logger.info(f"  ❌ 分析过程出错: {e}")
            analysis_results.append({
                'code': ffdc,
                'valid_data': False,
                'reason': f'错误: {e}'
            })
        
        # 只有从网络获取数据时才需要等待
        if not from_local:
            time.sleep(1)

    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("技术分析汇总结果:")
    logger.info("="*60)

    passed_stocks = []
    for result in analysis_results:
        if result.get('valid_data', False):
            if result.get('pass_filter', True):
                passed_stocks.append(result)
                logger.info(f"✅ {result['code']} - 通过筛选")
            else:
                reasons = []
                if result.get('is_downtrend'):
                    reasons.append("下跌趋势")
                if result.get('has_high_shadow'):
                    reasons.append("高位上影线")
                logger.info(f"❌ {result['code']} - 未通过: {', '.join(reasons)}")
        else:
            logger.info(f"⚠️  {result['code']} - {result.get('reason', '未知错误')}")

    logger.info(f"\n最终结果: {len(passed_stocks)} 只股票通过技术分析筛选")

    if passed_stocks:
        logger.info("\n符合条件的股票详情:")
        for stock in passed_stocks:
            logger.info(f"代码: {stock['code']}")
            logger.info(f"  最新价格: {stock['latest_price']:.2f}")
            logger.info(f"  MA5: {stock['ma5']:.2f}" if stock['ma5'] else "  MA5: 数据不足")
            logger.info(f"  MA20: {stock['ma20']:.2f}" if stock['ma20'] else "  MA20: 数据不足")
            logger.info(f"  数据天数: {stock['data_days']}")


# if __name__ == "__main__":
#     # 检查是否有命令行参数
#     if len(sys.argv) > 1 and sys.argv[1] == 'csv':
#         print("🔄 处理CSV文件模式")
#         process_csv_files()
#     else:
#         print("🔄 在线获取数据模式")
#         main()  # 调用主程序
if __name__ == "__main__":
    main()  # 调用主程序