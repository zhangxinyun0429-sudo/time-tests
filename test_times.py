# test_times.py
"""
时间范围和重叠计算功能的单元测试
"""
import pytest
from times import time_range, compute_overlap_time


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
        # 两个1小时的区间
        assert len(result) == 2
        assert result[0] == ("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        assert result[1] == ("2010-01-12 11:00:00", "2010-01-12 12:00:00")
    
    def test_multiple_intervals_with_gap(self):
        """测试多个区间，有间隔"""
        result = time_range(
            "2010-01-12 10:30:00", 
            "2010-01-12 10:45:00", 
            number_of_intervals=2, 
            gap_between_intervals_s=60
        )
        # 两个7分钟的区间，中间有1分钟间隔
        assert len(result) == 2
        assert result[0] == ("2010-01-12 10:30:00", "2010-01-12 10:37:00")
        assert result[1] == ("2010-01-12 10:38:00", "2010-01-12 10:45:00")
    
    def test_three_intervals_with_breaks(self):
        """测试三个区间，有较长的间隔"""
        result = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 13:00:00", 
            number_of_intervals=3, 
            gap_between_intervals_s=900  # 15分钟间隔
        )
        assert len(result) == 3
        # 验证第一个区间
        assert result[0][0] == "2010-01-12 10:00:00"
        # 验证最后一个区间的结束时间
        assert result[2][1] == "2010-01-12 13:00:00"


# ============================================
# 测试 time_range 函数的输入验证
# ============================================

class TestTimeRangeValidation:
    """time_range 函数输入验证的测试用例"""
    
    def test_backwards_time_raises_error(self):
        """测试结束时间早于开始时间时抛出 ValueError"""
        with pytest.raises(ValueError, match="must be after"):
            time_range(
                "2010-01-12 12:00:00",  # 结束时间
                "2010-01-12 10:00:00"   # 开始时间 - 错误！
            )
    
    def test_same_start_end_time_raises_error(self):
        """测试开始和结束时间相同时抛出 ValueError"""
        with pytest.raises(ValueError, match="must be after"):
            time_range(
                "2010-01-12 10:00:00",
                "2010-01-12 10:00:00"
            )
    
    def test_invalid_date_format_raises_error(self):
        """测试无效的日期格式"""
        with pytest.raises(ValueError):
            time_range("not-a-date", "2010-01-12 10:00:00")
        
        with pytest.raises(ValueError):
            time_range("2010-01-12", "2010-01-12 10:00:00")


# ============================================
# 测试 compute_overlap_time 函数
# ============================================

class TestComputeOverlapTime:
    """compute_overlap_time 函数的测试用例集合"""
    
    def test_generic_case(self):
        """测试题目中给定的示例"""
        large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
        short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
        expected = [
            ("2010-01-12 10:30:00", "2010-01-12 10:37:00"),
            ("2010-01-12 10:38:00", "2010-01-12 10:45:00")
        ]
        assert compute_overlap_time(large, short) == expected
    
    def test_complete_overlap(self):
        """测试完全重叠的情况"""
        large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
        small = time_range("2010-01-12 10:30:00", "2010-01-12 11:30:00")
        expected = [("2010-01-12 10:30:00", "2010-01-12 11:30:00")]
        assert compute_overlap_time(large, small) == expected
    
    def test_partial_overlap(self):
        """测试部分重叠的情况"""
        range1 = time_range("2010-01-12 10:00:00", "2010-01-12 11:30:00")
        range2 = time_range("2010-01-12 11:00:00", "2010-01-12 12:00:00")
        expected = [("2010-01-12 11:00:00", "2010-01-12 11:30:00")]
        assert compute_overlap_time(range1, range2) == expected
    
    def test_no_overlap(self):
        """测试完全不重叠的情况"""
        before = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        after = time_range("2010-01-12 12:30:00", "2010-01-12 12:45:00", 2, 60)
        expected = []
        assert compute_overlap_time(before, after) == expected
    
    def test_touching_edges(self):
        """测试边界相接但不重叠的情况"""
        before = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        after = time_range("2010-01-12 11:00:00", "2010-01-12 12:45:00")
        expected = []
        assert compute_overlap_time(before, after) == expected
    
    def test_multiple_intervals_overlap(self):
        """测试两组多区间的重叠"""
        # 3个区间，每个50分钟，间隔15分钟
        three_hours = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 13:00:00", 
            3, 
            900
        )
        # 2个区间，跨越第一个间隔
        two_ranges = time_range(
            "2010-01-12 10:40:00", 
            "2010-01-12 11:20:00", 
            2, 
            120
        )
        expected = [
            ("2010-01-12 10:40:00", "2010-01-12 10:50:00"),
            ("2010-01-12 11:05:00", "2010-01-12 11:20:00")
        ]
        assert compute_overlap_time(three_hours, two_ranges) == expected
    
    def test_multiple_small_intervals_overlap(self):
        """测试多个小区间的复杂重叠"""
        range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:15:00", 2, 5 * 60)
        range2 = time_range("2024-05-15 10:03:00", "2024-05-15 10:17:00", 2, 4 * 60)
        
        result = compute_overlap_time(range1, range2)
        expected = [
            ("2024-05-15 10:03:00", "2024-05-15 10:05:00"), 
            ("2024-05-15 10:12:00", "2024-05-15 10:15:00")
        ]
        
        # 使用排序比较，因为顺序可能不同
        assert sorted(result) == sorted(expected)
    
    def test_empty_ranges(self):
        """测试空的时间范围列表"""
        result = compute_overlap_time([], [])
        assert result == []
    
    def test_one_empty_range(self):
        """测试一个空列表和一个正常列表"""
        normal = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        result = compute_overlap_time(normal, [])
        assert result == []


# ============================================
# 边界情况和特殊测试
# ============================================

class TestEdgeCases:
    """边界情况和特殊场景的测试"""
    
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
    
    def test_same_interval_overlap_with_self(self):
        """测试时间范围与自身的重叠"""
        range1 = time_range("2010-01-12 10:00:00", "2010-01-12 11:00:00")
        result = compute_overlap_time(range1, range1)
        expected = [("2010-01-12 10:00:00", "2010-01-12 11:00:00")]
        assert result == expected
    
    def test_many_tiny_intervals(self):
        """测试很多小区间"""
        result = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 10:10:00",
            number_of_intervals=10
        )
        assert len(result) == 10
        # 每个区间应该是1分钟
        for start, end in result:
            # 简单验证格式正确
            assert len(start) == 19
            assert len(end) == 19


# ============================================
# 集成测试
# ============================================

class TestIntegration:
    """集成测试 - 测试多个函数协同工作"""
    
    def test_workflow_create_and_compute(self):
        """测试完整工作流：创建时间范围并计算重叠"""
        # 步骤1：创建工作时间
        work_hours = time_range("2010-01-12 09:00:00", "2010-01-12 17:00:00")
        
        # 步骤2：创建会议时间（2个会议，中间休息）
        meetings = time_range(
            "2010-01-12 10:00:00", 
            "2010-01-12 12:00:00",
            number_of_intervals=2,
            gap_between_intervals_s=1800  # 30分钟休息
        )
        
        # 步骤3：计算重叠
        overlaps = compute_overlap_time(work_hours, meetings)
        
        # 验证：应该有2个重叠（2个会议都在工作时间内）
        assert len(overlaps) == 2
        
        # 验证重叠时间就是会议时间
        assert overlaps == meetings


# ============================================
# 参数化测试（可选 - 更简洁的版本）
# ============================================

@pytest.mark.parametrize("start,end,intervals,gap,expected_count", [
    ("2010-01-12 10:00:00", "2010-01-12 12:00:00", 1, 0, 1),
    ("2010-01-12 10:00:00", "2010-01-12 12:00:00", 2, 0, 2),
    ("2010-01-12 10:00:00", "2010-01-12 13:00:00", 3, 900, 3),
    ("2010-01-12 10:00:00", "2010-01-12 11:00:00", 4, 300, 4),
])
def test_time_range_interval_count(start, end, intervals, gap, expected_count):
    """参数化测试：验证生成的区间数量正确"""
    result = time_range(start, end, intervals, gap)
    assert len(result) == expected_count


@pytest.mark.parametrize("start1,end1,start2,end2,should_overlap", [
    # 完全重叠
    ("2010-01-12 10:00:00", "2010-01-12 12:00:00",
     "2010-01-12 10:30:00", "2010-01-12 11:30:00", True),
    # 部分重叠
    ("2010-01-12 10:00:00", "2010-01-12 11:00:00",
     "2010-01-12 10:30:00", "2010-01-12 11:30:00", True),
    # 完全不重叠
    ("2010-01-12 10:00:00", "2010-01-12 11:00:00",
     "2010-01-12 12:00:00", "2010-01-12 13:00:00", False),
    # 边界相接
    ("2010-01-12 10:00:00", "2010-01-12 11:00:00",
     "2010-01-12 11:00:00", "2010-01-12 12:00:00", False),
])
def test_overlap_scenarios(start1, end1, start2, end2, should_overlap):
    """参数化测试：各种重叠场景"""
    range1 = time_range(start1, end1)
    range2 = time_range(start2, end2)
    result = compute_overlap_time(range1, range2)
    
    if should_overlap:
        assert len(result) > 0, "应该有重叠但没有找到"
    else:
        assert len(result) == 0, "不应该有重叠但找到了重叠"