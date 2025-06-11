import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import time
import threading
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

# 设置tushare token
ts.set_token('00e414e1e675fe57036110eb1f115cb501a6a418a5278b261b86f948')

class RealTimeStockMonitor:
    def __init__(self, ts_code='600900.SH', interval=46):
        """
        实时股票监控类
        
        Args:
            ts_code: 股票代码
            interval: 获取数据间隔时间(秒)
        """
        self.ts_code = ts_code
        self.interval = interval
        self.data_df = pd.DataFrame()
        self.is_running = False
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图形
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle(f'实时股票数据监控 - {ts_code}', fontsize=16)
        
    def fetch_data(self):
        """获取实时数据"""
        try:
            df = ts.realtime_quote(ts_code=self.ts_code)
            if not df.empty:
                # 添加获取时间戳
                df['fetch_time'] = datetime.now()
                return df
        except Exception as e:
            print(f"获取数据出错: {e}")
        return None
    
    def calculate_change_percent(self, current_price, pre_close):
        """计算涨跌幅"""
        try:
            current = float(current_price)
            pre = float(pre_close)
            if pre != 0:
                return ((current - pre) / pre) * 100
        except:
            pass
        return 0
    
    def update_dataframe(self, new_data):
        """更新合并数据框"""
        if new_data is not None:
            if self.data_df.empty:
                self.data_df = new_data.copy()
            else:
                self.data_df = pd.concat([self.data_df, new_data], ignore_index=True)
    
    def plot_data(self):
        """绘制数据图表"""
        if self.data_df.empty:
            return
        
        # 清空之前的图表
        self.ax1.clear()
        self.ax2.clear()
        
        # 转换数据类型
        times = self.data_df['fetch_time']
        prices = pd.to_numeric(self.data_df['PRICE'], errors='coerce')
        volumes = pd.to_numeric(self.data_df['VOLUME'], errors='coerce') / 10000  # 转换为万手
        
        # 绘制价格走势图
        self.ax1.plot(times, prices, 'b-', linewidth=2, marker='o', markersize=4)
        self.ax1.set_title('实时价格走势', fontsize=12)
        self.ax1.set_ylabel('价格 (元)', fontsize=10)
        self.ax1.grid(True, alpha=0.3)
        
        # 格式化x轴时间显示
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax1.tick_params(axis='x', rotation=45)
        
        # 绘制成交量图
        self.ax2.bar(times, volumes, width=0.0008, color='red', alpha=0.7)
        self.ax2.set_title('实时成交量', fontsize=12)
        self.ax2.set_ylabel('成交量 (万手)', fontsize=10)
        self.ax2.set_xlabel('时间', fontsize=10)
        self.ax2.grid(True, alpha=0.3)
        
        # 格式化x轴时间显示
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax2.tick_params(axis='x', rotation=45)
        
        # 显示最新数据信息
        if not self.data_df.empty:
            latest = self.data_df.iloc[-1]
            # 计算涨跌幅
            pct_change = self.calculate_change_percent(latest['PRICE'], latest['PRE_CLOSE'])
            
            info_text = (f"最新价格: {latest['PRICE']} | "
                        f"昨收: {latest['PRE_CLOSE']} | "
                        f"涨跌幅: {pct_change:.2f}% | "
                        f"成交量: {float(latest['VOLUME'])/10000:.2f}万手 | "
                        f"最高: {latest['HIGH']} | 最低: {latest['LOW']}")
            
            self.fig.suptitle(f'实时股票数据监控 - {self.ts_code}\n{info_text}', fontsize=12)
        
        # 调整布局
        plt.tight_layout()
        plt.draw()
        
    def data_collection_loop(self):
        """数据采集循环"""
        while self.is_running:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在获取数据...")
            
            # 获取新数据
            new_data = self.fetch_data()
            
            if new_data is not None:
                # 更新数据框
                self.update_dataframe(new_data)
                print(f"数据更新成功，当前共有 {len(self.data_df)} 条记录")
                
                # 显示最新数据详情
                latest = new_data.iloc[-1]
                pct_change = self.calculate_change_percent(latest['PRICE'], latest['PRE_CLOSE'])
                print(f"股票: {latest['NAME']} | 价格: {latest['PRICE']} | "
                      f"涨跌幅: {pct_change:.2f}% | 成交量: {float(latest['VOLUME'])/10000:.2f}万手")
                
                # 更新图表
                self.plot_data()
            else:
                print("数据获取失败")
            
            # 等待指定时间
            time.sleep(self.interval)
    
    def start_monitoring(self):
        """开始监控"""
        print(f"开始监控股票 {self.ts_code}，每 {self.interval} 秒更新一次...")
        self.is_running = True
        
        # 在单独线程中运行数据采集
        self.data_thread = threading.Thread(target=self.data_collection_loop)
        self.data_thread.daemon = True
        self.data_thread.start()
        
        # 显示图表
        plt.show()
    
    def stop_monitoring(self):
        """停止监控"""
        print("停止监控...")
        self.is_running = False
        
    def get_current_data(self):
        """获取当前累积的数据"""
        return self.data_df.copy()
    
    def save_data(self, filename=None):
        """保存数据到文件"""
        if filename is None:
            filename = f"{self.ts_code}_realtime_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.data_df.empty:
            self.data_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"数据已保存到: {filename}")
        else:
            print("没有数据可保存")
    
    def print_data_summary(self):
        """打印数据摘要"""
        if not self.data_df.empty:
            print("\n=== 数据摘要 ===")
            latest = self.data_df.iloc[-1]
            print(f"股票名称: {latest['NAME']}")
            print(f"股票代码: {latest['TS_CODE']}")
            print(f"当前价格: {latest['PRICE']}")
            print(f"昨日收盘: {latest['PRE_CLOSE']}")
            print(f"今日开盘: {latest['OPEN']}")
            print(f"最高价: {latest['HIGH']}")
            print(f"最低价: {latest['LOW']}")
            print(f"买一价: {latest['BID']}")
            print(f"卖一价: {latest['ASK']}")
            print(f"成交量: {latest['VOLUME']}")
            print(f"成交额: {latest['AMOUNT']}")
            
            pct_change = self.calculate_change_percent(latest['PRICE'], latest['PRE_CLOSE'])
            print(f"涨跌幅: {pct_change:.2f}%")
            print(f"数据获取时间: {latest['DATE']} {latest['TIME']}")
            print("================")

# 使用示例函数
def start_real_time_monitoring(ts_code='600900.SH', interval=46):
    """
    启动实时股票监控
    
    Args:
        ts_code: 股票代码
        interval: 数据获取间隔(秒)
    """
    monitor = RealTimeStockMonitor(ts_code=ts_code, interval=interval)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n接收到停止信号...")
        monitor.stop_monitoring()
        
        # 显示数据摘要
        monitor.print_data_summary()
        
        # 询问是否保存数据
        save_choice = input("是否保存采集的数据？(y/n): ")
        if save_choice.lower() == 'y':
            monitor.save_data()
        
        print("程序已退出")
        return monitor.get_current_data()

# 简化版本的函数
def simple_real_time_monitor(ts_code='600900.SH', interval=46, max_records=50):
    """
    简化版实时监控函数
    
    Args:
        ts_code: 股票代码
        interval: 获取间隔(秒)
        max_records: 最大记录数，达到后停止
    """
    print(f"开始监控 {ts_code}，每 {interval} 秒获取一次数据...")
    
    all_data = pd.DataFrame()
    
    for i in range(max_records):
        try:
            # 获取数据
            df = ts.realtime_quote(ts_code=ts_code)
            df['fetch_time'] = datetime.now()
            
            # 合并数据
            if all_data.empty:
                all_data = df.copy()
            else:
                all_data = pd.concat([all_data, df], ignore_index=True)
            
            # 计算涨跌幅
            latest = df.iloc[0]
            pct_change = 0
            try:
                current = float(latest['PRICE'])
                pre = float(latest['PRE_CLOSE'])
                if pre != 0:
                    pct_change = ((current - pre) / pre) * 100
            except:
                pass
            
            print(f"[{i+1}/{max_records}] {datetime.now().strftime('%H:%M:%S')} - "
                  f"股票: {latest['NAME']} | 价格: {latest['PRICE']} | "
                  f"涨跌幅: {pct_change:.2f}% | 成交量: {float(latest['VOLUME'])/10000:.2f}万手")
            
            # 等待
            if i < max_records - 1:  # 最后一次不需要等待
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n手动停止监控")
            break
        except Exception as e:
            print(f"获取数据出错: {e}")
            continue
    
    return all_data

def test_data_structure():
    """测试数据结构"""
    print("测试获取数据结构...")
    try:
        df = ts.realtime_quote(ts_code='600900.SH')
        print("成功获取数据!")
        print("列名:", df.columns.tolist())
        print("数据预览:")
        print(df.head())
        print("\n数据类型:")
        print(df.dtypes)
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    # 首先测试数据结构
    print("=" * 50)
    print("1. 测试数据结构")
    test_data_structure()
    
    print("\n" + "=" * 50)
    print("2. 启动实时股票监控...")
    print("按 Ctrl+C 停止监控")
    
    # 启动监控
    final_data = start_real_time_monitoring('600900.SH', 46)
    
    # 方式2: 使用简化版本
    # print("\n" + "=" * 50)
    # print("3. 使用简化版本监控")
    # data = simple_real_time_monitor('600900.SH', 46, 10)
    # print(f"\n采集完成，共获取 {len(data)} 条数据")
    # print(data.head())
