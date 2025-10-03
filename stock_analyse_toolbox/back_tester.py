import pandas as pd

class Backtester:
    def __init__(self, data, initial_cash=100000, transaction_fee=0.001425):
        # 確保資料複製且欄位正確
        self.data = data.copy()
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = [col[0] for col in self.data.columns]  # 簡化為單層欄位
        self.initial_cash = initial_cash
        self.transaction_fee = transaction_fee  # 手續費率，例如 0.001425 表示 0.1425%

    def run(self, strategy_func, **kwargs):
        signals = strategy_func(self.data, **kwargs)
        self.data['Signal'] = signals

        position = 0
        cash = self.initial_cash
        portfolio = []

        for i in range(len(self.data)):
            price = self.data['Close'].iloc[i]
            signal = self.data['Signal'].iloc[i]

            if signal == 1 and position == 0:  # Buy
                position = (cash / price) * (1 - self.transaction_fee)  # 扣除買入手續費
                cash = 0
            elif signal == -1 and position > 0:  # Sell
                cash = (position * price) * (1 - self.transaction_fee)  # 扣除賣出手續費
                position = 0

            total_value = cash + position * price
            portfolio.append(total_value)

        self.data['Portfolio'] = portfolio
        return self.data

    def summary(self):
        total_return = self.data['Portfolio'].iloc[-1] / self.data['Portfolio'].iloc[0] - 1
        return {
            "Final Value": self.data['Portfolio'].iloc[-1],
            "Total Return": total_return
        }