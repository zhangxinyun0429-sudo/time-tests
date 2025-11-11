# test_times.py
"""
时间范围和重叠计算功能的单元测试（使用参数化）
"""
import pytest
from unittest.mock import patch, Mock
from times import (
    time_range, 
    compute_overlap_time, 
    unix_to_datetime_str, 
    iss_passes
)


# ============================================
# 测试 time_range 函数（参数化）
# ============================================

@pytest.mark.parametrize(
    "start,end,intervals,gap,expected_count",
    [
        # 单个区间，无间隔
        ("2010-01-12 10:00:00", "2010-01-12 12:00:00", 1, 0, 1),
        # 两个区间，无间隔
        ("2010-01-12 10:00:00", "2010-01-12 12:00:00", 2, 0, 2),
        # 三个区间，有间隔
        ("2010-01-12 10:00:00", "2010-01-12 13:00:00", 3, 900, 3),
        # 四个区间，有间隔
        ("2010-01-12 10:00:00", "2010-01-12 11:00:00", 4, 300, 4),
    ],
    ids=["single", "double", "triple", "quad"]
)
def test_time_range_interval_count(start, end, intervals, gap, expected_count):
    """参数化测试：验证生成的区间数量"""
    result = time_range(start, end, intervals, gap)
    assert len(result) == expected_count


@pytest.mark.parametrize(
    "start,end,expected_start,expected_end",
    [
        # 基本情况
        ("2010-01-12 10:00:00", "2010-01-12 12:00:00",
         "2010-01-12 10:00:00", "2010-01-12 12:00:00"),
        # 跨午夜
        ("2010-01-12 23:00:00", "2010-01-13 01:00:00",
         "2010-01-12 23:00:00", "2010-01-13 01:00:00"),
        # 很短的间隔
        ("2010-01-12 10:00:00", "2010-01-12 10:00:01",
         "2010-01-12 10:00:00", "2010-01-12 10:00:01"),
    ],
    ids=["basic", "cross_midnight", "one_second"]
)
def test_time_range_boundaries(start, end, expected_start, expected_end):
    """参数化测试：验证边界情况"""
    result = time_range(start, end)
    assert len(result) == 1
    assert result[0][0] == expected_start
    assert result[0][1] == expected_end


# ============================================
# 测试 time_range 输入验证（参数化）
# ============================================

@pytest.mark.parametrize(
    "start,end,error_match",
    [
        # 结束时间早于开始时间
        ("2010-01-12 12:00:00", "2010-01-12 10:00:00", "must be after"),
        # 开始和结束时间相同
        ("2010-01-12 10:00:00", "2010-01-12 10:00:00", "must be after"),
    ],
    ids=["backwards", "same_time"]
)
def test_time_range_validation(start, end, error_match):
    """参数化测试：验证输入验证"""
    with pytest.raises(ValueError, match=error_match):
        time_range(start, end)


# ============================================
# 测试 compute_overlap_time（参数化）⭐ 核心部分
# ============================================

@pytest.mark.parametrize(
    "range1_params,range2_params,expected",
    [
        # 测试 1: 题目给定的示例
        (
            ("2010-01-12 10:00:00", "2010-01-12 12:00:00"),
            ("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60),
            [
                ("2010-01-12 10:30:00", "2010-01-12 10:37:00"),
                ("2010-01-12 10:38:00", "2010-01-12 10:45:00")
            ]
        ),
        
        # 测试 2: 完全重叠
        (
            ("2010-01-12 10:00:00", "2010-01-12 12:00:00"),
            ("2010-01-12 10:30:00", "2010-01-12 11:30:00"),
            [("2010-01-12 10:30:00", "2010-01-12 11:30:00")]
        ),
        
        # 测试 3: 部分重叠
        (
            ("2010-01-12 10:00:00", "2010-01-12 11:30:00"),
            ("2010-01-12 11:00:00", "2010-01-12 12:00:00"),
            [("2010-01-12 11:00:00", "2010-01-12 11:30:00")]
        ),
        
        # 测试 4: 完全不重叠
        (
            ("2010-01-12 10:00:00", "2010-01-12 11:00:00"),
            ("2010-01-12 12:30:00", "2010-01-12 13:30:00"),
            []
        ),
        
        # 测试 5: 边界相接
        (
            ("2010-01-12 10:00:00", "2010-01-12 11:00:00"),
            ("2010-01-12 11:00:00", "2010-01-12 12:00:00"),
            []
        ),
        
        # 测试 6: 多个区间
        (
            ("2010-01-12 10:00:00", "2010-01-12 13:00:00", 3, 900),
            ("2010-01-12 10:40:00", "2010-01-12 11:20:00", 2, 120),
            [
                ("2010-01-12 10:40:00", "2010-01-12 10:50:00"),
                ("2010-01-12 11:05:00", "2010-01-12 11:20:00")
            ]
        ),
    ],
    ids=[
        "given_input",
        "complete_overlap",
        "partial_overlap",
        "no_overlap",
        "touching_edges",
        "multiple_intervals"
    ]
)
def test_compute_overlap_scenarios(range1_params, range2_params, expected):
    """
    参数化测试：各种重叠场景
    
    这个测试替代了之前的多个独立测试函数：
    - test_given_input
    - test_complete_overlap
    - test_partial_overlap
    - test_no_overlap
    - test_touching_edges
    - test_multiple_intervals_overlap
    """
    # 生成时间范围
    range1 = time_range(*range1_params)
    range2 = time_range(*range2_params)
    
    # 计算重叠
    result = compute_overlap_time(range1, range2)
    
    # 验证结果
    assert result == expected


# 边界情况的参数化测试
@pytest.mark.parametrize(
    "range1,range2,expected",
    [
        # 空列表
        ([], [], []),
        # 一个空列表
        ([("2010-01-12 10:00:00", "2010-01-12 11:00:00")], [], []),
        # 与自身重叠
        (
            [("2010-01-12 10:00:00", "2010-01-12 11:00:00")],
            [("2010-01-12 10:00:00", "2010-01-12 11:00:00")],
            [("2010-01-12 10:00:00", "2010-01-12 11:00:00")]
        ),
    ],
    ids=["both_empty", "one_empty", "self_overlap"]
)
def test_compute_overlap_edge_cases(range1, range2, expected):
    """参数化测试：边界情况"""
    result = compute_overlap_time(range1, range2)
    assert result == expected


# ============================================
# 测试 unix_to_datetime_str（参数化）
# ============================================

@pytest.mark.parametrize(
    "timestamp,should_contain",
    [
        (0, "1970"),  # Unix 纪元
        (1263290400, "2010"),  # 2010 年某个时间
        (1704067200, "202"),  # 2024 或 2023（考虑时区）
    ],
    ids=["epoch", "2010", "2024"]
)
def test_unix_conversion(timestamp, should_contain):
    """参数化测试：Unix 时间戳转换"""
    result = unix_to_datetime_str(timestamp)
    assert isinstance(result, str)
    assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS"
    assert should_contain in result


# ============================================
# 测试 iss_passes（使用 Mock，保留原样）
# ============================================

class TestISSPasses:
    """ISS API 测试（使用 Mock）"""
    
    @patch('times.requests.get')
    def test_successful_api_call(self, mock_get):
        """测试成功的 API 调用"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'passes': [
                {'startUTC': 1263290400, 'endUTC': 1263294000},
                {'startUTC': 1263380400, 'endUTC': 1263384000}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = iss_passes('test_api_key')
        
        assert len(result) == 2
        assert all(isinstance(item, tuple) for item in result)
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
    def test_api_request_exception(self, mock_get):
        """测试 API 请求异常"""
        mock_get.side_effect = Exception("Network error")
        
        result = iss_passes('test_api_key')
        assert result == []