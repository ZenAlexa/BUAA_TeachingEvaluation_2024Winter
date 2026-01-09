# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-01-09

### Fixed - Critical Startup Freeze Issue
- **CRITICAL**: Removed `http_server=True` parameter that caused Windows freezing
- **CRITICAL**: Fixed event registration timing - now registers BEFORE `webview.start()`
- **CRITICAL**: Added polling-based ready detection via `api.is_ready()` method
- Fixed `pywebviewready` event race condition with early capture script in `<head>`
- Fixed frontend infinite loading when API initialization fails

### Added
- `is_ready()` and `mark_ready()` methods in API for reliable ready state detection
- 15-second timeout with error message display for initialization failures
- Detailed console logging for debugging startup issues
- Error display in LoadingScreen component

### Changed
- Simplified `main.py` startup flow - no more background thread callback
- Moved pywebview event capture script to `<head>` before any other scripts
- `useApi` hook now uses polling instead of relying solely on events
- Improved thread safety with `RLock` in API class

### Technical Details
- pywebview automatically starts HTTP server (Bottle) for local files
- Event order: `before_load` → `_pywebviewready` → `loaded`
- Frontend polls `api.is_ready()` every 100ms until ready or timeout

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

[1.5.0]: https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/tag/v1.5.0
[2.0.0]: https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/tag/v2.0.0
[1.0.0]: https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter/releases/tag/v1.0.0
