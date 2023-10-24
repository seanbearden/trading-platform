from dotenv import load_dotenv
from io import StringIO
import os
import pandas as pd

from tools.finviz_helper import get_screener
import unittest
from unittest.mock import patch, Mock

load_dotenv()


class TestFinvizUtils(unittest.TestCase):

    def setUp(self):
        self.api_token = "test_token"
        self.layout = "Overview"
        self.expected_url = f"https://elite.finviz.com/export.ashx?v={self.layout}&auth={self.api_token}"

    @patch('requests.get')
    def test_get_screener_successful_response(self, mock_get):
        # Mocking a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'success'
        mock_get.return_value = mock_response

        response = get_screener(self.api_token, self.filters)

        mock_get.assert_called_once_with(self.expected_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'success')

    @patch('requests.get')
    def test_get_screener_error_response(self, mock_get):
        # Mocking an error response (e.g., 404)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'not found'
        mock_get.return_value = mock_response

        response = get_screener(self.api_token, self.filters)

        mock_get.assert_called_once_with(self.expected_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'not found')

    def test_get_screener_layouts(self):
        symbols = ['AAPL', 'META', 'AMZN', 'GOOGL', 'TSLA']
        layouts = ['Overview', 'Valuation', 'Financial', 'Ownership', 'Performance', 'Technical', 'Custom']
        for layout in layouts:
            response = get_screener(os.getenv('FINVIZ_API_KEY'), layout=layout, symbols=symbols, sleep_secs=2)
            data_str = response.text

            # Using StringIO to convert the string data to a file-like object so it can be read into a pandas DataFrame
            data_io = StringIO(data_str)

            # Reading the data into a pandas DataFrame
            df = pd.read_csv(data_io)
            for ticker in df['Ticker']:
                self.assertIn(ticker, symbols)


if __name__ == '__main__':
    unittest.main()
