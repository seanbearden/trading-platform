# Standard library imports
import unittest
from unittest.mock import patch, MagicMock

# Third-party imports
import pandas as pd
import pytest
from requests.models import Response
from tda import client

# Local application/library specific imports
from tools.ameritrade_helper import get_quote, tda_auth, verify_entry, get_option_chain, get_expiration_date_summary


class TestExpirationDateSummary:

    @pytest.fixture(scope='class')
    def sample_data(self):
        # This method can be used to set up data that is common across tests
        data = {
            'instrument_symbol': ['CVX_111723C145', 'AAPL_121523C150'],
            'marketValue': [100, 200],
            'instrument_putCall': ['CALL', 'PUT']
        }
        return pd.DataFrame(data)

    def test_correct_date_extraction(self, sample_data):
        result = get_expiration_date_summary(sample_data)
        assert all(result['expiration_date'] == pd.Series(pd.to_datetime(['2023-11-17', '2023-12-15'])).dt.date)

    def test_aggregation_accuracy(self):
        data = {
            'instrument_symbol': ['CVX_111723C145', 'CVX_111723P145000'],
            'marketValue': [100, 200],
            'instrument_putCall': ['CALL', 'PUT']
        }
        df = pd.DataFrame(data)
        result = get_expiration_date_summary(df)
        assert result.loc[result['expiration_date'] == pd.to_datetime('2023-11-17').date(), 'marketValue_sum'].iloc[
                   0] == 300
        assert result.loc[result['expiration_date'] == pd.to_datetime('2023-11-17').date(), 'call_mark_perc'].iloc[
                   0] == 100 / 300

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = get_expiration_date_summary(df)
        assert result.empty

    def test_missing_values(self):
        data = {
            'instrument_symbol': ['CVX_111723C145', None],
            'marketValue': [100, None],
            'instrument_putCall': ['CALL', None]
        }
        df = pd.DataFrame(data)
        result = get_expiration_date_summary(df)
        assert not result.empty  # Depending on how you handle missing values, this assertion might change

    def test_result_format(self, sample_data):
        result = get_expiration_date_summary(sample_data)
        assert set(result.columns) == {'expiration_date', 'marketValue_sum', 'call_mark_perc',
                                       'instrument_putCall_count', 'call_vol_perc'}
        assert pd.api.types.is_object_dtype(result['expiration_date'])


class TestAmeritradeUtils(unittest.TestCase):

    # @patch('tools.ameritrade_helper.auth')
    # @patch('tools.ameritrade_helper.webdriver.Chrome')
    # def test_tda_auth_with_token_file(self, mock_chrome, mock_auth):
    #     # Set up the mock auth client
    #     mock_client = MagicMock()
    #     mock_auth.client_from_token_file.return_value = mock_client
    #
    #     # Call the function with the mock client
    #     actual_client = tda_auth('dummy-api-key')
    #
    #     # Assert that client_from_token_file was called with the right arguments
    #     mock_auth.client_from_token_file.assert_called_once_with('./token.json', 'dummy-api-key')
    #
    #     # Assert that client_from_login_flow and Chrome were not called
    #     mock_auth.client_from_login_flow.assert_not_called()
    #     mock_chrome.assert_not_called()
    #
    #     # Assert that the function returned the expected client
    #     self.assertEqual(actual_client, mock_client)

    # @patch('tools.ameritrade_helper.auth')
    # @patch('tools.ameritrade_helper.webdriver.Chrome')
    # def test_tda_auth_with_login_flow(self, mock_chrome, mock_auth):
    #     # Set up the mock auth client and mock Chrome
    #     mock_auth.client_from_token_file.side_effect = FileNotFoundError
    #     mock_client = MagicMock()
    #     mock_auth.client_from_login_flow.return_value = mock_client
    #
    #     # Call the function with the mock client and mock Chrome
    #     actual_client = tda_auth('dummy-api-key', chrome_driver_path='./../trading_platform/chromedriver')
    #
    #     # Assert that client_from_login_flow was called with the right arguments
    #     mock_auth.client_from_login_flow.assert_called_once_with(
    #         mock_chrome.return_value.__enter__.return_value, 'dummy-api-key', 'https://localhost:8895', './token.json')
    #
    #     # Assert that the function returned the expected client
    #     self.assertEqual(actual_client, mock_client)

    # @patch('tools.ameritrade_helper.tda_auth')
    # def test_get_quote(self, mock_tda_auth):
    #     # Set up the mock tda_auth client
    #     mock_client = MagicMock()
    #     mock_tda_auth.return_value = mock_client
    #
    #     # Mock the client's get_quote method
    #     expected_quote = {'symbol': 'AAPL', 'price': 150}
    #     mock_client.get_quote.return_value = expected_quote
    #
    #     # Call the function with the mock client
    #     actual_quote = get_quote('AAPL', 'dummy-api-key', tda_auth_func=mock_tda_auth)
    #
    #     # Assert that the client's get_quote method was called with the right arguments
    #     mock_client.get_quote.assert_called_once_with('AAPL')
    #
    #     # Assert that the function returned the expected quote
    #     self.assertEqual(actual_quote, expected_quote)

    @patch('tools.ameritrade_helper.get_quote')
    def test_verify_entry_success(self, mock_get_quote):
        # Mock successful response
        mock_response = MagicMock(spec=Response)
        mock_response.json.return_value = {'AAPL': {}}
        mock_get_quote.return_value = mock_response

        result = verify_entry('AAPL', 'tda_api_key')

        self.assertTrue(result)

    @patch('tools.ameritrade_helper.get_quote')
    def test_verify_entry_request_failure(self, mock_get_quote):
        # Simulate request failure
        mock_get_quote.side_effect = Exception("Request failed")

        result = verify_entry('AAPL', 'tda_api_key')

        self.assertFalse(result)

    @patch('tools.ameritrade_helper.get_quote')
    def test_verify_entry_json_failure(self, mock_get_quote):
        # Simulate JSON decoding failure
        mock_response = MagicMock(spec=Response)
        mock_response.json.side_effect = ValueError("Decoding JSON has failed")
        mock_get_quote.return_value = mock_response

        result = verify_entry('AAPL', 'tda_api_key')

        self.assertFalse(result)

    @patch('tools.ameritrade_helper.get_quote')
    def test_verify_entry_symbol_missing(self, mock_get_quote):
        # Mock successful response but with missing symbol
        mock_response = MagicMock(spec=Response)
        mock_response.json.return_value = {'MSFT': {}}
        mock_get_quote.return_value = mock_response

        result = verify_entry('AAPL', 'tda_api_key')

        self.assertFalse(result)

    @patch('tools.ameritrade_helper.tda_auth')
    def test_get_option_chain_with_strike(self, mock_tda_auth):
        mock_client = MagicMock()
        mock_tda_auth.return_value = mock_client
        mock_client.get_option_chain.return_value.json.return_value = {'data': 'dummy_data'}
        mock_client.Client.Options.ContractType.PUT = 'PUT'

        result = get_option_chain('AAPL', 'PUT', 'dummy_tda_api_key', tda_auth_func=mock_tda_auth, strike=150)

        mock_client.get_option_chain.assert_called_once_with('AAPL',
                                                             contract_type=client.Client.Options.ContractType.PUT,
                                                             strike=150)
        assert result.json() == {'data': 'dummy_data'}




# Mock the TD Ameritrade client object
@pytest.fixture
def mock_tda_client():
    with patch('tools.ameritrade_helper.client') as mock_client:
        yield mock_client

# Test tda_auth function
def test_tda_auth_token_file_exists():
    with patch('tools.ameritrade_helper.auth.client_from_token_file') as mock_auth:
        tda_auth(api_key='dummy_key', token_path='dummy_path')
        mock_auth.assert_called_with('dummy_path', 'dummy_key')

def test_tda_auth_token_file_not_found():
    with patch('tools.ameritrade_helper.auth.client_from_token_file', side_effect=FileNotFoundError):
        with pytest.raises(Exception):
            tda_auth(api_key='dummy_key', token_path='dummy_path')


# # Test get_quote function
# def test_get_quote(mock_tda_client):
#     # Setup mock response
#     mock_response = MagicMock()
#     mock_response.json.return_value = {'symbol': 'AAPL', 'price': 100}
#     mock_response.status_code = 200  # Set the status_code explicitly
#
#     mock_tda_client.return_value.get_quote.return_value = mock_response
#
#     # Call the function
#     result = get_quote('AAPL', tda_auth_func=lambda **kwargs: mock_tda_client)
#
#     # Assertions
#     assert result == {'symbol': 'AAPL', 'price': 100}
#     mock_tda_client.return_value.get_quote.assert_called_with('AAPL')

if __name__ == '__main__':
    unittest.main()
