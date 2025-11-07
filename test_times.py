import pytest
import yaml
from pathlib import Path
from times import compute_overlap_time, time_range

# --- 1. YAML Data Loading Fixture ---

# 获取 fixture.yaml 的路径 (假设它在与此文件相同的目录下)
YAML_FILE_PATH = Path(__file__).parent / "fixture.yaml"

def load_yaml_data():
    """Reads all test data from the external fixture.yaml file."""
    if not YAML_FILE_PATH.exists():
        pytest.fail(f"Error: Required test data file not found at {YAML_FILE_PATH}")
    with open(YAML_FILE_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Pytest fixture to load the data once
@pytest.fixture(scope="module")
def test_data():
    """Module-scoped fixture to ensure data is loaded only once."""
    return load_yaml_data()

# --- 2. Data Preparation for Parametrize ---

def extract_overlap_cases(data: dict):
    """Prepares the overlap test cases for parametrize."""
    test_cases = []
    # 从 'overlap_tests' 键中获取所有测试案例
    for case in data.get('overlap_tests', []):
        # 提取参数和 ID
        test_cases.append((
            case['range1_params'],
            case['range2_params'],
            case['expected'],
            case['expected_len_check'],
            case['name']
        ))
    return test_cases

def extract_exception_cases(data: dict):
    """Prepares the time_range exception cases for parametrize."""
    test_cases = []
    # 从 'time_range_exceptions' 键中获取所有测试案例
    for case in data.get('time_range_exceptions', []):
        test_cases.append((
            case['start'],
            case['end'],
            case['expected_error'],
            case['name']
        ))
    return test_cases


# --- 3. Parametrized Test Functions ---

# 使用 pytest.fixture 来加载数据，然后提取参数
@pytest.mark.parametrize(
    "range1_params, range2_params, expected, expected_len_check, case_name",
    extract_overlap_cases(load_yaml_data()),
    ids=lambda x: x[-1] # 使用 YAML 中的 'name' 字段作为测试 ID
)
def test_compute_overlap(range1_params, range2_params, expected, expected_len_check, case_name):
    """
    Tests various compute_overlap_time cases loaded from fixture.yaml.
    The parameters for time_range are stored in the YAML.
    """
    
    # Helper function to safely call time_range with variable arguments
    def create_range(params):
        # 移除 params 列表末尾的 None/null 值，以匹配 time_range 的签名
        actual_params = [p for p in params if p is not None]
        return time_range(*actual_params)

    # 1. 创建 time_range 对象
    range1 = create_range(range1_params)
    range2 = create_range(range2_params)
    
    # 2. 计算重叠结果
    result = compute_overlap_time(range1, range2)
    
    # 3. 执行断言
    if expected_len_check:
        # 对应于原始的 test_multiple_intervals 逻辑
        assert len(result) > 0
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
    else:
        # 检查精确值（适用于通用、不重叠和相邻情况）
        # 将 YAML 中的列表 Expected 转换为元组列表，以匹配 compute_overlap_time 的返回类型
        expected_tuples = [tuple(item) for item in expected]
        assert result == expected_tuples


@pytest.mark.parametrize(
    "start_time, end_time, expected_error, case_name",
    extract_exception_cases(load_yaml_data()),
    ids=lambda x: x[-1]
)
def test_time_range_exceptions(start_time, end_time, expected_error, case_name):
    """Tests that time_range raises ValueError when end_time is before start_time."""
    with pytest.raises(ValueError) as excinfo:
        time_range(start_time, end_time)
    assert expected_error in str(excinfo.value).lower()
    
# NOTE: The original test_backwards_time_range is now parameterized and covered above.