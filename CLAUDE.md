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

### Python-to-JavaScript Communication

**CRITICAL**: When calling frontend functions via `_call_frontend()`, Python values must be converted to JS syntax:
- `True` → `true` (not `'True'`)
- `False` → `false` (not `'False'`)
- `None` → `null`

Use `_python_to_js()` helper in `api.py` for proper conversion.

### Threading

Long-running operations (like `start_evaluation`) run in background threads to prevent UI freeze. Use `threading.Thread` with `daemon=True`.

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
2. **UI freeze**: Long operation on main thread - use threading
3. **Request timeout**: Add timeout to all `requests` calls
4. **Windows blurry**: Ensure DPI awareness is set in `main.py`
