"""Util that calls AlphaVantage for Daily Adjusted Time Series."""
from typing import Any, Dict, Optional

import requests

from langchain.pydantic_v1 import BaseModel, Extra, root_validator
from langchain.utils import get_from_dict_or_env


class AlphaVantageDailyAdjustedAPIWrapper(BaseModel):
    """Wrapper for AlphaVantage API for Daily Adjusted Time Series.

    Docs for using:

    1. Go to AlphaVantage and sign up for an API key
    2. Save your API KEY into ALPHAVANTAGE_API_KEY env variable
    """

    alphavantage_api_key: Optional[str] = None

    class Config:
        extra = Extra.forbid

    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        values["alphavantage_api_key"] = get_from_dict_or_env(
            values, "alphavantage_api_key", "ALPHAVANTAGE_API_KEY"
        )
        return values

    def _get_daily_adjusted(
            self, symbol: str, outputsize: Optional[str] = "compact", datatype: Optional[str] = "json"
    ) -> Dict[str, Any]:
        """Make a request to the AlphaVantage API to get the daily adjusted time series."""
        response = requests.get(
            "https://www.alphavantage.co/query/",
            params={
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol,
                "outputsize": outputsize,
                "datatype": datatype,
                "apikey": self.alphavantage_api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")

        return data

    def run(self, symbol: str, outputsize: Optional[str] = "compact", datatype: Optional[str] = "json") -> str:
        """Get the daily adjusted time series for a specified equity symbol."""
        data = self._get_daily_adjusted(symbol, outputsize, datatype)
        return data


def get_daily_adjusted_processed(data):
    data = data.iloc[::-1]  # reverse order
    data = data.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. adjusted close': 'adjusted_close',
        '6. volume': 'volume',
        '7. dividend amount': 'dividend_amount',
        '8. split coefficient': 'split_coefficient'
    })
    adjust_ratio = (data['adjusted_close'] / data['close'])

    data['open'] = data['open'] * adjust_ratio
    data['high'] = data['high'] * adjust_ratio
    data['low'] = data['low'] * adjust_ratio
    data['close'] = data['adjusted_close']
    data = data.drop(['adjusted_close', 'split_coefficient'], axis=1)

    return data


def find_last_crossover(df):
    last_crossover_date = None
    trend = None
    for idx in range(len(df) - 1):
        current_row = df.iloc[idx]
        previous_row = df.iloc[idx + 1]
        # Check for crossover. Identify touch as crossover (MACD_Hist = 0)
        if current_row['MACD_Hist'] * previous_row['MACD_Hist'] <= 0:
            last_crossover_date = current_row.name
            break  # Exit the loop once a crossover is found

    return last_crossover_date
