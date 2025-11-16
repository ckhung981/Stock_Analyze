import os
import mplfinance as mpf
import pandas as pd
import ta
import numpy as np

def plot_ohlc(data, ticker=None, xaxis_freq='auto', save_suffix='_ohlc', 
              strategy_indicators=[], **kwargs): # *** 修改 1: 增加 new_argument ***
    """
    畫蠟燭圖、買賣點、並在下方加入指定的技術指標子圖 (Panel)
    
    Args:
        data (pd.DataFrame): 必須包含 Open, High, Low, Close, Volume.
                             可選: Signal (用於買賣點), RSI, MACD...
        ticker (str, optional): 股票代碼.
        xaxis_freq (str, optional): X 軸頻率 ('auto', 'year', 'month', 'day').
        save_suffix (str, optional): 儲存的檔案名稱後綴.
        strategy_indicators (list, optional): 要在 K 線圖下方額外繪製的指標列表.
                                             支援: ['RSI', 'MACD', 'KD']
    """
    
    # --- 1. 資料準備 (與您原先的程式碼相同) ---
    if ticker is None:
        ticker = getattr(data, 'ticker', 'UNKNOWN')

    folder = os.path.join('output', ticker)
    os.makedirs(folder, exist_ok=True)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    ohlc_cols = ['Open','High','Low','Close','Volume']
    for col in ohlc_cols:
        if col in data.columns:
            data[col] = data[col].astype(float)
    data = data.dropna(subset=[col for col in ohlc_cols if col in data.columns])

    if data.empty:
        print("資料不足，無法繪製 OHLC")
        return

    # --- 2. 準備 add_plots 列表 (K線圖上的疊圖) ---
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']
    
    add_plots = []
    
    # 2a. 計算 SMA / EMA / BB (疊加在 K 線圖上, panel=0)
    data['SMA20'] = ta.trend.SMAIndicator(close=close, window=20).sma_indicator()
    data['EMA50'] = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    data['BB_high'] = bb.bollinger_hband()
    data['BB_low'] = bb.bollinger_lband()

    if data['SMA20'].notna().any():
        add_plots.append(mpf.make_addplot(data['SMA20'], color='blue', width=1, label='SMA20', panel=0))
    if data['EMA50'].notna().any():
        add_plots.append(mpf.make_addplot(data['EMA50'], color='red', width=1, label='EMA50', panel=0))
    if data['BB_high'].notna().any():
        add_plots.append(mpf.make_addplot(data['BB_high'], color='orange', linestyle='--', alpha=0.7, label='BB High', panel=0))
    if data['BB_low'].notna().any():
        add_plots.append(mpf.make_addplot(data['BB_low'], color='orange', linestyle='--', alpha=0.7, label='BB Low', panel=0))

    # 2b. 繪製買賣訊號 (疊加在 K 線圖上, panel=0)
    if 'Signal' in data.columns:
        buy_cond = (data['Signal'] == 1) & (data['Signal'].shift(1) != 1)
        sell_cond = (data['Signal'] == -1) & (data['Signal'].shift(1) == 1)
        buy_markers = pd.Series(np.nan, index=data.index)
        sell_markers = pd.Series(np.nan, index=data.index)
        buy_markers[buy_cond] = data['Low'][buy_cond] * 0.98 
        sell_markers[sell_cond] = data['High'][sell_cond] * 1.02

        if buy_markers.notna().any():
             add_plots.append(mpf.make_addplot(buy_markers, type='scatter', marker='^', color='g', markersize=150, label='Buy', panel=0))
        if sell_markers.notna().any():
            add_plots.append(mpf.make_addplot(sell_markers, type='scatter', marker='v', color='r', markersize=150, label='Sell', panel=0))

            
    # --- 3. 準備子圖指標 (Indicators in new panels) ---
    
    # K 線圖佔 3 份高度
    panel_ratios = [3] 
    
    # Volume 預設會放在 panel 1
    # 我們讓 Volume 佔 1 份高度
    panel_ratios.append(1)
    
    # 指標從 panel 2 開始
    current_panel = 2 

    for ind in strategy_indicators:
        if ind == 'RSI':
            # --- 從 kwargs 獲取參數，如果沒有就用預設值 ---
            period = kwargs.get('period', 14)
            overbought = kwargs.get('overbought', 70)
            oversold = kwargs.get('oversold', 30)
            # ----------------------------------------
            
            # ** 關鍵 **: 優先使用 data 中已有的 'RSI' (來自 strategy)
            if 'RSI' not in data.columns:
                print(f"Warning: Calculating RSI using 'ta' (SMA-based) with period={period}.")
                # 修正: 確保使用 data['Close']
                data['RSI'] = ta.momentum.RSIIndicator(close=data['Close'], window=period).rsi() 

            rsi_ylabel = f"RSI({period})\n{overbought} (OB)\n{oversold} (OS)"
           # --- 3. (新功能) 繪製 RSI 主線條 + 強制 Y 軸 ---
            # 1. 加上 ylim 來強制 Y 軸範圍 0-100
            # 2. 替換 ylabel 
            add_plots.append(mpf.make_addplot(
                data['RSI'], 
                panel=current_panel, 
                ylabel=rsi_ylabel,  # <-- 使用新的動態標籤
                color='purple',
                ylim=(0, 100)      # <-- 新增: 強制 Y 軸範圍
            ))
            
            # --- 4. (新功能) 繪製動態的水平線 + 強制 Y 軸 ---
            # 這裡也加上 ylim=(0, 100) 是為了確保 Y 軸在所有 plot 之間保持一致
            add_plots.append(mpf.make_addplot(
                pd.Series(overbought, index=data.index), 
                panel=current_panel, 
                color='red', 
                linestyle='--', 
                alpha=0.7,
                ylim=(0, 100)      # <-- 新增: 保持 Y 軸一致
            ))
            add_plots.append(mpf.make_addplot(
                pd.Series(oversold, index=data.index), 
                panel=current_panel, 
                color='green', 
                linestyle='--', 
                alpha=0.7,
                ylim=(0, 100)      # <-- 新增: 保持 Y 軸一致
            ))
            
            panel_ratios.append(1) # RSI 佔 1 份高度
            current_panel += 1

        elif ind == 'MACD':
            if 'MACD' not in data.columns:
                print("Warning: Calculating MACD using 'ta'.")
                macd = ta.trend.MACD(close)
                data['MACD'] = macd.macd()
                data['MACD_signal'] = macd.macd_signal()
                data['MACD_hist'] = macd.macd_diff()

            # 將 MACD 畫在新的 panel 上
            add_plots.append(mpf.make_addplot(data['MACD'], panel=current_panel, ylabel='MACD', color='blue', label='MACD'))
            add_plots.append(mpf.make_addplot(data['MACD_signal'], panel=current_panel, color='red', linestyle='--', label='Signal'))
            # 繪製柱狀圖
            add_plots.append(mpf.make_addplot(data['MACD_hist'], type='bar', panel=current_panel, color='gray', alpha=0.4, label='Hist'))
            
            panel_ratios.append(1) # MACD 佔 1 份高度
            current_panel += 1
            
        elif ind == 'KD':
            if '%K' not in data.columns or '%D' not in data.columns:
                print("Warning: Calculating KD using 'ta'.")
                stoch = ta.momentum.StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
                data['%K'] = stoch.stoch()
                data['%D'] = stoch.stoch_signal()
                
            # 將 KD 畫在新的 panel 上
            add_plots.append(mpf.make_addplot(data['%K'], panel=current_panel, ylabel='KD', color='blue', label='%K'))
            add_plots.append(mpf.make_addplot(data['%D'], panel=current_panel, color='orange', label='%D'))
            # 加上 80 / 20 水平線
            add_plots.append(mpf.make_addplot(pd.Series(80, index=data.index), panel=current_panel, color='red', linestyle='--', alpha=0.7))
            add_plots.append(mpf.make_addplot(pd.Series(20, index=data.index), panel=current_panel, color='green', linestyle='--', alpha=0.7))
            
            panel_ratios.append(1) # KD 佔 1 份高度
            current_panel += 1

    # --- 4. 繪圖 (mpf.plot) ---
    save_path = os.path.join(folder, f'{ticker}{save_suffix}.png')

    if xaxis_freq == 'year': dt_format = '%Y'
    elif xaxis_freq == 'month': dt_format = '%Y-%m'
    elif xaxis_freq == 'day': dt_format = '%Y-%m-%d'
    else: dt_format = None 

    mpf.plot(
        data,
        type='candle',
        style='charles',
        title=f'{ticker} Chart ({save_suffix.strip("_")})',
        ylabel='Price',
        volume=True,  # 啟用 Volume, 它會自動佔用 panel 1
        addplot=add_plots,
        figsize=(14, 4 + 2 * len(strategy_indicators)), # 動態調整高度
        tight_layout=True,
        warn_too_much_data=10000,
        show_nontrading=False,
        datetime_format=dt_format,
        xrotation=15,
        savefig=save_path,
        panel_ratios=tuple(panel_ratios) # *** 修改 2: 傳入 panel 比例 ***
    )

    print(f"Saved OHLC chart with indicators to {save_path}")