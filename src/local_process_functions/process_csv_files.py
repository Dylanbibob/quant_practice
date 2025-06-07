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
        stock_code = str(filename.replace('.csv', '').replace('ffdc', ''))
        
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