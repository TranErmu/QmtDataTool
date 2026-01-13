"""
数据下载主程序
从配置文件读取股票列表，批量下载数据
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.fetcher.downloader import QmtDataDownloader
from core.cleaner.validator import DataValidator
from config.etf_list import ETF_LIST
from config.stock_list import STOCK_LIST
from config.index_list import INDEX_LIST

# 加载环境变量
_ = load_dotenv()

def main():
    """主函数"""
    print("="*60)
    print("QmtDataTool - 数据下载工具")
    print("="*60)
    
    # 初始化下载器（会自动从.env读取OUTPUT_DIR）
    downloader = QmtDataDownloader()
    
    # 合并所有代码列表
    all_codes = ETF_LIST + STOCK_LIST + INDEX_LIST
    
    print(f"\n准备下载 {len(all_codes)} 个标的:")
    print(f"  - ETF: {len(ETF_LIST)} 个")
    print(f"  - 股票: {len(STOCK_LIST)} 个")
    print(f"  - 指数: {len(INDEX_LIST)} 个\n")
    
    # 从环境变量读取配置，如果没有则使用默认值
    years_per_segment = int(os.getenv('YEARS_PER_SEGMENT', '3'))
    retry_times = int(os.getenv('RETRY_TIMES', '3'))
    
    # 批量下载
    # 从2020年开始，到今天，每3年一个分段
    # 可以选择输出格式：'parquet', 'csv', 'excel'
    results = downloader.download_batch(
        code_list=all_codes,
        start_time='20200101',
        period='1d',
        dividend_type='front',  # 前复权
        years_per_segment=years_per_segment,  # 从环境变量读取，默认3
        retry_times=retry_times,  # 从环境变量读取，默认3
        # 输出格式：默认只保存parquet
        # 可以添加多种格式，例如: ['parquet', 'csv', 'excel']
        output_formats=['parquet', 'csv']  # 只保存parquet格式（推荐，文件小且快）
        # output_formats=['parquet', 'csv']  # 同时保存parquet和csv
        # output_formats=['parquet', 'csv', 'excel']  # 保存所有格式
    )
    
    print("\n" + "="*60)
    print("下载完成，开始生成数据清单...")
    print("="*60)
    
    # 验证数据并生成清单
    validator = DataValidator(downloader.output_dir)
    manifest = validator.generate_manifest(all_codes)
    validator.save_manifest(manifest)
    validator.print_manifest_summary(manifest)
    
    print("\n✅ 全部完成！")

if __name__ == "__main__":
    main()
