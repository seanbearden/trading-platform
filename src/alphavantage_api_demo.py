import requests
import pandas as pd
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
from dotenv import dotenv_values
from utils.IchimokuCloud import IchimokuCloud
env_dict = dotenv_values()

# Alpha Vantage API URL for daily adjusted data
url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={apikey}".format(
    symbol='SEDG',
    apikey=env_dict['ALPHAVANTAGE_API_KEY']
)

# Send GET request
response = requests.get(url)

# Convert the response to JSON
data = response.json()

# Get the daily adjusted time series data
daily_adjusted = data['Time Series (Daily)']

# Convert to a pandas DataFrame
df = pd.DataFrame.from_dict(daily_adjusted).T

# Convert the index to datetime
df.index = pd.to_datetime(df.index)

# Sort the DataFrame by date
df = df.sort_index()

# Convert columns to floats
for col in df.columns:
    df[col] = df[col].astype(float)

# # Create a new column of formatted dates
# df['date_fmt'] = df.index.map(mpl_dates.date2num)

# # Create a new DataFrame of OHLC data
# ohlc = df[['date_fmt', '1. open', '2. high', '3. low', '4. close']]
#
# # Create a candlestick chart
# fig, ax = plt.subplots()
#
# candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='g', colordown='r', alpha=0.8)
#
# # Format the x-ticks to display the date
# date_format = mpl_dates.DateFormatter('%d-%m-%Y')
# ax.xaxis.set_major_formatter(date_format)
#
# fig.autofmt_xdate()
#
# plt.show()


# Calculate Ichimoku Cloud indicators
ichimoku = IchimokuCloud(df=df)
df = ichimoku.calculate_ichimoku_cloud()

# Create a new column of formatted dates
df['date_fmt'] = df.index.map(mpl_dates.date2num)

# Create a new DataFrame of OHLC data
ohlc = df[['date_fmt', '1. open', '2. high', '3. low', '4. close']]

# Create a candlestick chart
fig, ax = plt.subplots()

candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='g', colordown='r', alpha=0.8)

# Plot Ichimoku Cloud indicators
ax.plot(df.index, df['tenkan_sen'], label='Tenkan-sen (Conversion)', color='blue')
ax.plot(df.index, df['kijun_sen'], label='Kijun-sen (Base)', color='red')
ax.plot(df.index, df['chikou_span'], label='Chikou Span (Lagging)', color='orange')

# Plot Ichimoku Cloud
ax.fill_between(df.index, df['senkou_span_a'], df['senkou_span_b'], where=df['senkou_span_a'] >= df['senkou_span_b'], color='lightgreen', alpha=0.5)
ax.fill_between(df.index, df['senkou_span_a'], df['senkou_span_b'], where=df['senkou_span_a'] < df['senkou_span_b'], color='lightcoral', alpha=0.5)

# Format the x-ticks to display the date
date_format = mpl_dates.DateFormatter('%d-%m-%Y')
ax.xaxis.set_major_formatter(date_format)

fig.autofmt_xdate()
plt.legend()

plt.show()
