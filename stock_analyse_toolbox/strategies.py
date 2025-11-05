import pandas as pd
import numpy as np 

def moving_average_strategy(data, short=10, long=30):
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data index must be DatetimeIndex")
    if isinstance(data.columns, pd.MultiIndex):
        data.copy()
        data.columns = [col[0] for col in data.columns]
    
    short_ma = data['Close'].rolling(short).mean()
    long_ma = data['Close'].rolling(long).mean()

    signals = pd.Series(0, index=data.index, dtype=int)
    signals.loc[short_ma > long_ma] = 1
    signals.loc[short_ma < long_ma] = -1
    signals = signals.fillna(0).astype(int) # 處理 NaN
    return signals


def rsi_strategy(data, period=14, overbought=70, oversold=30):
    """
    RSI 策略 (使用 Wilder's EWM 和 Crossover 邏輯)
    訊號：
    1: 買入/持有 (RSI 向上穿越 oversold)
    -1: 賣出/空手 (RSI 向下穿越 overbought)
    """
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = [col[0] for col in data.columns]
    
    # --- 1. 使用 Wilder's EWM 計算標準 RSI ---
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # 使用 ewm (Exponential Moving Average) 
    # com=period-1 等同於 Wilder's smoothing (alpha = 1/period)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    # 處理 avg_loss 為 0 的情況
    rs = avg_gain / avg_loss
    # 將 inf 替換為 NaN (如果 avg_loss 是 0)，然後用 100 填充 (代表 avg_loss 為 0, 強勢)
    rs = rs.replace([np.inf, -np.inf], np.nan).fillna(100)
    
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi.fillna(50) # 將開頭的 NaN 填為 50 (中性)

    # --- 2. 產生「穿越」訊號 (向量化版本) ---
    signals = pd.Series(0, index=data.index, dtype=int)
    
    # 昨天的 RSI
    rsi_prev = data['RSI'].shift(1)
    
    # 條件 1: 買入 (向上穿越超賣線)
    buy_condition = (rsi_prev <= oversold) & (data['RSI'] > oversold)
    
    # 條件 2: 賣出 (向下穿越超買線)
    sell_condition = (rsi_prev >= overbought) & (data['RSI'] < overbought)

    # --- 3. 填入 Backtester 用的訊號 ---
    # 你的 Backtester 是「狀態機」 (Signal 1 = 持有, Signal -1 = 空手)
    # 我們需要將「事件」轉換為「狀態」
    signals[buy_condition] = 1
    signals[sell_condition] = -1
    
    # 讓訊號 "持續" 下去，直到下一個相反訊號出現
    # 使用 ffill (forward-fill) 來填充 0 的部分
    signals = signals.replace(0, np.nan).ffill().fillna(0).astype(int)

    return signals