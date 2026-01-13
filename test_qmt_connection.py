"""
测试QMT连接和数据获取
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置QMT路径
qmt_path = os.getenv("QMT_LIB_PATH")
if qmt_path:
    sys.path.insert(0, qmt_path)
    print(f"✅ QMT路径: {qmt_path}")
else:
    print("❌ 未找到QMT_LIB_PATH环境变量")
    sys.exit(1)

# 导入xtquant
try:
    from xtquant import xtdata
    print("✅ xtquant导入成功")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    sys.exit(1)

# 测试1: 获取单个股票的最新数据
print("\n" + "="*60)
print("测试1: 获取510300.SH的最近10天数据")
print("="*60)

try:
    data = xtdata.get_market_data(
        field_list=['open', 'high', 'low', 'close', 'volume'],
        stock_list=['510300.SH'],
        period='1d',
        start_time='',  # 空字符串表示使用默认起始时间
        end_time='',    # 空字符串表示到最新
        count=10        # 获取最近10条数据
    )
    
    if data and 'close' in data:
        print("✅ 成功获取数据!")
        print(f"数据类型: {type(data)}")
        print(f"数据字段: {list(data.keys())}")
        print(f"\nclose价格数据预览:")
        print(data['close'])
    else:
        print("❌ 未获取到数据")
        print(f"返回结果: {data}")
        
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 测试指定时间范围的数据
print("\n" + "="*60)
print("测试2: 获取510300.SH从2023年1月开始的数据")
print("="*60)

try:
    data = xtdata.get_market_data(
        field_list=['open', 'high', 'low', 'close', 'volume'],
        stock_list=['510300.SH'],
        period='1d',
        start_time='20230101',
        end_time='20230131',
        dividend_type='front'
    )
    
    if data and 'close' in data:
        print("✅ 成功获取数据!")
        print(f"数据字段: {list(data.keys())}")
        print(f"\nclose价格数据:")
        print(data['close'])
    else:
        print("❌ 未获取到数据")
        print(f"返回结果: {data}")
        
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 尝试其他股票
print("\n" + "="*60)
print("测试3: 获取600519.SH(贵州茅台)的最近数据")
print("="*60)

try:
    data = xtdata.get_market_data(
        field_list=['close'],
        stock_list=['600519.SH'],
        period='1d',
        start_time='',
        end_time='',
        count=5
    )
    
    if data and 'close' in data:
        print("✅ 成功获取数据!")
        print(data['close'])
    else:
        print("❌ 未获取到数据")
        print(f"返回结果: {data}")
        
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)
