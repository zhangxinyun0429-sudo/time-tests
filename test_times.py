# test_times.py
"""
时间范围和重叠计算功能的完整单元测试
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from times import (
    time_range, 
    compute_overlap_time, 
    unix_to_datetime_str, 
    iss_passes
)


# ============================================
# 测试 time_range 函数
# ============================================

class TestTimeRange:
    """time_range 函数的测试用例集合"""
    
    def test_single_interval_default(self):
        """测试默认情况：单个区间，无间隔"""
        result = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
        expected = [("2010-01-12 10:00:00", "2010-01-12 12:00:00")]
        assert result == expected
    
    def test_multiple_intervals_no_gap(self):
        """测试多个区间，无间隔"""
        result = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 12:00:00",
            number_of_intervals=2
        )
        assert len(result) == 2
        assert result[0] == ("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        assert result[1] == ("2010-01-12 11:00:00", "2010-01-12 12:00:00")
    
    def test_multiple_intervals_with_gap(self):
        """测试题目中给定的示例"""
        result = time_range(
            "2010-01-12 10:30:00", 
            "2010-01-12 10:45:00", 
            number_of_intervals=2, 
            gap_between_intervals_s=60
        )
        assert len(result) == 2
        assert result[0] == ("2010-01-12 10:30:00", "2010-01-12 10:37:00")
        assert result[1] == ("2010-01-12 10:38:00", "2010-01-12 10:45:00")
    
    def test_three_intervals_with_breaks(self):
        """测试三个区间，有较长的间隔"""
        result = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 13:00:00", 
            number_of_intervals=3, 
            gap_between_intervals_s=900
        )
        assert len(result) == 3
        assert result[0][0] == "2010-01-12 10:00:00"
        assert result[2][1] == "2010-01-12 13:00:00"
    
    def test_very_short_interval(self):
        """测试非常短的时间间隔（1秒）"""
        result = time_range("2010-01-12 10:00:00", "2010-01-12 10:00:01")
        assert len(result) == 1
        assert result[0] == ("2010-01-12 10:00:00", "2010-01-12 10:00:01")
    
    def test_cross_midnight(self):
        """测试跨越午夜的时间范围"""
        result = time_range("2010-01-12 23:00:00", "2010-01-13 01:00:00")
        assert len(result) == 1
        assert result[0][0] == "2010-01-12 23:00:00"
        assert result[0][1] == "2010-01-13 01:00:00"


# ============================================
# 测试 time_range 函数的输入验证
# ============================================

class TestTimeRangeValidation:
    """time_range 函数输入验证的测试用例"""
    
    def test_backwards_time_raises_error(self):
        """测试结束时间早于开始时间"""
        with pytest.raises(ValueError, match="must be after"):
            time_range("2010-01-12 12:00:00", "2010-01-12 10:00:00")
    
    def test_same_start_end_time_raises_error(self):
        """测试开始和结束时间相同"""
        with pytest.raises(ValueError, match="must be after"):
            time_range("2010-01-12 10:00:00", "2010-01-12 10:00:00")
    
    def test_invalid_date_format_raises_error(self):
        """测试无效的日期格式"""
        with pytest.raises(ValueError):
            time_range("not-a-date", "2010-01-12 10:00:00")


# ============================================
# 测试 compute_overlap_time 函数
# ============================================

class TestComputeOverlapTime:
    """compute_overlap_time 函数的测试用例集合"""
    
    def test_given_input(self):
        """测试题目中给定的示例"""
        large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
        short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
        expected = [
            ("2010-01-12 10:30:00", "2010-01-12 10:37:00"),
            ("2010-01-12 10:38:00", "2010-01-12 10:45:00")
        ]
        assert compute_overlap_time(large, short) == expected
    
    def test_complete_overlap(self):
        """测试完全重叠"""
        large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
        small = time_range("2010-01-12 10:30:00", "2010-01-12 11:30:00")
        expected = [("2010-01-12 10:30:00", "2010-01-12 11:30:00")]
        assert compute_overlap_time(large, small) == expected
    
    def test_partial_overlap(self):
        """测试部分重叠"""
        range1 = time_range("2010-01-12 10:00:00", "2010-01-12 11:30:00")
        range2 = time_range("2010-01-12 11:00:00", "2010-01-12 12:00:00")
        expected = [("2010-01-12 11:00:00", "2010-01-12 11:30:00")]
        assert compute_overlap_time(range1, range2) == expected
    
    def test_no_overlap(self):
        """测试完全不重叠"""
        before = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        after = time_range("2010-01-12 12:30:00", "2010-01-12 13:30:00")
        expected = []
        assert compute_overlap_time(before, after) == expected
    
    def test_touching_edges(self):
        """测试边界相接但不重叠"""
        before = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        after = time_range("2010-01-12 11:00:00", "2010-01-12 12:00:00")
        expected = []
        assert compute_overlap_time(before, after) == expected
    
    def test_empty_ranges(self):
        """测试空的时间范围列表"""
        result = compute_overlap_time([], [])
        assert result == []
    
    def test_one_empty_range(self):
        """测试一个空列表和一个正常列表"""
        normal = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        result = compute_overlap_time(normal, [])
        assert result == []
    
    def test_same_interval_overlap_with_self(self):
        """测试时间范围与自身的重叠"""
        range1 = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        result = compute_overlap_time(range1, range1)
        expected = [("2010-01-12 10:00:00", "2010-01-12 11:00:00")]
        assert result == expected
    
    def test_multiple_intervals_overlap(self):
        """测试多个区间的复杂重叠"""
        three_hours = time_range("2010-01-12 10:00:00", "2010-01-12 13:00:00", 3, 900)
        two_ranges = time_range("2010-01-12 10:40:00", "2010-01-12 11:20:00", 2, 120)
        result = compute_overlap_time(three_hours, two_ranges)
        # 应该有重叠
        assert len(result) > 0


# ============================================
# 测试 unix_to_datetime_str 函数
# ============================================

class TestUnixToDatetimeStr:
    """unix_to_datetime_str 函数的测试用例"""
    
    def test_basic_conversion(self):
        """测试基本的时间戳转换"""
        # 2010-01-12 10:00:00 UTC 的时间戳
        timestamp = 1263290400
        result = unix_to_datetime_str(timestamp)
        # 注意：这取决于系统时区，可能需要调整
        assert isinstance(result, str)
        assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS" 格式
    
    def test_zero_timestamp(self):
        """测试零时间戳（Unix 纪元）"""
        timestamp = 0
        result = unix_to_datetime_str(timestamp)
        assert isinstance(result, str)
        # 1970-01-01 00:00:00 (可能因时区不同)
        assert "1970" in result
    
    def test_recent_timestamp(self):
        """测试最近的时间戳"""
        # 2024-01-01 00:00:00 UTC 的时间戳
        timestamp = 1704067200
        result = unix_to_datetime_str(timestamp)
        assert "2024" in result or "2023" in result  # 考虑时区差异
    
    def test_format_correctness(self):
        """测试返回格式的正确性"""
        timestamp = 1263290400
        result = unix_to_datetime_str(timestamp)
        # 验证格式：YYYY-MM-DD HH:MM:SS
        parts = result.split()
        assert len(parts) == 2  # 日期和时间两部分
        assert len(parts[0].split('-')) == 3  # 年-月-日
        assert len(parts[1].split(':')) == 3  # 时:分:秒


# ============================================
# 测试 iss_passes 函数
# ============================================

class TestISSPasses:
    """iss_passes 函数的测试用例"""
    
    @patch('times.requests.get')
    def test_successful_api_call(self, mock_get):
        """测试成功的 API 调用"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'passes': [
                {'startUTC': 1263290400, 'endUTC': 1263294000},
                {'startUTC': 1263380400, 'endUTC': 1263384000}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 调用函数
        result = iss_passes('test_api_key')
        
        # 验证
        assert len(result) == 2
        assert all(isinstance(item, tuple) for item in result)
        assert all(len(item) == 2 for item in result)
        
        # 验证 API 被正确调用
        mock_get.assert_called_once()
    
    @patch('times.requests.get')
    def test_empty_passes(self, mock_get):
        """测试空的 passes 响应"""
        mock_response = Mock()
        mock_response.json.return_value = {'passes': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = iss_passes('test_api_key')
        assert result == []
    
    @patch('times.requests.get')
    def test_missing_passes_key(self, mock_get):
        """测试响应中缺少 passes 键"""
        mock_response = Mock()
        mock_response.json.return_value = {'error': 'some error'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = iss_passes('test_api_key')
        assert result == []
    
    @patch('times.requests.get')
    def test_incomplete_pass_data(self, mock_get):
        """测试不完整的 pass 数据"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'passes': [
                {'startUTC': 1263290400},  # 缺少 endUTC
                {'endUTC': 1263294000},    # 缺少 startUTC
                {'startUTC': 1263380400, 'endUTC': 1263384000}  # 完整的
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = iss_passes('test_api_key')
        # 只有完整的数据应该被包含
        assert len(result) == 1
    
    @patch('times.requests.get')
    def test_api_request_exception(self, mock_get):
        """测试 API 请求异常"""
        mock_get.side_effect = Exception("Network error")
        
        result = iss_passes('test_api_key')
        assert result == []
    
    @patch('times.requests.get')
    def test_api_http_error(self, mock_get):
        """测试 HTTP 错误"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_get.return_value = mock_response
        
        result = iss_passes('test_api_key')
        assert result == []
    
    @patch('times.requests.get')
    def test_custom_parameters(self, mock_get):
        """测试自定义参数"""
        mock_response = Mock()
        mock_response.json.return_value = {'passes': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 使用自定义参数调用
        iss_passes('test_key', lat=40, lon=-74, alt=100, days=10, min_visibility=60)
        
        # 验证 URL 中包含了自定义参数
        called_url = mock_get.call_args[0][0]
        assert '40' in called_url  # lat
        assert '-74' in called_url  # lon
        assert '100' in called_url  # alt


# ============================================
# 集成测试
# ============================================

class TestIntegration:
    """集成测试 - 测试函数协同工作"""
    
    def test_workflow_create_and_compute(self):
        """测试完整工作流"""
        work_hours = time_range("2010-01-12 09:00:00", "2010-01-12 17:00:00")
        meetings = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 12:00:00",
            number_of_intervals=2,
            gap_between_intervals_s=1800
        )
        overlaps = compute_overlap_time(work_hours, meetings)
        
        assert len(overlaps) == 2
        assert overlaps == meetings
    
    @patch('times.requests.get')
    def test_iss_passes_with_time_range(self, mock_get):
        """测试 ISS passes 与 time_range 的结合"""
        # 模拟 ISS API 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'passes': [
                {'startUTC': 1263290400, 'endUTC': 1263294000}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 获取 ISS passes
        iss_times = iss_passes('test_key')
        
        # 创建一个观测窗口
        observation_window = time_range(
            "2010-01-12 09:00:00", 
            "2010-01-12 15:00:00"
        )
        
        # 如果有 ISS passes，可以计算重叠
        if iss_times:
            # 这里只是验证格式正确
            assert len(iss_times) > 0
            assert isinstance(iss_times[0], tuple)


# ============================================
# 参数化测试
# ============================================

@pytest.mark.parametrize("start,end,intervals,gap,expected_count", [
    ("2010-01-12 10:00:00", "2010-01-12 12:00:00", 1, 0, 1),
    ("2010-01-12 10:00:00", "2010-01-12 12:00:00", 2, 0, 2),
    ("2010-01-12 10:00:00", "2010-01-12 13:00:00", 3, 900, 3),
    ("2010-01-12 10:00:00", "2010-01-12 11:00:00", 4, 300, 4),
])
def test_time_range_interval_count(start, end, intervals, gap, expected_count):
    """参数化测试：验证生成的区间数量"""
    result = time_range(start, end, intervals, gap)
    assert len(result) == expected_count


@pytest.mark.parametrize("timestamp,should_contain", [
    (0, "1970"),
    (1263290400, "2010"),
    (1704067200, "202"),  # 2024或2023，取决于时区
])
def test_unix_conversion_years(timestamp, should_contain):
    """参数化测试：验证时间戳转换的年份"""
    result = unix_to_datetime_str(timestamp)
    assert should_contain in result