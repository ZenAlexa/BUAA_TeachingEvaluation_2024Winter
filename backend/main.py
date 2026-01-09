#!/usr/bin/env python3
"""
Desktop application entry point
Cross-platform GUI using pywebview

Version: 1.5.0
- CRITICAL FIX: Removed http_server=True which caused Windows freezing
- CRITICAL FIX: Event registration before webview.start()
- CRITICAL FIX: Simplified startup flow to prevent deadlocks
- Added polling-based ready detection for frontend
- Improved logging for debugging
"""

import logging
import os
import platform
import sys
from typing import Optional

# Add parent directory to path for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import webview

from api import EvaluationAPI

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get('DEBUG') else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application constants
APP_TITLE = 'BUAA Evaluation'
APP_VERSION = '1.5.0'
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 720
MIN_WIDTH = 400
MIN_HEIGHT = 600
BACKGROUND_COLOR = '#050505'


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource file"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_gui_backend() -> Optional[str]:
    """Determine the best GUI backend for the current platform"""
    system = platform.system().lower()
    if system == 'linux':
        return 'gtk'
    # Windows/macOS: auto-detect
    return None


def setup_dpi_awareness() -> None:
    """Set up DPI awareness for high-resolution displays"""
    system = platform.system().lower()

    if system == 'windows':
        try:
            import ctypes
            # Try modern API first
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (AttributeError, OSError):
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception as e:
            logger.debug(f"DPI awareness setup failed: {e}")

    elif system == 'darwin':
        try:
            from AppKit import NSApplication
            NSApplication.sharedApplication()
        except ImportError:
            pass


def main() -> None:
    """Application entry point"""
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")

    # DPI setup must be before window creation
    setup_dpi_awareness()

    # Initialize API (minimal - uses lazy initialization)
    api = EvaluationAPI()

    # Find frontend HTML
    html_path = get_resource_path('web/index.html')
    if not os.path.exists(html_path):
        logger.error(f"Frontend not found: {html_path}")
        print(f"Error: Frontend not found at {html_path}")
        sys.exit(1)

    logger.info(f"Loading frontend from: {html_path}")

    # Create window
    # CRITICAL: Do NOT use http_server=True on Windows - it causes freezing
    window = webview.create_window(
        title=f'{APP_TITLE} v{APP_VERSION}',
        url=html_path,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        js_api=api,
        background_color=BACKGROUND_COLOR,
        text_select=False,
    )

    # Store window reference immediately
    api.set_window(window)

    # Register event handlers BEFORE start()
    # This ensures we don't miss any events
    def on_loaded():
        logger.info("Frontend DOM loaded")
        api.mark_ready()

    def on_closing():
        logger.info("Window closing")
        api.stop_evaluation()
        return True

    window.events.loaded += on_loaded
    window.events.closing += on_closing

    # Get GUI backend
    gui = get_gui_backend()
    logger.info(f"GUI backend: {gui or 'auto'}")

    # Start application
    # CRITICAL: No http_server parameter - use direct file loading
    debug_mode = os.environ.get('DEBUG', '').lower() in ('1', 'true')

    logger.info("Starting webview...")
    webview.start(
        gui=gui,
        debug=debug_mode,
    )

    logger.info("Application closed")


if __name__ == '__main__':
    main()
