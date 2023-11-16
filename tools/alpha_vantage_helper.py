def get_daily_adjusted_processed(data):
    """
    Processes the given DataFrame by reversing its order and adjusting the financial data
    columns based on the adjusted close price.

    The function renames the columns for clarity, calculates the adjustment ratio using the
    adjusted close and close prices, and applies this ratio to the open, high, and low prices.
    It also drops the 'adjusted_close' and 'split_coefficient' columns and returns the modified DataFrame.

    Args:
        data (DataFrame): The DataFrame containing stock market data. Expected columns include
                          '1. open', '2. high', '3. low', '4. close', '5. adjusted close',
                          '6. volume', '7. dividend amount', and '8. split coefficient'.

    Returns:
        DataFrame: The processed DataFrame with adjusted financial data.
    """
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
    """
        Finds the last crossover point in a given DataFrame based on the MACD Histogram (MACD_Hist) values.

        The function iterates through the DataFrame and checks for a crossover, identified when
        the product of MACD_Hist values for consecutive rows is less than or equal to zero.
        Once a crossover is found, the function returns the date of the last crossover.

        Args:
            df (DataFrame): The DataFrame containing financial data with a column named 'MACD_Hist'.

        Returns:
            last_crossover_date (datetime or None): The date of the last crossover, or None if no crossover is found.
        """
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
