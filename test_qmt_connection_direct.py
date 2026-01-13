"""
测试直接使用项目环境中的xtquant
不需要QMT_LIB_PATH
"""

print("正在导入xtquant...")

try:
    from xtquant import xtdata
    print("✅ xtquant导入成功\n")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    print("\n请先运行: uv run copy_qmt_to_venv.py")
    exit(1)

# 测试获取数据
print("="*60)
print("测试: 获取510300.SH的最近10天数据")
print("="*60)

try:
    data = xtdata.get_market_data(
        field_list=['open', 'high', 'low', 'close', 'volume'],
        stock_list=['510300.SH'],
        period='1d',
        start_time='',
        end_time='',
        count=10
    )
    
    if data and 'close' in data:
        print("✅ 成功获取数据!")
        print(f"\nclose价格数据:")
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
