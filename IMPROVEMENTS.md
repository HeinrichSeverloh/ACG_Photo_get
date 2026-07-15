# ACG_Photo_get 项目功能改进与优化报告

## 🚀 已实现的功能增强

| 功能 | 具体实现 | 说明 |
|------|----------|------|
| **持久化已下载 PID** | `PID_LOG`、`load_seen_pids()`、`register_pid()` | 防止跨运行重复下载，节约流量和存储。
| **指数退避限流** | 对 NekosAPI 与图片请求的 429 状态码实现 `retry` + `min(2**retry,30)` 退避 | 自动缓解 API 限流，避免递归栈溢出。
| **流式写入 & 冲突命名** | `requests.iter_content` + `BytesIO`，文件已存在时自动追加 `_1`, `_2` 等序号 | 降低大图内存占用，避免文件覆盖冲突。
| **可选分辨率过滤** | `CONFIG["FILTER_RESOLUTION"]`、`MIN_WIDTH`/`MIN_HEIGHT`，使用 Pillow 检测尺寸 | 默认关闭，可按需打开。
| **统一日志系统** | `logging` 设置，日志写入 `photo_get.log`，`safe_print` 统一走 `logging.info` | 方便排障、持久化运行记录。
| **CLI 参数化** | `argparse` 支持 `--target`, `--workers`, `--r18`, `--config`, `--export-config` | 无需改源码即可调整运行参数。 |
| **导出运行时配置** | `--export-config <path>` 将当前 `CONFIG`（已包含命令行覆盖）写入指定 JSON 文件 | 便于分享、备份或后续复现相同参数。
| **自定义配置文件** | `--config <json>` 读取并 `CONFIG.update(custom)` | 直接通过 JSON 覆盖任意配置项。
| **统计信息** | `stats = {"success":0,"duplicate":0,"filtered":0,"error":0}` 并在结束时打印 | 直观了解下载效果与异常分布。
| **路径解析** | `resolve_path()` 统一处理 `~` 与 `${ENV}`，提前处理 `SAVE_DIR` | 确保日志文件路径正确。
| **单元测试** | `tests/test_fetch.py`、`tests/test_download.py`（`pytest`） | 验证 API 抓取与图片下载核心逻辑。

## 📂 项目结构（新增/修改）
```
.
├─ main.py                # 主脚本，已加入上述所有改动
├─ IMPROVEMENTS.md        # 本文档
├─ tests/
│   ├─ test_fetch.py      # NekosAPI 抓取单元测试
│   └─ test_download.py  # 下载函数单元测试
└─ pyproject.toml
```

## 🛠️ 如何使用
```bash
# 默认运行（使用内置 CONFIG）
python main.py

# 指定目标数量、并发数、是否 R18
python main.py --target 50 --workers 8 --r18

# 读取外部 JSON 配置文件覆盖默认配置
python main.py --config my_config.json
```

## ✅ 运行测试
```bash
pip install pytest pillow
pytest
```

---
*以上内容已保存至项目根目录的 `IMPROVEMENTS.md`，可直接在仓库查看与编辑。*