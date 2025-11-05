# (在 back_tester.py 中)
import pandas as pd
import numpy as np # 需要 numpy

class Backtester:
    def __init__(self, data, initial_cash=100000, transaction_fee=0.001425):
        self.data = data.copy()
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = [col[0] for col in self.data.columns]
        self.initial_cash = initial_cash
        self.transaction_fee = transaction_fee
        
        # 儲存所有交易紀錄
        self.trades = [] 
        self.buy_price = 0.0

    def run(self, strategy_func, **kwargs):
        signals = strategy_func(self.data, **kwargs)
        self.data['Signal'] = signals

        position = 0
        cash = self.initial_cash
        portfolio = []
        
        #重設交易紀錄
        self.trades = []
        self.buy_price = 0.0

        for i in range(len(self.data)):
            price = self.data['Close'].iloc[i]
            signal = self.data['Signal'].iloc[i]

            if signal == 1 and position == 0:  # Buy
                position = (cash / price) * (1 - self.transaction_fee)
                cash = 0
                
                #記錄買入價格
                self.buy_price = price 
                
            elif signal == -1 and position > 0:  # Sell
                cash = (position * price) * (1 - self.transaction_fee)
                position = 0
                
                # 記錄一筆完整交易
                if self.buy_price > 0:
                    sell_price = price
                    trade_pnl_pct = (sell_price - self.buy_price) / self.buy_price
                    self.trades.append({
                        'buy_price': self.buy_price,
                        'sell_price': sell_price,
                        'pnl_pct': trade_pnl_pct
                    })
                    self.buy_price = 0.0 # 重設買入價

            total_value = cash + position * price
            portfolio.append(total_value)

        #處理期末仍持倉的情況 (強制平倉)
        if position > 0 and self.buy_price > 0:
            last_price = self.data['Close'].iloc[-1]
            trade_pnl_pct = (last_price - self.buy_price) / self.buy_price
            self.trades.append({
                'buy_price': self.buy_price,
                'sell_price': last_price,
                'pnl_pct': trade_pnl_pct
            })
            self.buy_price = 0.0

        self.data['Portfolio'] = portfolio
        return self.data

    def summary(self):
        
        # 投資組合淨值
        final_value = self.data['Portfolio'].iloc[-1]
        total_return = final_value / self.data['Portfolio'].iloc[0] - 1
        
        if not self.trades:
            return {
                "Final Value": final_value,
                "Total Return": total_return,
                "Total Trades": 0
            }

        # 逐筆交易統計
        pnl_pcts = [t['pnl_pct'] for t in self.trades]
        total_trades = len(self.trades)
        win_trades = sum(1 for pnl in pnl_pcts if pnl > 0)
        lose_trades = sum(1 for pnl in pnl_pcts if pnl < 0)
        win_rate = (win_trades / total_trades) if total_trades > 0 else 0
        
        avg_pnl = np.mean(pnl_pcts) if total_trades > 0 else 0
        max_profit = max(pnl_pcts) if total_trades > 0 else 0
        max_loss = min(pnl_pcts) if total_trades > 0 else 0
        
        return {
            "Final Value": final_value,
            "Total Return": total_return,
            "--- Trade Stats ---": "---",
            "Total Trades": total_trades,
            "Win Rate": f"{win_rate:.2%}",
            "Average PnL per Trade": f"{avg_pnl:.4f}",
            "Max Profit per Trade": f"{max_profit:.4f}",
            "Max Loss per Trade": f"{max_loss:.4f}",
        }