import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from stock_analyse_toolbox.k_line_plot import plot_ohlc
from stock_analyse_toolbox.indicator_plot import plot_indicators
from stock_analyse_toolbox.back_tester import Backtester
import stock_analyse_toolbox.strategies as strategies

Ticker = '2330.TW'
# 下載資料
data = yf.download(Ticker, start='2019-07-04', end='2024-07-16', interval="1d")
if data.empty:
    raise ValueError(f"No data downloaded for {Ticker}")

# 畫K線圖
# plot_ohlc(data, ticker=Ticker, xaxis_freq='day')

# 畫技術指標
# plot_indicators(data, ticker=Ticker, indicators_to_plot=['RSI','OBV','KD'], xaxis_freq='day')

# 建立回測器
bt = Backtester(data, initial_cash=100000, transaction_fee=0.001425)  # 使用預設費率
result = bt.run(strategies.moving_average_strategy, short=10, long=30)
result = bt.run(strategies.moving_average_strategy, short=10, long=30)

# 畫圖
plt.figure(figsize=(12,6))

plt.plot(result['Portfolio'], label="Portfolio Value")
buys = result[result['Signal'] == 1].index
sells = result[result['Signal'] == -1].index
plt.scatter(buys, result.loc[buys, 'Close'], marker='^', color='g', label='Buy', s=100)
plt.scatter(sells, result.loc[sells, 'Close'], marker='v', color='r', label='Sell', s=100)
plt.legend()
plt.show()

# 輸出報告
print(bt.summary())