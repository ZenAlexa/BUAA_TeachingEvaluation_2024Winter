# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

BUAA Teaching Evaluation Assistant - A desktop application for auto-completing course evaluations at Beijing University of Aeronautics and Astronautics (BUAA).

## Tech Stack

- **Backend**: Python 3.9+ with pywebview for cross-platform desktop GUI
- **Frontend**: React 18 + TypeScript + Vite
- **Animation**: animejs 3.x
- **HTTP Client**: requests with retry logic
- **Build**: PyInstaller for packaging

## Architecture

```
backend/
  ├── main.py          # Desktop app entry point (pywebview)
  ├── api.py           # Python-to-JS bridge (EvaluationAPI class)
  └── evaluator.py     # Core evaluation logic

frontend/
  └── src/
      ├── App.tsx      # Main React component
      ├── components/  # UI components with animations
      ├── hooks/       # useApi, useAnimation
      └── i18n/        # Translations (en/zh)
```

## Key Patterns

### pywebview Best Practices (v1.5.0)

**CRITICAL**: Follow these patterns to prevent "Not Responding" issues:

1. **DO NOT use `http_server=True`** - It causes Windows to freeze:
   ```python
   # BAD - causes freezing
   webview.start(http_server=True)

   # GOOD - use direct file loading
   webview.start(gui=gui, debug=debug_mode)
   ```

2. **Register events BEFORE `webview.start()`**:
   ```python
   window = webview.create_window(...)
   window.events.loaded += on_loaded  # BEFORE start()
   window.events.closing += on_closing
   webview.start()  # Events already registered
   ```

3. **Use polling for ready detection** - Don't rely solely on events:
   ```python
   # api.py
   def is_ready(self) -> bool:
       return self._ready

   def mark_ready(self):
       self._ready = True
   ```

4. **Lazy initialization** - Don't do heavy init in `__init__`:
   ```python
   @property
   def session(self):
       if self._session is None:
           self._session = create_session()
       return self._session
   ```

### Python-to-JavaScript Communication

**CRITICAL**: When calling frontend functions via `_call_frontend()`, Python values must be converted to JS syntax:
- `True` → `true` (not `'True'`)
- `False` → `false` (not `'False'`)
- `None` → `null`

Use `_python_to_js()` helper in `api.py` for proper conversion.

### Threading

Long-running operations (like `start_evaluation`) run in background threads to prevent UI freeze. Use `threading.Thread` with `daemon=True`.

### HTML Loading Spinner

The `index.html` includes an inline CSS loading spinner that shows immediately before React mounts. This provides visual feedback during startup.

### API Endpoints

All requests go to `https://spoc.buaa.edu.cn/pjxt/`. Key endpoints:
- `personnelEvaluation/listObtainPersonnelEvaluationTasks` - Get tasks
- `evaluationMethodSix/getQuestionnaireListToTask` - Get questionnaires
- `evaluationMethodSix/getRequiredReviewsData` - Get courses
- `evaluationMethodSix/submitSaveEvaluation` - Submit evaluation

## Build Commands

```bash
# Frontend
cd frontend && npm install && npm run build

# Run GUI
cd backend && python main.py

# Build executable (see scripts/)
```

## Common Issues

1. **"False is not defined"**: Python bool not converted to JS - use `_to_js()` in api.py
2. **UI freeze / Not Responding** (v1.5.0 complete fix):
   - **DO NOT** use `http_server=True` in `webview.start()` - causes Windows freezing
   - Register event handlers **BEFORE** `webview.start()`, not in callback
   - Use polling via `api.is_ready()` instead of relying on events
   - Keep `webview.start()` simple with minimal parameters
3. **Request timeout**: Add timeout to all `requests` calls
4. **Windows blurry**: Ensure DPI awareness is set in `main.py`
5. **Slow startup**:
   - Add HTML loading spinner in index.html
   - Use lazy session initialization
6. **Stuck on "Initializing"** (v1.5.0 complete fix):
   - **Root cause**: Multiple - `pywebviewready` event timing + `http_server=True` + event registration timing
   - **Solution**:
     1. Early event capture script in `<head>` BEFORE any other scripts
     2. Frontend polls `api.is_ready()` instead of relying solely on events
     3. Backend sets `_ready=True` on `window.events.loaded`
     4. 15-second timeout with error display
   - See `frontend/index.html`, `frontend/src/hooks/useApi.ts`, `backend/main.py`

## Platform-Specific Notes

### Windows
- EdgeChromium is preferred (auto-detected)
- DPI awareness enabled for 4K displays
- Avoid `import clr` checks (slow)
- **pywebviewready event timing**: May fire before React mounts - use early capture mechanism

### macOS
- Cocoa WebKit is used (auto-detected)
- NSApplication.sharedApplication() for high-DPI

### Linux
- GTK with WebKit2 explicitly set
- Requires webkit2gtk package
