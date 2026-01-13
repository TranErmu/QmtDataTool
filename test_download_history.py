"""
测试download_history_data方法
这可能是QMT获取历史数据的正确方法
"""

from xtquant import xtdata
import pandas as pd

print("="*60)
print("测试 download_history_data 方法")
print("="*60)

# 测试1: 使用download_history_data下载数据
print("\n[测试1] 使用 download_history_data 下载贵州茅台数据")
print("-"*60)

try:
    # download_history_data通常用于预先下载数据到本地缓存
    result = xtdata.download_history_data(
        stock_code='600519.SH',
        period='1d',
        start_time='20230101',
        end_time='20231231'
    )
    
    print(f"✅ download_history_data 调用成功")
    print(f"   返回结果: {result}")
    
except Exception as e:
    print(f"❌ download_history_data 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 下载后再用get_market_data获取
print("\n[测试2] 下载后使用 get_market_data 获取数据")
print("-"*60)

try:
    # 先下载
    print("步骤1: 下载历史数据...")
    xtdata.download_history_data('600519.SH', period='1d', start_time='20230101')
    
    # 再获取
    print("步骤2: 获取市场数据...")
    data = xtdata.get_market_data(
        field_list=['open', 'high', 'low', 'close', 'volume'],
        stock_list=['600519.SH'],
        period='1d',
        start_time='20230101',
        end_time='20231231'
    )
    
    if data and 'close' in data:
        close_data = data['close']
        print(f"✅ 成功获取数据!")
        print(f"   数据形状: {close_data.shape}")
        print(f"\n前5行数据:")
        print(close_data.head() if hasattr(close_data, 'head') else close_data)
        
        if hasattr(close_data, 'empty') and not close_data.empty:
            print("\n✅ 数据不为空，包含真实数据！")
        else:
            print("\n⚠️  数据仍然为空")
    else:
        print(f"❌ 未获取到数据")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 使用不同的参数格式
print("\n[测试3] 尝试不同的参数格式")
print("-"*60)

try:
    # 有些版本可能需要不同的参数格式
    data = xtdata.get_market_data(
        field_list=['close'],
        stock_list=['600519.SH'],
        period='1d',
        start_time='',  # 空字符串
        end_time='',
        count=10  # 指定获取最近N条数据
    )
    
    if data and 'close' in data:
        close_data = data['close']
        print(f"✅ 使用count参数成功")
        print(f"   数据形状: {close_data.shape}")
        print(close_data)
    else:
        print("❌ 使用count参数也失败")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")

# 测试4: 查看xtdata的帮助信息
print("\n[测试4] 查看 get_market_data 的帮助信息")
print("-"*60)

try:
    help_text = xtdata.get_market_data.__doc__
    if help_text:
        print(help_text)
    else:
        print("⚠️  没有帮助文档")
        
    # 尝试查看函数签名
    import inspect
    sig = inspect.signature(xtdata.get_market_data)
    print(f"\n函数签名: {sig}")
    
except Exception as e:
    print(f"⚠️  无法获取帮助: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
