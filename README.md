# 🌸 ACG Photo Get

> 一个高效、可配置的二次元图片批量下载与自动化管理脚本。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP8-orange.svg)](https://peps.python.org/pep-0008/)

ACG Photo Get 是一个专为二次元爱好者设计的图片自动化下载工具。它支持从多个主流 ACG 图片 API（如 NekosAPI、Lolicon API）并发抓取高质量图片，并提供分辨率过滤、内容分级控制以及灵活的配置方式。非常适合部署在服务器上配合定时任务（如 Cron）实现自动化图库更新。

---

## 📑 目录

- [🌸 ACG Photo Get](#-acg-photo-get)
  - [📑 目录](#-目录)
  - [✨ 核心特性](#-核心特性)
  - [📦 环境要求](#-环境要求)
  - [🚀 安装指南](#-安装指南)
  - [💻 使用方法](#-使用方法)
    - [1. 基础运行](#1-基础运行)
    - [2. 命令行参数](#2-命令行参数)
    - [3. 使用 JSON 配置文件](#3-使用-json-配置文件)
  - [⚙️ 自动化部署建议 (Cron)](#️-自动化部署建议-cron)
  - [📂 项目结构](#-项目结构)
  - [⚠️ 注意事项](#-注意事项)
  - [🤝 贡献指南](#-贡献指南)
  - [📜 许可证](#-许可证)

---

## ✨ 核心特性

- 🚀 **并发下载**：基于 `ThreadPoolExecutor` 实现多线程并发下载，大幅提升获取效率。
- 🖼️ **智能过滤**：支持按分辨率过滤（默认过滤低于 1920×1080 的图片），确保图库质量。
- 🔄 **多 API 支持**：无缝切换 `NekosAPI` 与 `Lolicon API` 作为图片源。
- 🛡️ **内容控制**：提供 R18 内容开关，默认仅获取安全（Safe）内容。
- ⚙️ **高度可配置**：支持通过命令行参数或外部 JSON 文件灵活调整所有运行参数。
- 📦 **易于打包**：提供 `build_exe.py`，方便将脚本打包为独立可执行文件。

---

## 📦 环境要求

- **Python**: `>= 3.10`
- **操作系统**: Linux / macOS / Windows (推荐在 Linux 服务器上配合 Cron 运行)
- **核心依赖**:
  - `requests >= 2.34.2`
  - `pillow >= 12.3.0`

---

## 🚀 安装指南

1. **克隆仓库**
   ```bash
   git clone https://github.com/HeinrichSeverloh/ACG_Photo_get.git
   cd ACG_Photo_get
