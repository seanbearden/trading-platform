import numpy as np
from scipy.signal import argrelextrema


def calculate_ichimoku(df):
    # df['date'] = pd.to_datetime(df.index)
    # df.index = pd.to_datetime(df['date'])
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


# Function to identify local maxima
def identify_multi_tops(data, tolerance=0.005, order=1):
    data_close = data['close']
    data_open = data['open']
    # Finding local maxima based on adjusted close and adjusted open
    local_maxima = argrelextrema(np.maximum(data_close.values, data_open.values), np.greater, order=order)[0]

    if len(local_maxima) < 2:
        return None, None

    top_indices = local_maxima[np.argsort(np.maximum(data_close.values[local_maxima], data_open.values[local_maxima]))[-2:]]
    resistance_value = np.maximum(data_close.values[top_indices], data_open.values[top_indices]).mean()

    # Check for additional touches
    touches = [idx for idx in local_maxima if abs(np.maximum(data_close.values[idx], data_open.values[idx]) -
                                                             resistance_value) / resistance_value <= tolerance]
    if len(touches) < 2:
        return None, None

    return touches, resistance_value


# Function to identify local minima
def identify_multi_bottoms(data, tolerance=0.005, order=1):
    data_close = data['close']
    data_open = data['open']
    # Finding local minima based on adjusted close and adjusted open
    local_minima = argrelextrema(
        np.minimum(data_close.values, data_open.values),
        np.less,
        order=order
    )[0]

    if len(local_minima) < 2:
        return None, None

    bottom_indices = local_minima[np.argsort(
        np.minimum(data_close.values[local_minima], data_open.values[local_minima]))[:2]]
    support_value = np.minimum(data_close.values[bottom_indices],
                               data_open.values[bottom_indices]).mean()

    # Check for additional touches
    touches = [idx for idx in local_minima if abs(np.minimum(data_close.values[idx], data_open.values[idx]) - support_value) /
               support_value <= tolerance]

    if len(touches) < 2:
        return None, None

    return touches, support_value
