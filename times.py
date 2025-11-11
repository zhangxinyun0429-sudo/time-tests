# times.py
import datetime
import requests


def time_range(start_time, end_time, number_of_intervals=1, gap_between_intervals_s=0):
    """
    生成时间范围列表
    
    参数:
        start_time: 开始时间字符串 (格式: "YYYY-MM-DD HH:MM:SS")
        end_time: 结束时间字符串
        number_of_intervals: 区间数量
        gap_between_intervals_s: 区间之间的间隔（秒）
    
    返回:
        时间范围列表，每个元素是 (开始时间, 结束时间) 的元组
    
    抛出:
        ValueError: 当 end_time 早于或等于 start_time 时
    """
    start_time_s = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time_s = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    
    # 输入验证
    if end_time_s <= start_time_s:
        raise ValueError(
            f"End time ({end_time}) must be after start time ({start_time})"
        )
    
    # 计算每个区间的持续时间
    d = (end_time_s - start_time_s).total_seconds() / number_of_intervals + \
        gap_between_intervals_s * (1 / number_of_intervals - 1)
    
    # 生成时间区间
    sec_range = [
        (start_time_s + datetime.timedelta(seconds=i * d + i * gap_between_intervals_s),
         start_time_s + datetime.timedelta(seconds=(i + 1) * d + i * gap_between_intervals_s))
        for i in range(number_of_intervals)
    ]
    
    # 转换为字符串格式
    return [(ta.strftime("%Y-%m-%d %H:%M:%S"), tb.strftime("%Y-%m-%d %H:%M:%S")) 
            for ta, tb in sec_range]


def compute_overlap_time(range1, range2):
    """
    计算两个时间范围列表的重叠部分
    
    参数:
        range1: 第一个时间范围列表
        range2: 第二个时间范围列表
    
    返回:
        重叠的时间范围列表
    """
    overlap_time = []
    for start1, end1 in range1:
        for start2, end2 in range2:
            low = max(start1, start2)
            high = min(end1, end2)
            
            # 只添加有效的重叠（low < high）
            if low < high:
                overlap_time.append((low, high))
    
    return overlap_time


# ISS API 相关常量
ISS_API_URL = "https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/{lat}/{lon}/{alt}/{days}/{min_visibility}/&apiKey={api_key}"


def unix_to_datetime_str(timestamp):
    """
    将 Unix 时间戳转换为日期时间字符串
    
    参数:
        timestamp: Unix 时间戳（秒）
    
    返回:
        格式化的日期时间字符串 "YYYY-MM-DD HH:MM:SS"
    """
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


# times.py
def iss_passes(api_key, lat=56, lon=0, alt=0, days=5, min_visibility=50):
    """
    获取国际空间站的可见通过时间
    
    参数:
        api_key: n2yo API 密钥
        lat: 纬度（默认56）
        lon: 经度（默认0）
        alt: 海拔高度（默认0）
        days: 预测天数（默认5）
        min_visibility: 最小可见度（默认50）
    
    返回:
        通过时间列表 [(开始时间, 结束时间), ...]
    """
    url = ISS_API_URL.format(
        lat=lat, lon=lon, alt=alt, days=days, 
        min_visibility=min_visibility, api_key=api_key
    )
    
    try:
        # 发起 API 请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查 HTTP 错误
        
        data = response.json()
        
        passes_list = []
        
        # 检查响应中是否有 passes 数据
        if 'passes' in data:
            for pass_info in data['passes']:
                # 获取开始和结束的 Unix 时间戳
                start_time_unix = pass_info.get('startUTC')
                end_time_unix = pass_info.get('endUTC')
                
                if start_time_unix and end_time_unix:
                    # 转换时间戳为字符串格式
                    start_str = unix_to_datetime_str(start_time_unix)
                    end_str = unix_to_datetime_str(end_time_unix)
                    
                    passes_list.append((start_str, end_str))
        
        return passes_list
    
    except Exception as e:  # ✅ 改为捕获所有异常
        print(f"Error fetching ISS passes: {e}")
        return []

# 主程序示例（可选）
if __name__ == "__main__":
    large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
    short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
    print("时间重叠:", compute_overlap_time(large, short))
    
    # ISS API 示例（需要有效的 API 密钥）
    # passes = iss_passes("YOUR_API_KEY")
    # print("ISS 通过时间:", passes)