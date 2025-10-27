from times import compute_overlap_time, time_range

def test_generic_case():
    large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
    short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
    expected = [("2010-01-12 10:30:00","2010-01-12 10:37:00"), ("2010-01-12 10:38:00", "2010-01-12 10:45:00")]
    assert compute_overlap_time(large, short) == expected

def test_non_overlapping_ranges():
    """Test two time ranges that do not overlap."""
    # Test two time ranges that do not overlap
    range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:30:00")
    range2 = time_range("2024-05-15 11:00:00", "2024-05-15 11:30:00")
    expected = []
    
    result = compute_overlap_time(range1, range2)
    assert result == expected

# --- Required Test 2: Two time ranges with multiple intervals each ---
def test_multiple_interval_overlaps():
    """Test two time ranges, both containing several intervals, ensuring all overlaps are captured."""
    # R1: 10:00:00 - 10:15:00, 2 intervals, 5 minutes gap (300s) => [10:00:00, 10:05:00), [10:10:00, 10:15:00) 
    range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:15:00", 2, 5 * 60)
    # R2: 10:03:00 - 10:17:00, 2 intervals, 4 minutes gap (240s) => [10:03:00, 10:08:00), [10:12:00, 10:17:00) 
    range2 = time_range("2024-05-15 10:03:00", "2024-05-15 10:17:00", 2, 4 * 60)
    
    # Expected Overlaps: [10:03:00, 10:05:00) and [10:12:00, 10:15:00)
    expected = [
        ("2024-05-15 10:03:00", "2024-05-15 10:05:00"), 
        ("2024-05-15 10:12:00", "2024-05-15 10:15:00")
    ]
    
    result = compute_overlap_time(range1, range2)
    assert sorted(result) == sorted(expected)

# --- Required Test 3: Two time ranges that end exactly when the other starts ---
def test_touching_ranges_no_overlap():
    """Test two time ranges that touch at a single point (R1 ends when R2 starts); intersection should be empty."""
    # R1: [10:00, 10:30)
    range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:30:00")
    # R2: [10:30, 11:00)
    range2 = time_range("2024-05-15 10:30:00", "2024-05-15 11:00:00")
    expected = []
    
    result = compute_overlap_time(range1, range2)
    assert result == expected