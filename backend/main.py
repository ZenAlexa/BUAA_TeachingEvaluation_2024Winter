#!/usr/bin/env python3
"""
Desktop application entry point
Cross-platform GUI using pywebview
"""

import os
import sys

import webview

from .api import EvaluationAPI


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


def main():
    """Application entry point"""
    api = EvaluationAPI()

    # Load frontend
    html_path = get_resource_path('web/index.html')

    # Create window
    window = webview.create_window(
        title='BUAA Evaluation',
        url=html_path,
        width=520,
        height=720,
        resizable=True,
        min_size=(400, 600),
        js_api=api,
        background_color='#050505'
    )

    # Store window reference for JavaScript callbacks
    api.set_window(window)

    # Start application
    webview.start(debug=False)


if __name__ == '__main__':
    main()
