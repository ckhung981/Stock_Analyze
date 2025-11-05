
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import stock_analyse_toolbox as sat

Ticker = '2330.TW'
data = yf.download(Ticker, start='2024-07-04', end='2025-11-4', interval="1d")
if data.empty:
    raise ValueError(f"No data downloaded for {Ticker}")

# 建立回測器
bt = sat.back_tester.Backtester(data, initial_cash=100000, transaction_fee=0.001425)

# 執行 RSI 策略
result = bt.run(sat.strategies.rsi_strategy, 
                period=14, 
                oversold=30, 
                overbought=70)

# --- 繪製投資組合淨值圖 ---
plt.figure(figsize=(12,6))
plt.title(f'{Ticker} Portfolio Value (RSI Strategy)')
plt.plot(result['Portfolio'], label="Portfolio Value")
plt.legend()
plt.show() 

# --- 繪製 K 線圖 + RSI 子圖 ---
sat.k_line_plot.plot_ohlc(result, 
          ticker=Ticker, 
          xaxis_freq='day', 
          save_suffix='_rsi_strategy_chart', 
          strategy_indicators=['RSI']) 

# 如果你想同時看 RSI 和 MACD, 傳入:
# strategy_indicators=['RSI', 'MACD']

# --- 輸出報告 ---
print(bt.summary())