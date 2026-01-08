#!/usr/bin/env python3
"""
Desktop application entry point
Cross-platform GUI using pywebview

Version: 1.3.0
- Optimized startup using webview.start(func) pattern
- Added window.events for proper lifecycle management
- Background session pre-warming for faster first login
- Platform-specific optimizations (Windows/macOS/Linux)

Based on pywebview best practices:
- https://pywebview.flowrl.com/guide/usage.html
- https://github.com/r0x0r/pywebview/issues/627
"""

import logging
import os
import platform
import sys
import threading
from typing import Optional, Callable

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
APP_VERSION = '1.3.0'
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

    Platform-specific behavior:
    - Windows: Auto-detect (EdgeChromium > EdgeHTML > MSHTML)
    - macOS: Auto-detect (Cocoa WebKit)
    - Linux: Explicitly use GTK with WebKit2
    """
    system = platform.system().lower()

    if system == 'linux':
        # Linux: Explicitly use GTK with WebKit2
        return 'gtk'
    else:
        # Windows/macOS: Let pywebview auto-detect the best renderer
        # Avoid manual detection which can slow down startup
        return None


def setup_platform_specific() -> None:
    """
    Apply platform-specific configurations before window creation

    This runs on the main thread before webview.start()
    """
    system = platform.system().lower()

    if system == 'darwin':
        # macOS: Enable high-DPI support
        try:
            from AppKit import NSApplication
            NSApplication.sharedApplication()
        except ImportError:
            pass

    elif system == 'windows':
        # Windows: Enable DPI awareness for crisp rendering on 4K displays
        try:
            import ctypes
            # PROCESS_PER_MONITOR_DPI_AWARE = 2
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass


def create_window(api: EvaluationAPI) -> webview.Window:
    """
    Create and configure the main application window

    Window is created but not shown until webview.start() is called.
    This allows for faster perceived startup.
    """
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


def on_window_shown(api: EvaluationAPI) -> Callable[[], None]:
    """
    Factory function that returns window shown event handler

    This runs when the window is first displayed to the user.
    Use this for non-critical initialization that can happen after UI shows.
    """
    def handler():
        logger.info("Window shown - starting background initialization")

        # Pre-warm session in background thread
        # This makes the first login faster
        def prewarm_session():
            try:
                # Access the session property to trigger lazy initialization
                _ = api.session
                logger.info("HTTP session pre-warmed successfully")
            except Exception as e:
                logger.warning(f"Session pre-warm failed (non-critical): {e}")

        # Run in daemon thread so it doesn't block app exit
        threading.Thread(
            target=prewarm_session,
            daemon=True,
            name="SessionPrewarm"
        ).start()

    return handler


def on_window_loaded(window: webview.Window) -> Callable[[], None]:
    """
    Factory function that returns DOM loaded event handler

    This runs when the frontend HTML/JS has fully loaded.
    """
    def handler():
        logger.info("Frontend loaded - DOM ready")
        # Notify frontend that Python backend is ready
        try:
            window.evaluate_js("window.dispatchEvent(new Event('pythonReady'))")
        except Exception as e:
            logger.debug(f"Could not dispatch pythonReady event: {e}")

    return handler


def on_window_closing(api: EvaluationAPI) -> Callable[[], bool]:
    """
    Factory function that returns window closing event handler

    Returns True to allow closing, False to prevent.
    """
    def handler():
        logger.info("Window closing - cleaning up")
        api.stop_evaluation()
        return True

    return handler


def on_startup(window: webview.Window, api: EvaluationAPI) -> None:
    """
    Startup callback executed in a separate thread after webview.start()

    This is the recommended pywebview pattern for background initialization.
    The GUI loop is running, so the window stays responsive.

    See: https://pywebview.flowrl.com/guide/usage.html
    """
    logger.info("Startup callback running in background thread")

    # Register event handlers
    # Note: Events must be registered after start() is called
    window.events.shown += on_window_shown(api)
    window.events.loaded += on_window_loaded(window)
    window.events.closing += on_window_closing(api)

    logger.info("Event handlers registered")


def main() -> None:
    """
    Application entry point

    Startup sequence:
    1. Platform-specific setup (DPI awareness, etc.)
    2. Create API instance (minimal initialization)
    3. Create window (not shown yet)
    4. Start webview with callback
    5. Callback registers events and does background init
    6. Window shows with loading spinner
    7. Frontend loads and becomes interactive
    """
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")

    # Step 1: Platform-specific setup (must be before window creation)
    setup_platform_specific()

    # Step 2: Initialize API (minimal - uses lazy initialization)
    api = EvaluationAPI()

    # Step 3: Create window
    try:
        window = create_window(api)
    except FileNotFoundError as e:
        logger.error(str(e))
        print(f"Error: {e}")
        sys.exit(1)

    # Store window reference for JavaScript callbacks
    api.set_window(window)

    # Step 4: Get optimal GUI backend
    gui = get_gui_backend()
    logger.info(f"Using GUI backend: {gui or 'auto'}")

    # Step 5: Start application with startup callback
    # The callback runs in a separate thread, keeping GUI responsive
    # See: https://pywebview.flowrl.com/guide/usage.html
    webview.start(
        func=on_startup,
        args=(window, api),
        debug=os.environ.get('DEBUG', '').lower() in ('1', 'true'),
        gui=gui,
        http_server=True,  # Required for proper asset loading
    )

    logger.info("Application closed")


if __name__ == '__main__':
    main()
