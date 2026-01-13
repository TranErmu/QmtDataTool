"""
QMT连接状态诊断工具
检查xtquant与MiniQMT的连接状态
"""

print("="*60)
print("QMT连接诊断工具")
print("="*60)

# 1. 检查xtquant导入
print("\n[1/4] 检查xtquant导入...")
try:
    from xtquant import xtdata
    print("✅ xtquant导入成功")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    print("\n请先运行: uv run copy_qmt_to_venv.py")
    exit(1)

# 2. 检查MiniQMT连接状态
print("\n[2/4] 检查MiniQMT连接状态...")
try:
    # 尝试调用连接检查API
    # QMT有一个connect()方法来建立连接
    connected = xtdata.connect()
    if connected:
        print("✅ MiniQMT连接成功")
    else:
        print("❌ MiniQMT连接失败")
        print("\n请确保：")
        print("1. 已启动MiniQMT客户端")
        print("2. 已登录MiniQMT账号")
        print("3. MiniQMT运行正常")
except AttributeError:
    print("⚠️  没有connect()方法，尝试直接获取数据...")
except Exception as e:
    print(f"⚠️  连接检查出错: {e}")

# 3. 测试数据获取（简单测试）
print("\n[3/4] 测试数据获取能力...")
try:
    # 尝试获取一个知名股票的最新数据
    data = xtdata.get_market_data(
        field_list=['close'],
        stock_list=['600519.SH'],  # 贵州茅台
        period='1d',
        count=5  # 只获取最近5天
    )
    
    if data and isinstance(data, dict):
        print(f"✅ 数据获取成功")
        print(f"   返回数据类型: {type(data)}")
        print(f"   数据字段: {list(data.keys())}")
        
        # 检查数据是否为空
        if 'close' in data:
            close_data = data['close']
            print(f"   close数据形状: {close_data.shape if hasattr(close_data, 'shape') else 'N/A'}")
            print(f"   close数据内容:")
            print(close_data)
            
            # 判断是否真的有数据
            if hasattr(close_data, 'empty'):
                if close_data.empty:
                    print("⚠️  返回的DataFrame为空！")
                else:
                    print("✅ 包含真实数据")
    else:
        print(f"❌ 数据获取失败，返回: {data}")
        
except Exception as e:
    print(f"❌ 数据获取失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 检查订阅能力（如果需要）
print("\n[4/4] 检查其他可用功能...")
try:
    # 列出xtdata的可用方法
    methods = [m for m in dir(xtdata) if not m.startswith('_')]
    print(f"✅ xtdata共有 {len(methods)} 个可用方法")
    print("\n主要方法：")
    important_methods = [
        'connect', 'disconnect', 'get_market_data', 
        'get_full_tick', 'subscribe_quote', 'download_history_data'
    ]
    for method in important_methods:
        if method in methods:
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} (不可用)")
            
except Exception as e:
    print(f"⚠️  检查功能时出错: {e}")

# 总结
print("\n" + "="*60)
print("诊断总结")
print("="*60)
print("\n如果看到 MiniQMT连接失败 或 数据获取失败，请按以下步骤操作：")
print("\n1. 🖥️  启动MiniQMT客户端")
print("   - 找到并打开MiniQMT应用程序")
print("   - 通常在: 开始菜单 > QMT > MiniQMT")
print("\n2. 🔐 登录账号")
print("   - 使用您的券商账号登录MiniQMT")
print("   - 确保登录成功")
print("\n3. ✅ 确认连接")
print("   - MiniQMT客户端需要保持运行")
print("   - 重新运行此诊断脚本")
print("\n4. 🔄 如果还是失败")
print("   - 检查MiniQMT是否正常运行（没有错误提示）")
print("   - 尝试重启MiniQMT")
print("   - 检查是否有防火墙阻止连接")

print("\n" + "="*60)
print("诊断完成")
print("="*60)
