# BUAA Eval

[![Release](https://img.shields.io/github/v/release/ZenAlexa/BUAA_TeachingEvaluation_2024Winter?style=flat-square)](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases)
[![License](https://img.shields.io/github/license/ZenAlexa/BUAA_TeachingEvaluation_2024Winter?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue?style=flat-square)](https://python.org)

北航教学评估助手 | BUAA Teaching Evaluation Assistant

一键完成课程评价 | Auto-complete course evaluations with one click

## Download | 下载

| Platform | File | 平台 |
|----------|------|------|
| Windows | [`BUAA-Evaluation-Windows.exe`](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/latest) | Windows |
| macOS | [`BUAA-Evaluation-macOS.zip`](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/latest) | macOS |
| Linux | [`BUAA-Evaluation-Linux`](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/latest) | Linux |

## Installation | 安装

### Windows

1. Download `BUAA-Evaluation-Windows.exe`
2. Double-click to run

下载后双击运行即可。

### macOS

1. Download and unzip `BUAA-Evaluation-macOS.zip`
2. Move `BUAA-Evaluation.app` to Applications folder
3. **First run**: The app is unsigned, run this command in Terminal:

```bash
xattr -cr /Applications/BUAA-Evaluation.app
```

4. Double-click to open

---

1. 下载并解压 `BUAA-Evaluation-macOS.zip`
2. 将 `BUAA-Evaluation.app` 移动到"应用程序"文件夹
3. **首次运行**：应用未签名，需在终端运行以下命令：

```bash
xattr -cr /Applications/BUAA-Evaluation.app
```

4. 双击打开

### Linux

1. Download `BUAA-Evaluation-Linux`
2. Make it executable and run:

```bash
chmod +x BUAA-Evaluation-Linux
./BUAA-Evaluation-Linux
```

## Features | 功能

- **Full Score | 满分评价** - Select highest score for each question | 每题选择最高分
- **Random | 随机评价** - Random selection from top options | 从前几个选项中随机选择
- **Minimum Pass | 最低及格** - Select minimum passing score | 选择及格分数
- **Special Teachers | 特殊教师** - Custom evaluation for specific teachers | 为指定教师单独设置评价方式
- **Auto Skip | 自动跳过** - Skip already evaluated courses | 跳过已完成评价的课程
- **Bilingual UI | 双语界面** - Chinese/English language switch | 中英文切换

## CLI Mode | 命令行模式

```bash
python main.py
```

## Development | 开发

### Requirements | 环境要求

- Python 3.8+
- Node.js 18+

### Setup | 设置

```bash
git clone https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter.git
cd BUAA_TeachingEvaluation_2024Winter

# Install Python dependencies | 安装 Python 依赖
pip install -e ".[dev]"

# Install frontend dependencies | 安装前端依赖
cd frontend && npm install
```

### Run | 运行

```bash
# Build frontend | 构建前端
cd frontend && npm run build && cd ..

# Run GUI | 运行图形界面
cd backend && python main.py
```

### Build | 构建

```bash
# Windows
.\scripts\windows\build.ps1

# macOS
./scripts/macos/build.sh

# Linux
./scripts/linux/build.sh
```

## License | 许可证

[MIT](LICENSE)

---

Made with ❤️ for BUAA | 为 BUAA 用 ❤️ 制作
