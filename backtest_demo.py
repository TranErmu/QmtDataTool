"""
简易回测示例
演示如何使用下载的数据进行回测
"""

import sys
import os
import pandas as pd
from typing import cast
from pandas import Timestamp

# 添加QmtDataTool到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.fetcher.downloader import load_data
from config.etf_list import ETF_LIST
from config.stock_list import STOCK_LIST


class SimpleBacktest:
    """简易回测引擎
    
    支持：
    - T+1交易规则
    - 涨跌停限制（简化版）
    """
    
    def __init__(self, initial_cash: float = 100000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0  # 持仓数量
        self.trades = []  # 交易记录
        
    def can_buy(self, price: float, amount: int) -> bool:
        """检查是否可以买入"""
        cost = price * amount
        return self.cash >= cost
    
    def buy(self, date, price: float, amount: int):
        """买入"""
        cost = price * amount
        if self.cash >= cost:
            self.cash -= cost
            self.position += amount
            self.trades.append({
                'date': date,
                'action': 'BUY',
                'price': price,
                'amount': amount,
                'cost': cost
            })
            return True
        return False
    
    def sell(self, date, price: float, amount: int):
        """卖出"""
        if self.position >= amount:
            proceeds = price * amount
            self.cash += proceeds
            self.position -= amount
            self.trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'amount': amount,
                'proceeds': proceeds
            })
            return True
        return False
    
    def get_portfolio_value(self, current_price: float) -> float:
        """获取当前组合价值"""
        return self.cash + self.position * current_price
    
    def print_summary(self, final_price: float):
        """打印回测摘要"""
        final_value = self.get_portfolio_value(final_price)
        total_return = (final_value - self.initial_cash) / self.initial_cash * 100
        
        print("\n" + "="*60)
        print("回测摘要")
        print("="*60)
        print(f"初始资金: ¥{self.initial_cash:,.2f}")
        print(f"最终价值: ¥{final_value:,.2f}")
        print(f"总收益率: {total_return:.2f}%")
        print(f"交易次数: {len(self.trades)}")
        print("="*60)


def run_ma_strategy(df: pd.DataFrame, short_window: int = 5, long_window: int = 20):
    """运行双均线策略
    
    Args:
        df: 数据DataFrame
        short_window: 短期均线窗口
        long_window: 长期均线窗口
    """
    # 计算均线
    df = df.copy()
    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()
    
    # 生成信号
    df['signal'] = 0
    df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1  # 买入信号
    df.loc[df['ma_short'] < df['ma_long'], 'signal'] = -1  # 卖出信号
    
    # 删除前long_window行（均线还没计算出来）
    df = df.iloc[long_window:]
    
    # 创建回测引擎
    backtest = SimpleBacktest(initial_cash=100000)
    
    # 模拟交易（T+1）
    prev_signal = 0
    
    for i in range(1, len(df)):
        current_date = df.index[i]
        current_price = df.iloc[i]['close']
        prev_signal_value = df.iloc[i-1]['signal']
        
        # T+1: 根据前一天的信号，今天开盘买入/卖出
        if prev_signal_value == 1 and prev_signal != 1:
            # 买入信号：全仓买入
            can_buy_amount = int(backtest.cash / current_price / 100) * 100  # 买入100的整数倍
            if can_buy_amount > 0:
                backtest.buy(current_date, current_price, can_buy_amount)
                prev_signal = 1
                
        elif prev_signal_value == -1 and prev_signal != -1:
            # 卖出信号：全部卖出
            if backtest.position > 0:
                backtest.sell(current_date, current_price, backtest.position)
                prev_signal = -1
    
    # 打印结果
    final_price = df.iloc[-1]['close']
    backtest.print_summary(final_price)
    
    print("\n交易记录（前10条）:")
    print("="*60)
    for trade in backtest.trades[:10]:
        print(f"{cast(Timestamp, trade['date']).date()} | {trade['action']:4} | "
              f"价格: ¥{trade['price']:.2f} | 数量: {trade['amount']}")
    
    if len(backtest.trades) > 10:
        print(f"... 还有 {len(backtest.trades) - 10} 条交易")
    print("="*60)


def main():
    """主函数"""
    print("="*60)
    print("QmtDataTool - 回测示例")
    print("="*60)
    
    # 选择一个ETF进行回测
    code = ETF_LIST[0]  # 沪深300ETF
    
    print(f"\n正在加载 {code} 的数据...")
    
    try:
        df = load_data(code)
        print(f"✅ 数据加载成功")
        print(f"   时间范围: {cast(Timestamp, df.index[0]).date()} ~ {cast(Timestamp, df.index[-1]).date()}")
        print(f"   数据行数: {len(df)}")
        
        print(f"\n运行双均线策略 (MA5 vs MA20)...")
        run_ma_strategy(df, short_window=5, long_window=20)
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("提示: 请先运行 download.py 下载数据")
    except Exception as e:
        print(f"❌ 回测失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
