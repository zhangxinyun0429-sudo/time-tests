import pytest
from unittest.mock import patch, Mock
from times import iss_passes, unix_to_datetime_str
import datetime
import requests # 需要导入 requests 来模拟它

# 示例 API 响应数据，包含两个过境时间
MOCK_API_RESPONSE = {
    "info": {
        "satid": 25544,
        # ... 其他信息
    },
    # 重要的 'passes' 列表，包含 Unix 时间戳
    "passes": [
        {
            "startUTC": 1667829600, # 假设是 2022-11-07 10:00:00 UTC
            "endUTC": 1667830200,   # 假设是 2022-11-07 10:10:00 UTC
            # ... 其他 pass 信息
        },
        {
            "startUTC": 1667854800, # 假设是 2022-11-07 17:00:00 UTC
            "endUTC": 1667855700,   # 假设是 2022-11-07 17:15:00 UTC
            # ...
        }
    ]
}

# 预期的结果列表（需要匹配 unix_to_datetime_str 的输出）
EXPECTED_RESULT = [
    (unix_to_datetime_str(1667829600), unix_to_datetime_str(1667830200)),
    (unix_to_datetime_str(1667854800), unix_to_datetime_str(1667855700)),
]

# 使用 @patch 装饰器来模拟 requests.get
@patch('requests.get')
def test_iss_passes_mocked_success(mock_get):
    """
    Tests iss_passes function by mocking the API response.
    This avoids making a real web request.
    """
    # 1. 配置模拟响应对象
    # 创建一个 Mock 对象来模拟 requests.Response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE
    
    # 告诉 mock_get 在被调用时返回我们配置的模拟响应
    mock_get.return_value = mock_response

    # 2. 调用被测试的函数
    test_api_key = "MOCKED_API_KEY"
    passes = iss_passes(test_api_key)

    # 3. 断言 (Assertions)
    
    # 断言 requests.get 确实被调用了，并且 URL 格式正确
    expected_url_format = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/56/0/0/0/5/50&apiKey={test_api_key}"
    mock_get.assert_called_once_with(expected_url_format, timeout=10)
    
    # 断言结果与预期数据相符
    assert passes == EXPECTED_RESULT

@patch('requests.get')
def test_iss_passes_mocked_no_data(mock_get):
    """Tests case where API returns a valid response but no passes."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"info": {"satid": 25544}} # No 'passes' key
    mock_get.return_value = mock_response
    
    passes = iss_passes("DUMMY")
    assert passes == []

@patch('requests.get', side_effect=requests.exceptions.Timeout)
def test_iss_passes_mocked_timeout(mock_get):
    """Tests case where API request times out."""
    passes = iss_passes("DUMMY")
    assert passes == []