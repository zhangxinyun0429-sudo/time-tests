import pytest
from times import compute_overlap_time, time_range


def test_generic_case():
    """Original test from sample solution"""
    large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
    short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
    expected = [("2010-01-12 10:30:00", "2010-01-12 10:37:00"), 
                ("2010-01-12 10:38:00", "2010-01-12 10:45:00")]
    assert compute_overlap_time(large, short) == expected


def test_non_overlapping_ranges():
    """Test two time ranges that do not overlap"""
    range1 = time_range("2010-01-12 09:00:00", "2010-01-12 11:00:00")
    range2 = time_range("2010-01-12 14:00:00", "2010-01-12 16:00:00")
    result = compute_overlap_time(range1, range2)
    assert result == []


def test_multiple_intervals():
    """Test two time ranges that both contain several intervals each"""
    range1 = time_range("2010-01-12 09:00:00", "2010-01-12 12:00:00", 3, 60)
    range2 = time_range("2010-01-12 10:00:00", "2010-01-12 13:00:00", 2, 60)
    result = compute_overlap_time(range1, range2)
    assert len(result) > 0
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


def test_adjacent_ranges():
    """Test two time ranges that end exactly at the same time when the other starts"""
    range1 = time_range("2010-01-12 09:00:00", "2010-01-12 12:00:00")
    range2 = time_range("2010-01-12 12:00:00", "2010-01-12 15:00:00")
    result = compute_overlap_time(range1, range2)
    assert result == []


def test_backwards_time_range():
    """Test that time_range raises ValueError when end_time is before start_time"""
    with pytest.raises(ValueError) as excinfo:
        time_range("2010-01-12 12:00:00", "2010-01-12 10:00:00")
    assert "must be after" in str(excinfo.value).lower()