# import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt


def calculate_ichimoku(df):
    df['date'] = pd.to_datetime(df.index)
    df.index = pd.to_datetime(df['date'])
    high_prices = df['high']
    close_prices = df['close']
    low_prices = df['low']
    nine_period_high = high_prices.rolling(window=9).max()
    nine_period_low = low_prices.rolling(window=9).min()
    df['tenkan_sen'] = (nine_period_high + nine_period_low) / 2
    twenty_six_period_high = high_prices.rolling(window=26).max()
    twenty_six_period_low = low_prices.rolling(window=26).min()
    df['kijun_sen'] = (twenty_six_period_high + twenty_six_period_low) / 2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    fifty_two_period_high = high_prices.rolling(window=52).max()
    fifty_two_period_low = low_prices.rolling(window=52).min()
    df['senkou_span_b'] = ((fifty_two_period_high + fifty_two_period_low) / 2).shift(26)
    df['chikou_span'] = close_prices.shift(-26)
    return df
