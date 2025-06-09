import pandas as pd
import numpy as np
import logging

class VolumeAnalyzer:
    """温和放量分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger()
    
    def calculate_volume_ratio(self, volumes, period=5):
        """
        计算成交量相对于移动平均的比率
        """
        if len(volumes) < period:
            return None
            
        # 计算移动平均成交量
        ma_volume = np.mean(volumes[-period:])
        current_volume = volumes[-1]
        
        if ma_volume == 0:
            return None
            
        ratio = current_volume / ma_volume
        return ratio
    
    def is_moderate_volume_increase(self, stock_data, window=5, threshold_low=1.2, threshold_high=1.8):
        """
        判断是否为温和放量
        
        参数:
        - stock_data: 包含成交量数据的DataFrame
        - window: 移动平均窗口期
        - threshold_low: 温和放量下限倍数
        - threshold_high: 温和放量上限倍数
        
        返回:
        - dict: 包含分析结果的字典
        """
        try:
            if stock_data is None or stock_data.empty:
                return {
                    'is_moderate_volume': False,
                    'volume_ratio': None,
                    'current_volume': None,
                    'avg_volume': None,
                    'reason': '数据为空'
                }
            
            # 确保有足够的数据
            if len(stock_data) < window + 1:
                return {
                    'is_moderate_volume': False,
                    'volume_ratio': None,
                    'current_volume': None,
                    'avg_volume': None,
                    'reason': f'数据不足，需要至少{window + 1}天数据'
                }
            
            # 获取成交量列（可能的列名）
            volume_col = None
            possible_volume_cols = ['成交量', 'volume', '成交量(手)', 'Volume']
            
            for col in possible_volume_cols:
                if col in stock_data.columns:
                    volume_col = col
                    break
            
            if volume_col is None:
                return {
                    'is_moderate_volume': False,
                    'volume_ratio': None,
                    'current_volume': None,
                    'avg_volume': None,
                    'reason': '未找到成交量数据列'
                }
            
            # 获取最近的成交量数据
            volumes = stock_data[volume_col].fillna(0).values
            
            # 计算当前成交量
            current_volume = volumes[-1]
            
            # 计算前期平均成交量（排除当前日）
            if len(volumes) >= window + 1:
                avg_volume = np.mean(volumes[-(window+1):-1])
            else:
                avg_volume = np.mean(volumes[:-1])
            
            if avg_volume == 0:
                return {
                    'is_moderate_volume': False,
                    'volume_ratio': None,
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'reason': '历史平均成交量为0'
                }
            
            # 计算量比
            volume_ratio = current_volume / avg_volume
            
            # 判断是否为温和放量
            is_moderate = threshold_low <= volume_ratio <= threshold_high
            
            # 附加检查：确保不是异常的巨量
            recent_max_volume = np.max(volumes[-10:]) if len(volumes) >= 10 else np.max(volumes)
            is_not_extreme = current_volume <= recent_max_volume * 1.5
            
            result = {
                'is_moderate_volume': is_moderate and is_not_extreme,
                'volume_ratio': round(volume_ratio, 2),
                'current_volume': current_volume,
                'avg_volume': round(avg_volume, 2),
                'reason': self._get_volume_reason(volume_ratio, threshold_low, threshold_high, is_not_extreme)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"温和放量分析出错: {e}")
            return {
                'is_moderate_volume': False,
                'volume_ratio': None,
                'current_volume': None,
                'avg_volume': None,
                'reason': f'分析出错: {str(e)}'
            }
    
    def _get_volume_reason(self, volume_ratio, threshold_low, threshold_high, is_not_extreme):
        """获取成交量判断原因"""
        if volume_ratio is None:
            return "无法计算量比"
        elif volume_ratio < threshold_low:
            return f"成交量不足，量比{volume_ratio:.2f}小于{threshold_low}"
        elif volume_ratio > threshold_high:
            return f"成交量过大，量比{volume_ratio:.2f}超过{threshold_high}"
        elif not is_not_extreme:
            return "成交量异常放大"
        else:
            return f"温和放量，量比{volume_ratio:.2f}"

def analyze_moderate_volume(stock_data, code):
    """
    便捷函数：分析单只股票的温和放量情况
    """
    analyzer = VolumeAnalyzer()
    result = analyzer.is_moderate_volume_increase(stock_data)
    result['code'] = code
    return result