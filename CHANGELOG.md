# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-08

### Added
- Desktop GUI application with React + TypeScript frontend
- Cross-platform support (Windows, macOS, Linux)
- Real-time progress tracking with log viewer
- Three evaluation methods: Full Score, Random, Minimum Pass
- Special teacher handling with custom evaluation
- Modern UI with grid background and minimal design

### Changed
- Migrated from CLI-only to desktop application
- Restructured project with frontend/backend separation
- Updated all dependencies to latest versions

### Technical
- Frontend: React 18, TypeScript, Vite, Lucide Icons
- Backend: Python 3.8+, pywebview, requests
- Build: PyInstaller with platform-specific configurations

## [1.0.0] - 2024-12-01

### Added
- Initial CLI release
- SSO authentication support
- Three evaluation strategies
- Auto-skip completed courses
- Rate limiting for requests

[2.0.0]: https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/tag/v2.0.0
[1.0.0]: https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/tag/v1.0.0
