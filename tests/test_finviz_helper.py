import pandas as pd
from unittest.mock import Mock, patch
import pytest
from tools.finviz_helper import (
    get_sp500_tickers_sectors,
    get_nasdaq100_tickers_sectors,
    get_djia_tickers_sectors,
    get_screener,
    get_groups,
    verify_group_name,
    verify_subgroup_name,
    get_group_layout,
    get_request,
    get_screener_layout
)

# Mock data to be used across multiple tests
mocked_screener_data = pd.DataFrame({
    'Ticker': ['AAPL', 'MSFT', 'GOOGL'],
    'Sector': ['Technology', 'Technology', 'Communication Services']
})

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get

@pytest.fixture
def mock_screener():
    with patch('pyfinviz.screener.Screener') as mock_screener_class:
        mock_screener_instance = mock_screener_class.return_value
        mock_screener_instance.data_frames.values.return_value = [mocked_screener_data]
        yield mock_screener_instance

# Test functions for the screener data retrieval
# def test_get_sp500_tickers_sectors(mock_screener):
#     df = get_sp500_tickers_sectors()
#     assert not df.empty
#     assert 'Ticker' in df.columns and 'Sector' in df.columns
#
# def test_get_nasdaq100_tickers_sectors(mock_screener):
#     df = get_nasdaq100_tickers_sectors()
#     assert not df.empty
#     assert 'Ticker' in df.columns and 'Sector' in df.columns
#
# def test_get_djia_tickers_sectors(mock_screener):
#     df = get_djia_tickers_sectors()
#     assert not df.empty
#     assert 'Ticker' in df.columns and 'Sector' in df.columns

# Tests for other utility functions
def test_verify_group_name():
    assert verify_group_name('sector') == 'sector'
    assert verify_group_name('invalid') == 'sector'

def test_verify_subgroup_name():
    with pytest.raises(Exception):
        verify_subgroup_name('sector', 'invalid')  # Should raise an exception
    assert verify_subgroup_name('industry', 'basicmaterials') == 'basicmaterials'

def test_get_group_layout():
    assert get_group_layout('Overview') == '110'
    assert get_group_layout('Invalid') == '110'  # Should return default '110'

def test_get_screener_layout():
    assert get_screener_layout('Overview') == '111'
    assert get_screener_layout('Invalid') == '111'  # Should return default '111'

def test_get_request(mock_requests_get):
    api_token = 'fake_api_token'
    filters = 'fake_filters'
    get_request(api_token, filters)
    mock_requests_get.assert_called_once_with(f"https://elite.finviz.com/export.ashx?{filters}&auth={api_token}")

# You would also want to test get_screener and get_groups, but these would require more complex mocking
# to simulate the API responses and handle the sleep_secs argument properly.
