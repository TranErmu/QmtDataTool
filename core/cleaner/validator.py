"""
数据验证和元数据管理模块
"""

import os
import json
import pandas as pd
from typing import Any
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
    def check_data_completeness(self, code: str) -> dict[str, str | bool | int | list[str] | float | None]:
        """检查单个数据文件的完整性
        
        Args:
            code: 股票/ETF代码
            
        Returns:
            元数据字典
        """
        file_path = os.path.join(self.output_dir, f"{code}.parquet")
        
        if not os.path.exists(file_path):
            return {
                'code': code,
                'exists': False,
                'error': 'File not found'
            }
        
        try:
            df = pd.read_parquet(file_path)
            
            metadata = {
                'code': code,
                'exists': True,
                'start_date': str(df.index[0].date()) if len(df) > 0 else None,  # type: ignore[union-attr]
                'end_date': str(df.index[-1].date()) if len(df) > 0 else None,  # type: ignore[union-attr]
                'count': len(df),
                'fields': list(df.columns),
                'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
            }
            
            return metadata
            
        except Exception as e:
            return {
                'code': code,
                'exists': True,
                'error': str(e)
            }
    
    def generate_manifest(self, code_list: list[str] | None = None) -> dict[str, dict[str, Any]]:
        """生成数据清单报告
        
        Args:
            code_list: 要检查的代码列表，None则检查output目录下所有文件
            
        Returns:
            清单字典
        """
        if code_list is None:
            # 扫描output目录
            code_list = []
            for file in os.listdir(self.output_dir):
                if file.endswith('.parquet'):
                    code = file.replace('.parquet', '')
                    code_list.append(code)
        
        manifest = {}
        
        for code in code_list:
            metadata = self.check_data_completeness(code)
            manifest[code] = metadata
        
        return manifest
    
    def save_manifest(self, manifest: dict[str, dict[str, Any]], filename: str = 'manifest.json'):
        """保存清单到JSON文件
        
        Args:
            manifest: 清单字典
            filename: 文件名
        """
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 清单已保存到: {file_path}")
    
    def print_manifest_summary(self, manifest: dict[str, dict[str, Any]]):
        """打印清单摘要
        
        Args:
            manifest: 清单字典
        """
        print("\n" + "="*60)
        print("数据清单摘要")
        print("="*60)
        
        total = len(manifest)
        success = sum(1 for v in manifest.values() if v.get('exists') and 'error' not in v)
        
        print(f"总数据文件: {total}")
        print(f"完整文件数: {success}")
        print(f"异常文件数: {total - success}")
        print("")
        
        for code, meta in manifest.items():
            if meta.get('exists') and 'error' not in meta:
                print(f"{code:15} | {meta['start_date']} ~ {meta['end_date']} | "
                      f"{meta['count']:6} 条 | {meta['file_size_mb']:6.2f} MB")
            else:
                error = meta.get('error', 'Unknown error')
                print(f"{code:15} | ❌ {error}")
        
        print("="*60)
