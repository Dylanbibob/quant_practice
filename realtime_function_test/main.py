# 创建数据收集器
collector = RealTimeDataCollector('600900.SH')

# 方式1: 前台运行（阻塞主线程）
collector.collect_data_continuously(interval=30, max_iterations=10)

# 方式2: 后台运行（不阻塞主线程）
collector.start_collecting(interval=30)
# ... 做其他事情 ...
collector.stop_collecting()

# 查看合并后的数据
collector.print_summary()

# 保存数据到CSV
collector.save_to_csv()