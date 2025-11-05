
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from stock_analyse_toolbox import back_tester,k_line_plot,indicator_plot,strategies

Ticker = '2330.tw'
data = yf.download(Ticker, start='2019-07-04', end='2025-11-4', interval="1d")
if data.empty:
    raise ValueError(f"No data downloaded for {Ticker}")

# 建立回測器
bt = back_tester.Backtester(data, initial_cash=100000, transaction_fee=0.001425)

# 執行策略
result = bt.run(strategies.rsi_strategy, 
                period=14, 
                oversold=30, 
                overbought=70)

# --- 繪製資產淨值圖---
plt.figure(figsize=(12,6))
plt.title(f'{Ticker} Portfolio Value (RSI Strategy)')
plt.plot(result['Portfolio'], label="Portfolio Value")
plt.show()

# --- 繪製 K 線圖 (包含買入、賣出點)---
k_line_plot.plot_ohlc(result, 
          ticker=Ticker, 
          xaxis_freq='day', 
          save_suffix='_rsi_strategy_trades')

# --- 輸出報告 ---
print(bt.summary())