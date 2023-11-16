import numpy as np
from scipy.signal import argrelextrema


def calculate_ichimoku(df):
    """
    Calculates the Ichimoku Cloud indicator components for a given DataFrame.

    This function computes the Tenkan-sen, Kijun-sen, Senkou Span A, Senkou Span B, and Chikou Span
    for each row in the DataFrame. The DataFrame must contain 'high', 'close', and 'low' columns.

    Args:
        df (DataFrame): A pandas DataFrame with columns 'high', 'close', and 'low'.

    Returns:
        DataFrame: The input DataFrame with new columns added for each Ichimoku component:
                   'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', and 'chikou_span'.
    """
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


def identify_multi_tops(data, tolerance=0.005, order=1):
    """
    Identifies potential multi-top formations in a given dataset.

    This function finds local maxima (potential tops) in the dataset based on the close and open prices.
    It then evaluates these tops to determine if they form a multi-top pattern based on the specified tolerance.

    Args:
        data (DataFrame): A pandas DataFrame with at least 'close' and 'open' columns.
        tolerance (float, optional): The tolerance level used to identify additional touches to the resistance. Defaults to 0.005.
        order (int, optional): The order parameter for the argrelextrema function. Defaults to 1.

    Returns:
        tuple: A tuple containing the indices of touches and the average resistance value if a multi-top is identified,
               otherwise (None, None).
    """
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


def identify_multi_bottoms(data, tolerance=0.005, order=1):
    """
    Identifies potential multi-bottom formations in a given dataset.

    This function finds local minima (potential bottoms) in the dataset based on the close and open prices.
    It then evaluates these bottoms to determine if they form a multi-bottom pattern based on the specified tolerance.

    Args:
        data (DataFrame): A pandas DataFrame with at least 'close' and 'open' columns.
        tolerance (float, optional): The tolerance level used to identify additional touches to the support. Defaults to 0.005.
        order (int, optional): The order parameter for the argrelextrema function. Defaults to 1.

    Returns:
        tuple: A tuple containing the indices of touches and the average support value if a multi-bottom is identified,
               otherwise (None, None).
    """
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
