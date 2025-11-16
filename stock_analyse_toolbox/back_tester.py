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
        
        # 儲存結果
        self.results_data = None

    def run(self, strategy_func, **kwargs):
        # 複製一份資料，避免汙染
        run_data = self.data.copy()
        
        signals = strategy_func(run_data, **kwargs)
        run_data['Signal'] = signals

        position = 0
        cash = self.initial_cash
        portfolio = []
        
        #重設交易紀錄
        self.trades = []
        self.buy_price = 0.0

        for i in range(len(run_data)):
            price = run_data['Close'].iloc[i]
            signal = run_data['Signal'].iloc[i]

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
            last_price = run_data['Close'].iloc[-1]
            trade_pnl_pct = (last_price - self.buy_price) / self.buy_price
            self.trades.append({
                'buy_price': self.buy_price,
                'sell_price': last_price,
                'pnl_pct': trade_pnl_pct
            })
            self.buy_price = 0.0

        run_data['Portfolio'] = portfolio
        
        # 儲存這次的執行結果
        self.results_data = run_data 
        return self.results_data

    def get_summary_stats(self):
        """
        計算並回傳包含「原始數值」的字典，用於參數優化。
        """
        if self.results_data is None:
            raise Exception("請先執行 run() 才能取得摘要。")
            
        # 投資組合淨值
        final_value = self.results_data['Portfolio'].iloc[-1]
        total_return = final_value / self.results_data['Portfolio'].iloc[0] - 1
        
        # 買入並持有 (Buy and Hold) 基準
        buy_and_hold_return = self.results_data['Close'].iloc[-1] / self.results_data['Close'].iloc[0] - 1

        stats = {
            "Final Value": final_value,
            "Total Return": total_return,
            "Buy and Hold Return": buy_and_hold_return,
            "Total Trades": 0,
            "Win Rate": 0,
            "Average PnL": 0,
            "Max Profit": 0,
            "Max Loss": 0
        }

        if not self.trades:
            return stats

        # 逐筆交易統計
        pnl_pcts = [t['pnl_pct'] for t in self.trades]
        total_trades = len(self.trades)
        win_trades = sum(1 for pnl in pnl_pcts if pnl > 0)
        
        stats["Total Trades"] = total_trades
        stats["Win Rate"] = (win_trades / total_trades) if total_trades > 0 else 0
        stats["Average PnL"] = np.mean(pnl_pcts) if total_trades > 0 else 0
        stats["Max Profit"] = max(pnl_pcts) if total_trades > 0 else 0
        stats["Max Loss"] = min(pnl_pcts) if total_trades > 0 else 0
        
        return stats

    def summary(self):
        """
        計算並回傳「格式化後」的字串字典，用於列印。
        """
        stats = self.get_summary_stats()
        
        if stats is None:
            return {}

        # 格式化輸出
        formatted_summary = {
            "Final Value": f"{stats['Final Value']:,.2f}",
            "Total Return": f"{stats['Total Return']:.2%}",
            "Buy and Hold Return": f"{stats['Buy and Hold Return']:.2%}",
            "--- Trade Stats ---": "---",
            "Total Trades": stats['Total Trades'],
            "Win Rate": f"{stats['Win Rate']:.2%}",
            "Average PnL per Trade": f"{stats['Average PnL']:.4f}",
            "Max Profit per Trade": f"{stats['Max Profit']:.4f}",
            "Max Loss per Trade": f"{stats['Max Loss']:.4f}",
        }
        return formatted_summary