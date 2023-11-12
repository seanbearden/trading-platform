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
