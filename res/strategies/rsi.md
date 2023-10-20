# RSI Trading Strategy

The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements. RSI oscillates between zero and 100. Traditionally and according to Wilder, RSI is considered overbought when above 70 and oversold when below 30. Below is a detailed strategy using the RSI indicator:

## 1. **Setting up RSI on the Chart:**

- Choose an RSI period such as the standard 14 periods.
- Identify the overbought (usually 70) and oversold (usually 30) levels.

```plaintext
RSI Period: 14
Overbought Level: 70
Oversold Level: 30
```

## 2. **Basic Signals:**

### a. Buy Signal:

- **Oversold Condition:** Buy when the RSI drops below 30 and then rises back above it.
- **Positive Divergence:** Buy when the price makes a new low, but the RSI makes a higher low.

```plaintext
if (RSI < 30 and RSI is increasing) or (Price is at new low and RSI is at higher low) then Buy
```

### b. Sell Signal:

- **Overbought Condition:** Sell when the RSI rises above 70 and then falls back below it.
- **Negative Divergence:** Sell when the price makes a new high, but the RSI makes a lower high.

```plaintext
if (RSI > 70 and RSI is decreasing) or (Price is at new high and RSI is at lower high) then Sell
```

## 3. **Confirmation:**

- Look for confirmation from other indicators or price patterns before entering a trade based on RSI signals.

## 4. **Swing Failure Signal (SFS):**

- **Bullish SFS:** When RSI breaks above a previous high but quickly falls back down, it might indicate a bullish trend.
- **Bearish SFS:** When RSI breaks below a previous low but quickly rises back up, it might indicate a bearish trend.

## 5. **Risk Management:**

- Setting stop losses and take profit levels to manage risks effectively.
- It's advisable not to risk more than 1-2% of trading capital on a single trade.

## 6. **Backtesting:**

- Backtest the RSI strategy on historical data to understand its effectiveness and to fine-tune its parameters.

## 7. **Additional Tips:**

- It's essential to trade with the trend to increase the odds of success.
- Patience and discipline are crucial to wait for high-probability setups based on the RSI indicator.

This trading strategy encapsulates the basics of trading with the RSI indicator. Just like with any trading strategy, it's essential to understand that there will be losses and the aim is to have the gains outperform the losses over time.