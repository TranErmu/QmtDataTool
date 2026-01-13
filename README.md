# QmtDataTool - QMT金融数据下载工具

<img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
<img src="https://img.shields.io/badge/License-GPL--3.0-orange.svg" alt="GPL-3.0 License">

一个**高可用的金融数据获取和清洗工具**，用于从QMT获取A股、ETF和指数的历史数据。

## ✨ 特性

- 🚀 **分段下载** - 按时间段切割，避免大数据量失败
- 🔄 **断点续传** - 支持重试机制，单段失败不影响整体
- 🧹 **数据清洗** - 自动去除停牌和异常数据
- 📦 **多格式导出** - 支持 Parquet/CSV/Excel 多种格式
- 📋 **自动报告** - 生成数据清单和股票列表
- ⚙️  **灵活配置** - 环境变量配置，支持个性化定制

## 📚 目录

- [快速开始](#-快速开始)
- [环境配置](#-环境配置)
- [使用方法](#-使用方法)
- [多格式导出](#-多格式导出)
- [项目结构](#-项目结构)
- [开发文档](#-开发文档)
- [常见问题](#-常见问题)

## 🚀 快速开始

### 1. 安装依赖

```bash
cd QmtDataTool
uv add xtquant pandas numpy pyarrow fastparquet tqdm openpyxl python-dotenv
```

### 2. 配置环境

复制环境变量模板并配置QMT路径：

```bash
cp .env.example .env
```

编辑 [`.env`](.env) 文件，修改为你的实际QMT安装路径：

```env
QMT_PATH=D:\ProgramData\QMT\Lib\site-packages
```

> 💡 **如何找到QMT路径？** 查看详细说明：[CONFIG.md](CONFIG.md)

### 3. 复制QMT到项目环境（仅首次）

```bash
uv run copy_qmt_to_venv.py
```

此步骤会将QMT的 `xtquant` 包复制到项目虚拟环境，之后不再需要配置环境变量。

### 4. 启动MiniQMT并登录

⚠️ **重要**：在运行下载脚本前，必须：
1. 启动MiniQMT客户端
2. 使用券商账号登录
3. 保持MiniQMT运行

### 5. 运行下载脚本

```bash
uv run download.py
```

数据将保存在 `output/` 目录，包括：
- 数据文件（Parquet/CSV格式）
- [`manifest.json`](output/manifest.json) - 数据清单
- [`stock_list.csv`](output/stock_list.csv) / [`stock_list.xlsx`](output/stock_list.xlsx) - 股票列表

## ⚙️ 环境配置

### 配置文件

- [`.env.example`](.env.example) - 环境变量模板
- [`.env`](.env) - 您的本地配置（不会被git跟踪）
- [`CONFIG.md`](CONFIG.md) - 详细配置指南

### 可配置项

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `QMT_PATH` | QMT安装路径（必需） | `D:\ProgramData\QMT\Lib\site-packages` |
| `OUTPUT_DIR` | 数据输出目录 | `项目根目录/output` |
| `YEARS_PER_SEGMENT` | 每段下载年数 | `3` |
| `RETRY_TIMES` | 重试次数 | `3` |

### 配置示例

```env
# 必需配置
QMT_PATH=D:\ProgramData\QMT\Lib\site-packages

# 可选配置（有默认值）
OUTPUT_DIR=D:\MyData\QMT
YEARS_PER_SEGMENT=3
RETRY_TIMES=3
```

## 📖 使用方法

### 快速下载

运行主程序即可下载所有配置的股票：

```bash
uv run download.py
```

### 自定义股票列表

编辑配置文件添加或删除股票代码：

- [`config/etf_list.py`](config/etf_list.py) - ETF列表
- [`config/stock_list.py`](config/stock_list.py) - 股票列表
- [`config/index_list.py`](config/index_list.py) - 指数列表

**示例**：添加新股票到 [`config/stock_list.py`](config/stock_list.py)

```python
STOCK_LIST = [
    '600519.SH',  # 贵州茅台
    '000858.SZ',  # 五粮液
    '600036.SH',  # 招商银行
    # 在这里添加更多股票
]
```

> ⚠️ **注意**：股票代码必须带交易所后缀（`.SH` 或 `.SZ`）

### 回测示例

使用下载的数据运行回测：

```bash
uv run backtest_demo.py
```

查看 [`backtest_demo.py`](backtest_demo.py) 了解如何加载和使用数据。

## 📊 多格式导出

支持同时导出多种格式，方便不同场景使用。

### 配置导出格式

在 [`download.py`](download.py) 中修改 `output_formats` 参数：

```python
# 只保存Parquet（默认，推荐）
output_formats=['parquet']

# 同时保存Parquet和CSV
output_formats=['parquet', 'csv']

# 保存所有格式
output_formats=['parquet', 'csv', 'excel']
```

### 格式对比

| 格式 | 文件大小 | 读取速度 | 可读性 | 适用场景 |
|------|----------|----------|--------|----------|
| Parquet | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | 程序化处理（推荐） |
| CSV | ⭐⭐ | ⭐⭐ | ✓ | Excel快速查看 |
| Excel | ⭐ | ⭐ | ⭐⭐⭐ | 展示、分享 |

详细说明请查看：[EXPORT_FORMATS.md](EXPORT_FORMATS.md)

## 📁 项目结构

```
QmtDataTool/
├── core/                      # 核心模块
│   ├── fetcher/              # 数据获取
│   │   └── downloader.py     # 下载器核心
│   └── cleaner/              # 数据清洗
│       └── validator.py      # 验证器
├── config/                    # 配置模块
│   ├── etf_list.py           # ETF列表
│   ├── stock_list.py         # 股票列表
│   └── index_list.py         # 指数列表
├── output/                    # 数据输出目录
│   ├── *.parquet             # Parquet数据文件
│   ├── *.csv                 # CSV数据文件（可选）
│   ├── *.xlsx                # Excel数据文件（可选）
│   ├── manifest.json         # 数据清单
│   └── stock_list.csv/xlsx   # 股票列表
├── .env.example              # 环境变量模板
├── .env                      # 本地配置（不会被git跟踪）
├── copy_qmt_to_venv.py       # QMT环境复制脚本
├── download.py               # 数据下载主程序
├── backtest_demo.py          # 回测示例
├── CONFIG.md                 # 配置指南
├── EXPORT_FORMATS.md         # 导出格式说明
├── QmtDataTool_Dev.md        # 开发文档
└── README.md                 # 本文件
```

## 📚 开发文档

- [`CONFIG.md`](CONFIG.md) - 详细的环境配置指南
- [`EXPORT_FORMATS.md`](EXPORT_FORMATS.md) - 多格式导出使用说明
- [`QmtDataTool_Dev.md`](QmtDataTool_Dev.md) - 项目构建经验总结

## ❓ 常见问题

### Q: 下载数据为空怎么办？

**A:** 检查以下几点：
1. ✅ MiniQMT是否已启动并登录
2. ✅ 股票代码格式是否正确（必须带`.SH`或`.SZ`）
3. ✅ 时间范围是否有数据

运行诊断脚本检查：
```bash
uv run diagnose_qmt_connection.py
```

### Q: 如何找到QMT安装路径？

**A:** 详见 [`CONFIG.md`](CONFIG.md#如何找到qmt路径) 的"如何找到QMT路径"章节。

常见路径：
- `D:\ProgramData\QMT\Lib\site-packages`
- `C:\Program Files\QMT\Lib\site-packages`
- `C:\QMT\Lib\site-packages`

### Q: 需要在每台机器上配置吗？

**A:** 是的，每台机器需要：
1. 复制 [`.env.example`](.env.example) 为 `.env`
2. 修改为本机的QMT路径
3. 运行 `uv run copy_qmt_to_venv.py`

### Q: 数据保存在哪里？

**A:** 默认保存在 `output/` 目录。

可以通过 `.env` 文件中的 `OUTPUT_DIR` 配置自定义路径：
```env
OUTPUT_DIR=D:\MyData\QMT
```

### Q: 如何修改下载时间范围？

**A:** 在 [`download.py`](download.py) 中修改 `start_time` 参数：

```python
results = downloader.download_batch(
    code_list=all_codes,
    start_time='20180101',  # 修改起始时间
    # ...
)
```

### Q: CSV文件中文乱码怎么办？

**A:** 工具已使用 `utf-8-sig` 编码，Excel应该能正确显示中文。如果仍有问题，可以：
1. 使用Excel打开CSV时选择UTF-8编码
2. 或直接使用生成的 `.xlsx` 文件

### Q: 如何更新数据？

**A:** 直接重新运行下载脚本：
```bash
uv run download.py
```

新数据会覆盖旧数据。

## 🔧 进阶使用

### 编程方式加载数据

```python
from core.fetcher.downloader import load_data

# 加载单个股票数据
df = load_data('510300.SH')

# 查看数据
print(df.head())
print(f"时间范围: {df.index[0]} ~ {df.index[-1]}")
print(f"数据量: {len(df)} 条")
```

### 批量处理数据

```python
from config.stock_list import STOCK_LIST
from core.fetcher.downloader import load_data

for code in STOCK_LIST:
    df = load_data(code)
    # 处理数据
    print(f"{code}: {len(df)} 条数据")
```

## 📝 数据格式

所有数据文件包含以下标准字段：

| 字段 | 说明 | 类型 |
|------|------|------|
| date (索引) | 交易日期 | Timestamp |
| open | 开盘价 | float |
| high | 最高价 | float |
| low | 最低价 | float |
| close | 收盘价 | float |
| volume | 成交量 | float |
| amount | 成交额 | float |

**数据特点**：
- ✅ 前复权处理
- ✅ 已去除停牌日（volume=0）
- ✅ 已去除异常数据
- ✅ 按日期排序
- ✅ 已去重

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 **GPL-3.0 许可证**。

这意味着：
- ✅ 您可以自由使用、修改和分发本项目
- ⚠️ **您必须将衍生作品也以 GPL-3.0 许可证开源**
- ⚠️ 修改后的代码必须标明修改内容
- ⚠️ 必须保留原作者的版权声明

详细条款请查看 [LICENSE](LICENSE) 文件。

---

**最后更新**：2026-01-13

**项目状态**：✅ 生产就绪，可正常使用
