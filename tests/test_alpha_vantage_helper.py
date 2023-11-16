import pandas as pd
import pytest
from tools.alpha_vantage_helper import get_daily_adjusted_processed, find_last_crossover

# Sample data for testing
sample_data = {
    '1. open': [100, 102, 101],
    '2. high': [105, 103, 102],
    '3. low': [99, 98, 97],
    '4. close': [102, 100, 99],
    '5. adjusted close': [104, 102, 100],
    '6. volume': [1000, 2000, 1500],
    '7. dividend amount': [0.5, 0.3, 0.4],
    '8. split coefficient': [1, 1, 1]
}

# Sample MACD_Hist data for crossover test
macd_data = {
    'MACD_Hist': [-0.1, -0.2, 0.2, -0.2, -0.1]
}


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(sample_data)


@pytest.fixture
def macd_dataframe():
    return pd.DataFrame(macd_data, index=pd.date_range(start='2020-01-01', periods=5)).loc[::-1]


class TestFinancialFunctions:
    def test_get_daily_adjusted_processed(self, sample_dataframe):
        adjusted_df = get_daily_adjusted_processed(sample_dataframe.copy())

        # Verify that the DataFrame is processed correctly
        assert 'adjusted_close' not in adjusted_df.columns
        assert 'split_coefficient' not in adjusted_df.columns
        assert all(adjusted_df['open'] == (sample_dataframe['1. open'] * (
                    sample_dataframe['5. adjusted close'] / sample_dataframe['4. close'])).loc[::-1])

    def test_find_last_crossover(self, macd_dataframe):
        crossover_date = find_last_crossover(macd_dataframe)

        # Verify that the correct crossover date is found
        assert crossover_date == macd_dataframe.index[1]  # Based on the sample data
        # Add more assertions to test different scenarios
