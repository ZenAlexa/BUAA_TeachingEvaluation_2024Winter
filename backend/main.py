#!/usr/bin/env python3
"""
Desktop application entry point
Cross-platform GUI using pywebview

Version: 1.2.0
- Improved cross-platform compatibility
- Added proper GUI backend selection
- Better error handling and logging
"""

import logging
import os
import platform
import sys
from typing import Optional

# Add parent directory to path for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    sys.path.insert(0, sys._MEIPASS)
else:
    # Running in development
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import webview

from api import EvaluationAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application constants
APP_TITLE = 'BUAA Evaluation'
APP_VERSION = '1.2.0'
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 720
MIN_WIDTH = 400
MIN_HEIGHT = 600
BACKGROUND_COLOR = '#050505'


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource file
    Works both in development and when packaged with PyInstaller
    """
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def get_gui_backend() -> Optional[str]:
    """
    Determine the best GUI backend for the current platform

    Returns:
        GUI backend name or None for auto-detection
    """
    system = platform.system().lower()

    if system == 'darwin':
        # macOS: Use Cocoa (default)
        return None
    elif system == 'windows':
        # Windows: Prefer EdgeChromium for better performance
        try:
            import clr  # pythonnet for .NET interop
            return 'edgechromium'
        except ImportError:
            # Fall back to MSHTML if EdgeChromium not available
            return None
    elif system == 'linux':
        # Linux: Use GTK with WebKit2
        return 'gtk'
    else:
        return None


def setup_platform_specific() -> None:
    """Apply platform-specific configurations"""
    system = platform.system().lower()

    if system == 'darwin':
        # macOS: Enable high-DPI support
        try:
            from AppKit import NSApplication, NSApp
            NSApplication.sharedApplication()
        except ImportError:
            pass

    elif system == 'windows':
        # Windows: Enable DPI awareness for crisp rendering
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass


def create_window(api: EvaluationAPI) -> webview.Window:
    """Create and configure the main application window"""
    html_path = get_resource_path('web/index.html')

    if not os.path.exists(html_path):
        logger.error(f"Frontend not found: {html_path}")
        raise FileNotFoundError(f"Frontend not found: {html_path}")

    window = webview.create_window(
        title=f'{APP_TITLE} v{APP_VERSION}',
        url=html_path,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        js_api=api,
        background_color=BACKGROUND_COLOR,
        text_select=False,  # Disable text selection for app-like feel
    )

    return window


def on_closing(api: EvaluationAPI) -> bool:
    """Handle window close event"""
    # Stop any running evaluation
    api.stop_evaluation()
    return True


def main() -> None:
    """Application entry point"""
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")

    # Apply platform-specific setup
    setup_platform_specific()

    # Initialize API
    api = EvaluationAPI()

    # Create window
    try:
        window = create_window(api)
    except FileNotFoundError as e:
        logger.error(str(e))
        print(f"Error: {e}")
        sys.exit(1)

    # Store window reference for JavaScript callbacks
    api.set_window(window)

    # Set up closing handler
    window.events.closing += lambda: on_closing(api)

    # Get optimal GUI backend
    gui = get_gui_backend()

    # Start application
    logger.info(f"Starting webview with GUI: {gui or 'auto'}")
    webview.start(
        debug=os.environ.get('DEBUG', '').lower() in ('1', 'true'),
        gui=gui,
        http_server=True,  # Use HTTP server for better compatibility
    )

    logger.info("Application closed")


if __name__ == '__main__':
    main()
