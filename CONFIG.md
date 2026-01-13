# ============================================================
# QmtDataTool 配置指南
# ============================================================

## 环境配置

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 配置QMT路径

编辑 `.env` 文件，修改 `QMT_PATH` 为你的实际QMT安装路径：

```env
# 默认路径
QMT_PATH=D:\ProgramData\QMT\Lib\site-packages

# 如果QMT安装在其他位置，修改为实际路径
# QMT_PATH=C:\YourPath\QMT\Lib\site-packages
```

#### 如何找到QMT路径？

**方法1：通过MiniQMT查找**
1. 打开MiniQMT客户端
2. 点击"帮助" → "关于"
3. 查看安装路径，在路径后添加 `\Lib\site-packages`

**方法2：通过文件搜索**
1. 打开文件资源管理器
2. 搜索 `xtquant`
3. 找到包含 `xtquant` 文件夹的 `site-packages` 目录
4. 复制完整路径

**常见路径示例：**
- `D:\ProgramData\QMT\Lib\site-packages`
- `C:\Program Files\QMT\Lib\site-packages`
- `C:\QMT\Lib\site-packages`

### 3. 复制QMT到项目环境（仅首次）

```bash
uv run copy_qmt_to_venv.py
```

此脚本会：
1. 读取 `.env` 中的 `QMT_PATH`
2. 将 `xtquant` 复制到项目虚拟环境
3. 之后不再需要配置环境变量

## 可选配置

### 自定义输出目录

默认数据保存在 `output/` 目录，如果想更改：

```env
OUTPUT_DIR=D:\MyData\QMT
```

### 下载参数配置

```env
# 起始时间（YYYYMMDD格式）
START_TIME=20200101

# 每段年数（建议3-5年）
YEARS_PER_SEGMENT=3

# 重试次数
RETRY_TIMES=3
```

## 注意事项

1. **`.env` 文件已在 `.gitignore` 中**
   - 不会被git跟踪
   - 可以安全配置个人路径

2. **路径格式**
   - Windows路径可以使用 `\` 或 `/`
   - 例如：`D:\Path` 或 `D:/Path` 都可以

3. **QMT必须先安装**
   - 确保MiniQMT已安装并可以正常运行
   - 首次使用前需登录MiniQMT

4. **环境变量优先级**
   - `.env` > 系统环境变量 > 默认值

## 常见问题

### Q: 找不到QMT路径怎么办？

A: 运行以下Python代码查找：

```python
import os
for root, dirs, files in os.walk('C:\\'):
    if 'xtquant' in dirs:
        print(os.path.join(root, 'xtquant'))
```

### Q: 复制脚本报错"目录不存在"？

A: 检查：
1. `.env` 文件是否存在
2. `QMT_PATH` 配置是否正确
3. 路径中的 `\` 是否正确转义

### Q: 需要在每台机器上配置吗？

A: 是的，每台机器的QMT安装路径可能不同，需要：
1. 复制 `.env.example` 为 `.env`
2. 修改为本机的QMT路径
3. 运行 `copy_qmt_to_venv.py`

## 示例配置

### 完整 `.env` 示例

```env
# QMT配置
QMT_PATH=D:\ProgramData\QMT\Lib\site-packages

# 项目配置
OUTPUT_DIR=D:\workspace\Quant\data

# 下载配置
START_TIME=20180101
YEARS_PER_SEGMENT=3
RETRY_TIMES=3
```

### 最小配置

只需要配置QMT路径即可：

```env
QMT_PATH=D:\ProgramData\QMT\Lib\site-packages
```

其他配置项都有合理的默认值。
