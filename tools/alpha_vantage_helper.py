def get_daily_adjusted_processed(data):
    data = data.iloc[::-1]  # reverse order
    data = data.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. adjusted close': 'adjusted close',
        '6. volume': 'volume',
        '7. dividend amount': 'dividend amount',
        '8. split coefficient': 'split coefficient'
        })
    adjust_ratio = (data['adjusted close'] / data['close'])

    data['open'] = data['open'] * adjust_ratio
    data['high'] = data['high'] * adjust_ratio
    data['low'] = data['low'] * adjust_ratio
    data['close'] = data['adjusted close']
    data = data.drop(['adjusted close', 'split coefficient'], axis=1)

    return data
