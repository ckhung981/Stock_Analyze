import pandas as pd

def moving_average_strategy(data, short=10, long=30):
    """均線交叉策略"""
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data index must be DatetimeIndex")
    
    # 確保欄位正確
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = [col[0] for col in data.columns]
    
    short_ma = data['Close'].rolling(short).mean()
    long_ma = data['Close'].rolling(long).mean()

    signals = pd.Series(0, index=data.index, dtype=int)
    signals.loc[short_ma > long_ma] = 1
    signals.loc[short_ma < long_ma] = -1
    signals = signals.fillna(0).astype(int)  # 處理 NaN
    return signals

def rsi_strategy(data, period=14, overbought=70, oversold=30):
    """RSI 超買超賣策略"""
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = [col[0] for col in data.columns]
    
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))