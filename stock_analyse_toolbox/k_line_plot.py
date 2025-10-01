import os
import mplfinance as mpf
import pandas as pd
import ta

def plot_ohlc(data, ticker=None):
    """
    畫蠟燭圖並自動建立資料夾存圖
    data: yf.download 回傳的 DataFrame
    ticker: 股票代號，若為 None，從 data.columns 或其他方式自動判斷
    """
    # 自動判斷 ticker
    if ticker is None:
        ticker = getattr(data, 'ticker', 'UNKNOWN')

    # 建立輸出資料夾
    folder = os.path.join('output', ticker)
    os.makedirs(folder, exist_ok=True)

    # MultiIndex 轉單層
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # OHLC + Volume
    ohlc_cols = ['Open','High','Low','Close','Volume']
    data[ohlc_cols] = data[ohlc_cols].astype(float)
    data = data.dropna(subset=ohlc_cols)

    # 計算 SMA/EMA/布林通道
    close = data['Close']
    data['SMA20'] = ta.trend.SMAIndicator(close=close, window=20).sma_indicator()
    data['EMA50'] = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    data['BB_high'] = bb.bollinger_hband()
    data['BB_low'] = bb.bollinger_lband()

    # addplot
    add_plots = [
        mpf.make_addplot(data['SMA20'], color='blue', width=1, label='SMA20'),
        mpf.make_addplot(data['EMA50'], color='red', width=1, label='EMA50'),
        mpf.make_addplot(data['BB_high'], color='orange', linestyle='--', alpha=0.7, label='BB High'),
        mpf.make_addplot(data['BB_low'], color='orange', linestyle='--', alpha=0.7, label='BB Low')
    ]

    save_path = os.path.join(folder, f'{ticker}_ohlc.png')

    # 畫圖並存檔
    mpf.plot(
        data,
        type='candle',
        style='charles',
        title=f'{ticker} OHLC Candlestick Chart',
        ylabel='Price',
        volume=True,
        addplot=add_plots,
        figsize=(14,7),
        tight_layout=True,
        warn_too_much_data=10000,
        show_nontrading=False,
        savefig=save_path
    )

    print(f"Saved OHLC chart to {save_path}")
