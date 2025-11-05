# (位於 stock_analyse_toolbox/k_line_plot.py)

import os
import mplfinance as mpf
import pandas as pd
import ta
import numpy as np

def plot_ohlc(data, ticker=None, xaxis_freq='auto', save_suffix='_ohlc'): # *** 修改 1: 增加 save_suffix ***
    """
    畫蠟燭圖並自動建立資料夾存圖
    xaxis_freq: 'auto', 'year', 'month', 'day'
    save_suffix: 儲存的檔案名稱後綴
    *** 新功能: 如果 data 中包含 'Signal' 欄位, 將自動繪製買賣點 ***
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

    # 確保資料型態正確
    ohlc_cols = ['Open','High','Low','Close','Volume']
    for col in ohlc_cols:
        if col in data.columns:
            data[col] = data[col].astype(float)
    data = data.dropna(subset=[col for col in ohlc_cols if col in data.columns])

    if data.empty:
        print("資料不足，無法繪製 OHLC")
        return

    # 計算 SMA/EMA/布林通道
    close = data['Close']
    data['SMA20'] = ta.trend.SMAIndicator(close=close, window=20).sma_indicator()
    data['EMA50'] = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    data['BB_high'] = bb.bollinger_hband()
    data['BB_low'] = bb.bollinger_lband()

    # addplot 前先檢查資料是否有效
    add_plots = []
    if data['SMA20'].notna().any():
        add_plots.append(mpf.make_addplot(data['SMA20'], color='blue', width=1, label='SMA20'))
    if data['EMA50'].notna().any():
        add_plots.append(mpf.make_addplot(data['EMA50'], color='red', width=1, label='EMA50'))
    if data['BB_high'].notna().any():
        add_plots.append(mpf.make_addplot(data['BB_high'], color='orange', linestyle='--', alpha=0.7, label='BB High'))
    if data['BB_low'].notna().any():
        add_plots.append(mpf.make_addplot(data['BB_low'], color='orange', linestyle='--', alpha=0.7, label='BB Low'))

    # ------------------------------------------------------------------
    # ***繪製買賣訊號 ***
    if 'Signal' in data.columns:
        # 找出訊號 "改變" 的那一天 (即交易發生的那天)
        
        # 買入: 訊號從 -1 或 0 變為 1
        buy_cond = (data['Signal'] == 1) & (data['Signal'].shift(1) != 1)
        # 賣出: 訊號從 1 變為 -1
        sell_cond = (data['Signal'] == -1) & (data['Signal'].shift(1) == 1)

        # 建立兩個新的 Series, 只在買賣點有值, 其他地方都是 NaN
        buy_markers = pd.Series(np.nan, index=data.index)
        sell_markers = pd.Series(np.nan, index=data.index)

        # 在 K 線的 "下方" 標記買入點
        buy_markers[buy_cond] = data['Low'][buy_cond] * 0.98 
        # 在 K 線的 "上方" 標記賣出點
        sell_markers[sell_cond] = data['High'][sell_cond] * 1.02

        # 加入 add_plots 列表
        if buy_markers.notna().any():
             add_plots.append(mpf.make_addplot(buy_markers, type='scatter', marker='^', color='g', markersize=150, label='Buy'))
        if sell_markers.notna().any():
            add_plots.append(mpf.make_addplot(sell_markers, type='scatter', marker='v', color='r', markersize=150, label='Sell'))
    # ------------------------------------------------------------------

    # *** 使用 save_suffix 來命名檔案 ***
    save_path = os.path.join(folder, f'{ticker}{save_suffix}.png')

    # 根據 xaxis_freq 決定日期格式
    if xaxis_freq == 'year':
        dt_format = '%Y'
    elif xaxis_freq == 'month':
        dt_format = '%Y-%m'
    elif xaxis_freq == 'day':
        dt_format = '%Y-%m-%d'
    else:
        dt_format = None # 讓 mplfinance 自動決定

    # 畫圖並存檔
    mpf.plot(
        data,
        type='candle',
        style='charles',
        title=f'{ticker} OHLC Chart ({save_suffix.strip("_")})', 
        ylabel='Price',
        volume=True,
        addplot=add_plots,
        figsize=(14,7),
        tight_layout=True,
        warn_too_much_data=10000,
        show_nontrading=False,
        datetime_format=dt_format,
        xrotation=15,
        savefig=save_path
    )

    print(f"Saved OHLC chart with signals to {save_path}")