# BUAA Eval

[![Release](https://img.shields.io/github/v/release/ZenAlexa/BUAA_TeachingEvaluation_2024Winter?style=flat-square)](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases)
[![License](https://img.shields.io/github/license/ZenAlexa/BUAA_TeachingEvaluation_2024Winter?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue?style=flat-square)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue?style=flat-square)](https://typescriptlang.org)

Desktop application for BUAA teaching evaluation.

## Download

| Platform | File |
|----------|------|
| Windows | [`BUAA-Eval.exe`](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/latest) |
| macOS | [`BUAA-Eval.app`](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/latest) |
| Linux | [`buaa-eval`](https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/latest) |

## Features

- **Full Score** - Select highest score for each question
- **Random** - Random selection from top options
- **Minimum Pass** - Select minimum passing score
- **Special Teachers** - Custom evaluation for specific teachers
- **Auto Skip** - Skip already evaluated courses

## Development

### Requirements

- Python 3.8+
- Node.js 18+

### Setup

```bash
git clone https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter.git
cd BUAA_TeachingEvaluation_2024Winter

# Backend
pip install -e ".[dev]"

# Frontend
cd frontend && npm install
```

### Run

```bash
cd frontend && npm run build && cd ..
python -m backend.main
```

### Build

```bash
# Windows
.\scripts\windows\build.ps1

# macOS
./scripts/macos/build.sh

# Linux
./scripts/linux/build.sh
```

## CLI

```bash
python main.py
```

## License

[MIT](LICENSE)
