import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import ta

def plot_indicators(data, ticker=None, indicators_to_plot=['RSI','MACD','OBV']):
    """
    畫技術指標，並自動建立資料夾存圖
    """
    if ticker is None:
        ticker = getattr(data,  'Ticker', 'UNKNOWN')

    # 建立資料夾
    folder = os.path.join('output', ticker)
    os.makedirs(folder, exist_ok=True)

    # 計算技術指標
    close = data['Close']
    volume = data['Volume']

    if 'RSI' in indicators_to_plot:
        data['RSI'] = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    if 'MACD' in indicators_to_plot:
        macd = ta.trend.MACD(close)
        data['MACD'] = macd.macd()
        data['MACD_signal'] = macd.macd_signal()
        data['MACD_hist'] = macd.macd_diff()
    if 'OBV' in indicators_to_plot:
        data['OBV'] = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()

    # 設定 subplot
    n_subplots = len(indicators_to_plot)
    fig, axes = plt.subplots(n_subplots, 1, figsize=(14, 3*n_subplots), sharex=True)

    if n_subplots == 1:
        axes = [axes]

    for ax, ind in zip(axes, indicators_to_plot):
        if ind == 'RSI':
            ax.plot(data.index, data['RSI'], label='RSI', color='purple')
            ax.axhline(70, linestyle='--', color='red', alpha=0.7, label='Overbought 70')
            ax.axhline(30, linestyle='--', color='green', alpha=0.7, label='Oversold 30')
            ax.set_ylabel('RSI')
            ax.legend(loc='upper left')
        elif ind == 'MACD':
            ax.plot(data.index, data['MACD'], label='MACD', color='blue')
            ax.plot(data.index, data['MACD_signal'], label='Signal', color='red')
            ax.bar(data.index, data['MACD_hist'], label='MACD Hist', color='gray', alpha=0.4)
            ax.axhline(0, color='black', linestyle='--')
            ax.set_ylabel('MACD')
            ax.legend(loc='upper left')
        elif ind == 'OBV':
            ax.plot(data.index, data['OBV'], label='OBV', color='brown')
            ax.set_ylabel('OBV')
            ax.legend(loc='upper left')

    # X 軸格式
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    save_path = os.path.join(folder, f'{ticker}_indicators.png')
    plt.savefig(save_path)
    print(f"Saved indicator chart to {save_path}")
