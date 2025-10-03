import yfinance as yf
from stock_analyse_toolbox.k_line_plot import plot_ohlc
from stock_analyse_toolbox.indicator_plot import plot_indicators
Ticker='2330.TW'
# 下載資料
data = yf.download(Ticker, start='2024-07-04', end='2024-07-16', interval="1d")

print(data)
if data.empty:
    print("資料為空，無法畫圖")
required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
for col in required_cols:
    if col not in data.columns:
        print(f"缺少欄位: {col}")

# 畫K線圖
plot_ohlc(data, ticker=Ticker, xaxis_freq='day')

# 畫技術指標 (使用者可以選擇要畫哪些)
plot_indicators(data, ticker=Ticker, indicators_to_plot=['RSI','OBV','KD'], xaxis_freq='day')
# 或只畫 RSI 和 OBV
# plot_indicators(data, indicators_to_plot=['RSI','OBV'])
