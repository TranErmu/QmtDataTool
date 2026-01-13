# 多格式导出功能使用说明

## 功能概述

现在下载器支持将数据保存为多种格式：
- **Parquet** (默认) - 推荐，文件小且读取快
- **CSV** - Excel可直接打开，通用性强
- **Excel** - 美观，适合查看和分析

## 使用方法

### 1. 在download.py中配置输出格式

```python
results = downloader.download_batch(
    code_list=all_codes,
    start_time='20200101',
    period='1d',
    dividend_type='front',
    years_per_segment=3,
    
    # 选择输出格式
    output_formats=['parquet']  # 只保存parquet（默认，推荐）
    # output_formats=['parquet', 'csv']  # 同时保存parquet和csv
    # output_formats=['parquet', 'csv', 'excel']  # 保存所有格式
)
```

### 2. 支持的格式

| 格式 | 参数值 | 优点 | 缺点 |
|------|--------|------|------|
| Parquet | `'parquet'` | 文件小，速度快，推荐 | 需要专门工具查看 |
| CSV | `'csv'` | Excel可直接打开，通用 | 文件较大，中文需utf-8-sig |
| Excel | `'excel'` 或 `'xlsx'` | 美观，易查看 | 文件最大，需openpyxl |

### 3. 自动生成股票列表

下载完成后会自动生成两个文件：

#### `stock_list.csv` - CSV格式列表
```csv
代码,起始日期,结束日期,数据量,文件
510300.SH,2020-01-02,2026-01-13,1462,510300.SH.parquet
002594.SZ,2020-01-02,2026-01-13,1462,002594.SZ.parquet
```

#### `stock_list.xlsx` - Excel格式列表
更美观的Excel表格，包含相同信息，方便查阅。

## 示例

### 例1：只保存Parquet（推荐）
```python
output_formats=['parquet']
```
- 文件小，速度快
- 适合程序化读取

### 例2：同时保存CSV和Parquet
```python
output_formats=['parquet', 'csv']
```
- Parquet用于程序读取
- CSV用于Excel快速查看

### 例3：保存所有格式
```python
output_formats=['parquet', 'csv', 'excel']
```
- 最全面，但占空间最大
- 适合需要多种查看方式的场景

## 文件位置

所有文件保存在 `output/` 目录：
```
output/
├── 510300.SH.parquet
├── 510300.SH.csv        # 如果选择了csv
├── 510300.SH.xlsx       # 如果选择了excel
├── 002594.SZ.parquet
├── stock_list.csv       # 自动生成的股票列表
└── stock_list.xlsx      # 自动生成的Excel列表
```

## 注意事项

1. **Excel格式需要openpyxl**：`uv add openpyxl`
2. **CSV中文编码**：使用utf-8-sig确保Excel正确显示中文
3. **文件大小**：Parquet < CSV < Excel
4. **读取速度**：Parquet最快

## 推荐配置

- **日常使用**：`['parquet']` - 快速高效
- **需要查看**：`['parquet', 'csv']` - 兼顾速度和可读性
- **展示分享**：`['parquet', 'csv', 'excel']` - 最全面
