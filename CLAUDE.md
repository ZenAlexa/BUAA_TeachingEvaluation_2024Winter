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

### pywebview Best Practices

**CRITICAL**: Follow these patterns to prevent "Not Responding" issues:

1. **Use `webview.start(func, args)` pattern** - Pass startup function to run in background thread:
   ```python
   def on_startup(window, api):
       # Runs in background thread - GUI stays responsive
       window.events.shown += on_shown_handler

   webview.start(func=on_startup, args=(window, api))
   ```

2. **Use window events** - Register handlers for lifecycle events:
   - `window.events.shown` - Window first displayed (do post-show init here)
   - `window.events.loaded` - DOM fully loaded
   - `window.events.closing` - Window about to close

3. **Lazy initialization** - Don't do heavy init in `__init__`:
   ```python
   @property
   def session(self):
       if self._session is None:
           self._session = create_session()
       return self._session
   ```

4. **Background pre-warming** - Pre-warm resources after window shows:
   ```python
   def on_shown():
       threading.Thread(target=prewarm_session, daemon=True).start()
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

1. **"False is not defined"**: Python bool not converted to JS - use `_python_to_js()`
2. **UI freeze / Not Responding**:
   - Use `webview.start(func, args)` pattern
   - Move heavy init to `window.events.shown` handler
   - Use lazy initialization for HTTP sessions
3. **Request timeout**: Add timeout to all `requests` calls
4. **Windows blurry**: Ensure DPI awareness is set in `main.py`
5. **Slow startup**:
   - Add HTML loading spinner in index.html
   - Use lazy session initialization
   - Pre-warm session in background after window shows
6. **Windows stuck on "Initializing"** (v1.4.0 fix):
   - **Root cause**: `pywebviewready` event fires before React useEffect registers listener
   - **Solution**: Early event capture in `index.html` before React loads
   - See `frontend/index.html` and `frontend/src/hooks/useApi.ts`

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
