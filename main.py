import yfinance as yf
from stock_analyse_toolbox.k_line_plot import plot_ohlc
from stock_analyse_toolbox.indicator_plot import plot_indicators
Ticker='0050.TW'
# 下載資料
data = yf.download(Ticker, start='2025-01-01', end='2025-10-03', interval="1d")

# 畫K線圖
plot_ohlc(data, ticker=Ticker, xaxis_freq='month')

# 畫技術指標 (使用者可以選擇要畫哪些)
plot_indicators(data, ticker=Ticker, indicators_to_plot=['RSI','MACD','OBV'], xaxis_freq='month')
# 或只畫 RSI 和 OBV
# plot_indicators(data, indicators_to_plot=['RSI','OBV'])
