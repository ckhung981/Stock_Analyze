import yfinance as yf
from stock_analyse_toolbox.k_line_plot import plot_ohlc
from stock_analyse_toolbox.indicator_plot import plot_indicators
Ticker='2330.TW'
# 下載資料
data = yf.download(Ticker, start='2015-01-01', end='2025-09-30', interval="1d")

# 畫K線圖
plot_ohlc(data, ticker=Ticker)

# 畫技術指標 (使用者可以選擇要畫哪些)
plot_indicators(data, ticker=Ticker, indicators_to_plot=['RSI','MACD','OBV'])
# 或只畫 RSI 和 OBV
# plot_indicators(data, indicators_to_plot=['RSI','OBV'])
