
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import stock_analyse_toolbox as sat

Ticker = 'NVDA'
data = yf.download(Ticker, start='2021-07-04', end='2025-11-5', interval="1d")
if data.empty:
    raise ValueError(f"No data downloaded for {Ticker}")

strategy_params = {
    'period': 21, 
    'oversold': 45, 
    'overbought': 55
}
# 建立回測器
bt = sat.back_tester.Backtester(data, initial_cash=100000, transaction_fee=0.001425)

# 執行 RSI 策略
result = bt.run(sat.strategies.rsi_strategy, **strategy_params)

'''
# 執行 KD 策略
result = bt.run(sat.strategies.kd_strategy, 
                period=14, 
                smooth_window=3)
'''
# --- 繪製投資組合淨值圖 ---
plt.figure(figsize=(12,6))
plt.title(f'{Ticker} Portfolio Value')
plt.plot(result['Portfolio'], label="Portfolio Value")
plt.legend()
plt.show() 

# --- 繪製 K 線圖 + RSI 子圖 ---
sat.k_line_plot.plot_ohlc(result, 
          ticker=Ticker, 
          xaxis_freq='day', 
          save_suffix='_rsi_strategy_chart',
          strategy_indicators=['RSI'],
          **strategy_params) 

# 如果你想同時看 RSI 和 MACD, 傳入:
# strategy_indicators=['RSI', 'MACD']

# --- 輸出報告 ---
print(bt.summary())