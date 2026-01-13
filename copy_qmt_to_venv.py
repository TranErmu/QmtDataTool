"""
将QMT相关包复制到项目虚拟环境
这样就可以直接使用项目环境的numpy和pandas
"""

import os
import shutil
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
_ = load_dotenv()

# 从环境变量获取QMT路径，如果没有则使用默认值
qmt_path_str = os.getenv('QMT_PATH', r'D:\XXXX\bin.x64\Lib\site-packages')
qmt_site_packages = Path(qmt_path_str)

# 项目虚拟环境的site-packages
venv_site_packages = Path(sys.prefix) / "Lib" / "site-packages"

print("="*60)
print("将QMT包复制到项目虚拟环境")
print("="*60)
print(f"\n源目录 (QMT): {qmt_site_packages}")
print(f"目标目录 (项目): {venv_site_packages}\n")

if not qmt_site_packages.exists():
    print(f"❌ QMT目录不存在: {qmt_site_packages}")
    print(f"\n请在 .env 文件中配置正确的 QMT_PATH")
    print(f"当前配置: QMT_PATH={qmt_path_str}")
    sys.exit(1)

# 需要复制的QMT相关包
qmt_packages = ['xtquant']

for package in qmt_packages:
    print(f"\n处理 {package}...")
    print("-"*60)
    
    # 查找源包目录和相关文件
    source_items = []
    for item in qmt_site_packages.iterdir():
        if item.name.startswith(package) or item.name.startswith(package.replace('-', '_')):
            source_items.append(item)
    
    if not source_items:
        print(f"❌ 在QMT中未找到 {package}")
        continue
    
    print(f"找到 {len(source_items)} 个相关文件/目录:")
    for item in source_items:
        print(f"  - {item.name}")
    
    # 复制到项目环境
    for item in source_items:
        target = venv_site_packages / item.name
        
        try:
            # 如果目标已存在，先删除
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                    print(f"  🗑️  删除旧目录: {item.name}")
                else:
                    target.unlink()
                    print(f"  🗑️  删除旧文件: {item.name}")
                
            if item.is_dir():
                shutil.copytree(item, target)
                print(f"  ✅ 已复制目录: {item.name}")
            else:
                shutil.copy2(item, target)
                print(f"  ✅ 已复制文件: {item.name}")
        except Exception as e:
            print(f"  ❌ 复制失败 {item.name}: {e}")

print("\n" + "="*60)
print("✅ 复制完成!")
print("="*60)
print("\n现在不再需要QMT_LIB_PATH环境变量")
print("请更新代码以直接使用项目环境中的xtquant")
print("\n测试连接:")
print("  uv run test_qmt_connection_direct.py")
print("="*60)
