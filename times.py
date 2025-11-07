import datetime
import requests

def time_range(start_time, end_time, number_of_intervals=1, gap_between_intervals_s=0):
    start_time_s = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time_s = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    
    
    if end_time_s <= start_time_s:
        raise ValueError(f"End time ({end_time}) must be after start time ({start_time})")
    
    d = (end_time_s - start_time_s).total_seconds() / number_of_intervals + gap_between_intervals_s * (1 / number_of_intervals - 1)
    sec_range = [(start_time_s + datetime.timedelta(seconds=i * d + i * gap_between_intervals_s),
                  start_time_s + datetime.timedelta(seconds=(i + 1) * d + i * gap_between_intervals_s))
                 for i in range(number_of_intervals)]
    return [(ta.strftime("%Y-%m-%d %H:%M:%S"), tb.strftime("%Y-%m-%d %H:%M:%S")) for ta, tb in sec_range]


def compute_overlap_time(range1, range2):
    overlap_time = []
    for start1, end1 in range1:
        for start2, end2 in range2:
            low = max(start1, start2)
            high = min(end1, end2)
            
            if low < high:
                overlap_time.append((low, high))
    return overlap_time


# if __name__ == "__main__":
#     large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
#     short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
#     print(compute_overlap_time(large, short))
# 设置默认的 API URL 结构
ISS_API_URL = "https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/56/0/0/0/5/50&apiKey={}"

def unix_to_datetime_str(timestamp):
    """Converts a Unix timestamp to the required datetime string format."""
    # datetime.datetime.fromtimestamp(timestamp) 是题目要求的转换函数
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    # 假设需要的格式是 'YYYY-MM-DD HH:MM:SS'
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


def iss_passes(api_key):
    """
    Fetches visible ISS passes from a given location using the n2yo API.
    
    The location (lat=56, lon=0, alt=0) is hardcoded as per the example URL.
    Returns a list of tuples: [(start_time_str, end_time_str), ...]
    """
    url = ISS_API_URL.format(api_key)
    
    try:
        # 发起 API 请求
        response = requests.get(url, timeout=10)
        response.raise_for_status() # 检查是否有 HTTP 错误
        
        data = response.json()
        
        passes_list = []
        
        # 检查响应中是否有 passes 数据
        if 'passes' in data:
            for pass_info in data['passes']:
                # 获取 start and end Unix timestamps
                start_time_unix = pass_info.get('startUTC')
                end_time_unix = pass_info.get('endUTC')
                
                if start_time_unix and end_time_unix:
                    # 转换时间戳为字符串格式
                    start_str = unix_to_datetime_str(start_time_unix)
                    end_str = unix_to_datetime_str(end_time_unix)
                    
                    passes_list.append((start_str, end_str))
        
        return passes_list

    except requests.exceptions.RequestException as e:
        print(f"Error fetching ISS passes: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []