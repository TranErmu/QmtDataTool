"""
数据下载器 - 核心ETL模块
支持分段下载、自动合并、断点续传
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import logging
import time
from dotenv import load_dotenv

# 直接导入xtquant（已复制到项目环境）
from xtquant import xtdata

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QmtDataDownloader:
    """QMT数据下载器"""
    
    def __init__(self, output_dir: str | None = None):
        """初始化下载器
        
        Args:
            output_dir: 输出目录，默认为QmtDataTool/output或从.env读取
        """
        # 加载环境变量
        load_dotenv()
        
        # 设置输出目录
        if output_dir is None:
            # 优先从环境变量读取
            env_output_dir = os.getenv('OUTPUT_DIR')
            if env_output_dir:
                self.output_dir = env_output_dir
                logger.info(f"📁 使用环境变量配置的输出目录: {self.output_dir}")
            else:
                # 使用默认目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                qmt_root = os.path.dirname(os.path.dirname(current_dir))
                self.output_dir = os.path.join(qmt_root, 'output')
        else:
            self.output_dir = output_dir
            
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("✅ 数据下载器初始化成功")
    
    def _generate_time_segments(self, start_time: str, end_time: str | None = None, 
                               years_per_segment: int = 3) -> list[tuple[str, str]]:
        """生成时间分段
        
        Args:
            start_time: 起始时间，格式YYYYMMDD
            end_time: 结束时间，格式YYYYMMDD，默认为今天
            years_per_segment: 每个分段的年数
            
        Returns:
            时间段列表 [(start1, end1), (start2, end2), ...]
        """
        if end_time is None:
            end_time = datetime.now().strftime('%Y%m%d')
        
        # 解析日期
        start_dt = datetime.strptime(start_time, '%Y%m%d')
        end_dt = datetime.strptime(end_time, '%Y%m%d')
        
        segments = []
        current_start = start_dt
        
        while current_start < end_dt:
            # 计算当前段的结束时间
            current_end = datetime(
                current_start.year + years_per_segment,
                current_start.month,
                current_start.day
            )
            
            # 如果超过了总结束时间，则使用总结束时间
            if current_end > end_dt:
                current_end = end_dt
            
            segments.append((
                current_start.strftime('%Y%m%d'),
                current_end.strftime('%Y%m%d')
            ))
            
            # 移动到下一个分段的起始时间（当前结束时间+1天）
            current_start = current_end + timedelta(days=1)
        
        return segments
    
    def _download_segment(self, code: str, start_time: str, end_time: str,
                         period: str = '1d', dividend_type: str = 'front') -> pd.DataFrame | None:
        """下载一个时间段的数据
        
        Args:
            code: 股票/ETF代码
            start_time: 起始时间
            end_time: 结束时间
            period: 周期，默认日线
            dividend_type: 复权方式，默认前复权
            
        Returns:
            DataFrame或None（如果失败）
        """
        try:
            # 第一步：下载历史数据到本地缓存
            # 这是QMT的必要步骤，必须先下载数据
            logger.info(f"   下载 {code} ({start_time} - {end_time}) 到本地缓存...")
            xtdata.download_history_data(
                stock_code=code,
                period=period,
                start_time=start_time,
                end_time=end_time
            )
            
            # 获取数据字段
            field_list = ['open', 'high', 'low', 'close', 'volume', 'amount']
            
            # 第二步：从本地缓存获取数据
            data_dict = xtdata.get_market_data(
                field_list=field_list,
                stock_list=[code],
                period=period,
                start_time=start_time,
                end_time=end_time,
                dividend_type=dividend_type,
                fill_data=False  # 不填充数据
            )
            
            # 检查是否有数据
            if not data_dict or 'close' not in data_dict:
                logger.warning(f"⚠️ {code} 在 {start_time}-{end_time} 期间无数据")
                return None
            
            # 将数据字典转换为DataFrame
            # 数据格式: {field: DataFrame(index=codes, columns=times)}
            df_list = []
            for field in field_list:
                if field in data_dict:
                    # 转置使时间成为index
                    df_field = data_dict[field].T
                    # 重命名列
                    df_field.columns = [field]
                    df_list.append(df_field)
            
            if not df_list:
                return None
            
            # 合并所有字段
            df = pd.concat(df_list, axis=1)
            
            # 确保索引是datetime类型
            df.index = pd.to_datetime(df.index)
            df.index.name = 'date'
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 下载 {code} 数据失败 ({start_time}-{end_time}): {e}")
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        if df is None or len(df) == 0:
            return df
        
        # 去除volume=0的行（停牌）
        df = df[df['volume'] > 0]
        
        # 去除close=0或NaN的行
        df = df[(df['close'] > 0) & (df['close'].notna())]
        
        # 去除其他字段的NaN
        df = df.dropna()
        
        # 按日期排序
        df = df.sort_index()
        
        # 去重（保留最后一条）
        df = df[~df.index.duplicated(keep='last')]
        
        return df
    
    def download_stock_data(self, code: str, start_time: str = '20000101',
                           end_time: str = None, period: str = '1d',
                           dividend_type: str = 'front',
                           years_per_segment: int = 3,
                           retry_times: int = 3,
                           output_formats: list[str] | None = None) -> bool:
        """下载单个股票/ETF的历史数据
        
        Args:
            code: 股票/ETF代码
            start_time: 起始时间
            end_time: 结束时间，默认今天
            period: 周期
            dividend_type: 复权方式
            years_per_segment: 每段的年数
            retry_times: 重试次数
            output_formats: 输出格式列表，可选 ['parquet', 'csv', 'excel']
                          默认只保存parquet格式
            
        Returns:
            是否成功
        """
        # 默认只保存parquet格式
        if output_formats is None:
            output_formats = ['parquet']
        
        logger.info(f"📊 开始下载 {code} 的数据")
        
        # 生成时间分段
        segments = self._generate_time_segments(start_time, end_time, years_per_segment)
        logger.info(f"   分为 {len(segments)} 个时间段")
        
        # 存储所有分段的数据
        all_data = []
        
        # 逐段下载
        for start, end in tqdm(segments, desc=f"下载{code}"):
            # 尝试下载
            df_segment = None
            for attempt in range(retry_times):
                df_segment = self._download_segment(
                    code, start, end, period, dividend_type
                )
                if df_segment is not None:
                    break
                if attempt < retry_times - 1:
                    logger.warning(f"⚠️ 重试 {attempt + 1}/{retry_times}")
                    time.sleep(1)  # 等待1秒后重试
            
            if df_segment is not None and len(df_segment) > 0:
                all_data.append(df_segment)
        
        if not all_data:
            logger.error(f"❌ {code} 没有下载到任何数据")
            return False
        
        # 合并所有分段
        logger.info(f"   合并 {len(all_data)} 个数据段")
        df_combined = pd.concat(all_data, axis=0)
        
        # 清洗数据
        logger.info(f"   清洗数据（原始行数: {len(df_combined)}）")
        df_clean = self._clean_data(df_combined)
        logger.info(f"   清洗后行数: {len(df_clean)}）")
        
        if len(df_clean) == 0:
            logger.error(f"❌ {code} 清洗后无数据")
            return False
        
        # 保存为多种格式
        saved_files = []
        
        for fmt in output_formats:
            fmt = fmt.lower()
            
            if fmt == 'parquet':
                output_path = os.path.join(self.output_dir, f"{code}.parquet")
                df_clean.to_parquet(output_path, engine='pyarrow', compression='snappy')
                saved_files.append(output_path)
                
            elif fmt == 'csv':
                output_path = os.path.join(self.output_dir, f"{code}.csv")
                df_clean.to_csv(output_path, encoding='utf-8-sig')  # utf-8-sig 支持中文Excel打开
                saved_files.append(output_path)
                
            elif fmt == 'excel' or fmt == 'xlsx':
                output_path = os.path.join(self.output_dir, f"{code}.xlsx")
                df_clean.to_excel(output_path, engine='openpyxl')
                saved_files.append(output_path)
                
            else:
                logger.warning(f"⚠️ 不支持的格式: {fmt}，已跳过")
        
        # 打印保存信息
        logger.info(f"✅ {code} 数据已保存")
        logger.info(f"   时间范围: {df_clean.index[0]} ~ {df_clean.index[-1]}")
        logger.info(f"   总行数: {len(df_clean)}")
        logger.info(f"   保存格式: {', '.join(output_formats)}")
        for file in saved_files:
            logger.info(f"   文件: {file}")
        
        return True
    
    def download_batch(self, code_list: list[str], **kwargs) -> dict[str, bool]:
        """批量下载多个股票/ETF的数据
        
        Args:
            code_list: 代码列表
            **kwargs: 传递给download_stock_data的其他参数
            
        Returns:
            下载结果字典 {code: success}
        """
        results = {}
        
        logger.info(f"🚀 开始批量下载 {len(code_list)} 个标的")
        
        for code in code_list:
            success = self.download_stock_data(code, **kwargs)
            results[code] = success
            # 每个标的之间暂停一下，避免请求过快
            time.sleep(0.5)
        
        # 统计结果
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"📈 批量下载完成: {success_count}/{len(code_list)} 成功")
        
        # 保存成功下载的股票列表
        if success_count > 0:
            self.save_stock_list(results)
        
        return results
    
    def save_stock_list(self, results: dict[str, bool]) -> None:
        """保存已下载的股票代码列表
        
        Args:
            results: 下载结果字典 {code: success}
        """
        # 筛选成功的股票
        successful_codes = [code for code, success in results.items() if success]
        
        if not successful_codes:
            return
        
        # 创建DataFrame
        stock_list_data = []
        for code in successful_codes:
            # 尝试读取数据获取详细信息
            try:
                parquet_file = os.path.join(self.output_dir, f"{code}.parquet")
                if os.path.exists(parquet_file):
                    df = pd.read_parquet(parquet_file)
                    stock_list_data.append({
                        '代码': code,
                        '起始日期': str(df.index[0].date()),
                        '结束日期': str(df.index[-1].date()),
                        '数据量': len(df),
                        '文件': f"{code}.parquet"
                    })
                else:
                    stock_list_data.append({
                        '代码': code,
                        '起始日期': '-',
                        '结束日期': '-',
                        '数据量': 0,
                        '文件': '-'
                    })
            except Exception as e:
                logger.warning(f"⚠️ 读取 {code} 信息失败: {e}")
                stock_list_data.append({
                    '代码': code,
                    '起始日期': '-',
                    '结束日期': '-',
                    '数据量': 0,
                    '文件': '-'
                })
        
        df_list = pd.DataFrame(stock_list_data)
        
        # 保存为CSV（方便查看）
        csv_path = os.path.join(self.output_dir, 'stock_list.csv')
        df_list.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"📋 股票列表已保存到: {csv_path}")
        
        # 保存为Excel（更美观）
        try:
            excel_path = os.path.join(self.output_dir, 'stock_list.xlsx')
            df_list.to_excel(excel_path, index=False, engine='openpyxl')
            logger.info(f"📋 股票列表已保存到: {excel_path}")
        except Exception as e:
            logger.warning(f"⚠️ 保存Excel失败: {e}，请安装openpyxl: pip install openpyxl")


def load_data(code: str, output_dir: str = None) -> pd.DataFrame:
    """从output目录读取指定代码的数据
    
    Args:
        code: 股票/ETF代码
        output_dir: 输出目录，默认为项目内的output目录
        
    Returns:
        DataFrame
    """
    if output_dir is None:
        # 获取默认output目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        qmt_root = os.path.dirname(os.path.dirname(current_dir))
        output_dir = os.path.join(qmt_root, 'output')
    
    file_path = os.path.join(output_dir, f"{code}.parquet")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    df = pd.read_parquet(file_path, engine='pyarrow')
    return df
