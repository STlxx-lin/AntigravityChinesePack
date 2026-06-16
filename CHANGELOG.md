# Changelog

## 2026.11.6 (2026-06-16)

### ✨ 新特性
- **硬编码汉化引擎 (Patch Engine)**：新增 `patch_zh.py` 脚本，支持对 IDE 主程序 `out/main.js` (Chat)、`out/jetskiAgent/main.js` (Settings) 以及 `out/vs/workbench/workbench.desktop.main.js` (Workbench) 进行直接源码级汉化，完美解决部分关键界面硬编码英文的问题。
- **一键切换屏蔽更新**：支持屏蔽 Antigravity IDE 的自动更新，提供命令面板指令与状态栏快捷图标（右下角盾牌）以便随时切换，保护汉化成果不被覆盖。
- **更全面的 NLS 覆盖**：新增并补充了更多专属扩展的 NLS 翻译条目，包含：
  - Antigravity 核心 (25 条)
  - Browser Launcher (4 条)
  - Code Executor (2 条)
  - Dev Containers (9 条)
  - Remote - SSH (20 条)
  - Remote - WSL (17 条)
  - VS Code 基础覆盖 (7 条)

### 🔧 优化与修复
- **分支迁移与重塑**：重构并迁移为 `STlxx-lin` 维护的专有分支，更新了 `package.json` 中的仓库链接、发布者及插件标识名。
- **.gitignore 深度优化**：重构并新增了完整的 Git 忽略规则，涵盖 OS 临时文件、Node/NPM 依赖日志、VS Code 临时/打包产物，以及 Python 编译缓存与虚拟环境。
- **移除未跟踪缓存**：从 Git 跟踪中删除了历史遗留的 `__pycache__` 编译缓存文件。
- **文档完善**：更新 `README.md` 中的 NLS 翻译统计表格与硬编码补丁目标路径，使数据与实际代码完全一致。

---

## 1.0.0 (2026-02-08)

### 🎉 初始版本

- 支持 Antigravity 核心扩展（AI 功能、登录、导入设置等）的简体中文翻译
- 支持 Browser Launcher 浏览器启动器的简体中文翻译
- 支持 Code Executor 代码执行器的简体中文翻译
- 支持 Dev Containers 开发容器的简体中文翻译
- 支持 Remote - SSH 远程连接的简体中文翻译
- 支持 Remote - WSL 子系统连接的简体中文翻译
