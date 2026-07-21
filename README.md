# 🌸 ACG Photo Get

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)
[![Code%20Style](https://img.shields.io/badge/Code%20Style-PEP8-orange.svg)](https://peps.python.org/pep-0008/)

## 简介

ACG Photo Get 是一款面向二次元爱好者的图片自动化下载工具。它可以并发抓取 **NekosAPI** 与 **Lolicon API** 提供的高质量图片，支持分辨率过滤、R18 内容开关以及灵活的命令行/JSON 配置，适合在服务器上配合 **Cron** 实现定时图库更新。

## 核心特性
- 🚀 **并发下载**：基于 `ThreadPoolExecutor` 实现多线程提升抓取速度。
- 🖼️ **智能过滤**：默认过滤低于 `1920×1080` 的图片，支持手动开启/关闭。
- 🔄 **多 API 支持**：可自由切换 NekosAPI 与 Lolicon API。
- 🛡️ **内容控制**：R18 开关，默认仅下载 Safe 内容。
- ⚙️ **高度可配置**：支持命令行参数或外部 JSON 配置文件。
- 📦 **易于打包**：提供 PyInstaller 打包脚本，生成独立可执行文件。

## 环境要求
- **Python** >= 3.10
- **依赖**: `requests>=2.34.2`, `pillow>=12.3.0`, `pyqt6>=6.11.0`
- **操作系统**: Linux / macOS / Windows

## 安装指南
```bash
# 克隆仓库
git clone https://github.com/HeinrichSeverloh/ACG_Photo_get.git
cd ACG_Photo_get

# 推荐使用 uv 管理依赖（若未安装 uv，请先 `pip install uv`）
uv sync
```
或使用 pip：
```bash
pip install -r requirements.txt
```

## 使用方法
### CLI
```bash
uv run main.py                # 默认配置
uv run main.py -t 50           # 下载 50 张图片
uv run main.py -r              # 开启 R18 内容
uv run main.py --api lolicon  # 使用 Lolicon API
uv run main.py -c config.json  # 使用 JSON 配置文件
```
### GUI
```bash
uv run gui.py
```
在图形界面中可直观设置下载数量、并发数、标签、R18、分辨率过滤等参数，点击 **开始下载** 即可。

## 自动化部署 (Cron 示例)
```cron
0 3 * * * /usr/bin/env uv run /path/to/ACG_Photo_get/main.py -t 100 >> /var/log/acg_photo_get.log 2>&1
```
将上述指令写入系统 `crontab`，即可实现每日凌晨自动抓取最新图片。

## 项目结构
```
.
├── gui.py               # PyQt6 GUI
├── main.py              # CLI 主逻辑
├── tests/               # 单元测试
│   ├── test_download.py
│   └── test_fetch.py
├── pyproject.toml       # 项目元数据与依赖
└── README.md
```

## 注意事项
- 默认保存路径为 `"/DATA/Photo/Static"`，若目录不可写会回退到用户主目录下的 `ACG_Photo_get`。
- 如遇 API 限流（429），程序会自动指数退避重试。

## 贡献指南
欢迎提交 Issue 与 Pull Request！
- 请保持代码符合 **PEP8** 风格。
- 提交前请运行 `pytest` 确保所有测试通过。

## 许可证
本项目采用 **GNU GPL v3** 许可证，详见 [LICENSE](LICENSE)。
