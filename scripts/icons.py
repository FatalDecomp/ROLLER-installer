#!/usr/bin/env python3
"""Cross-platform icon mapping for build scripts."""

import sys

# Cross-platform emoji/text mapping
# Uses emojis on Unix systems, text brackets on Windows for console compatibility
ICONS = {
    "build": "📦" if sys.platform != "win32" else "[BUILD]",
    "size": "📏" if sys.platform != "win32" else "[SIZE]",
    "compress": "🗜️" if sys.platform != "win32" else "[COMPRESS]",
    "success": "✅" if sys.platform != "win32" else "[OK]",
    "warning": "⚠️" if sys.platform != "win32" else "[WARNING]",
    "error": "❌" if sys.platform != "win32" else "[ERROR]",
    "info": "ℹ️" if sys.platform != "win32" else "[INFO]",
    "folder": "📂" if sys.platform != "win32" else "[FOLDER]",
    "hammer": "🔨" if sys.platform != "win32" else "[BUILDING]",
    "search": "🔍" if sys.platform != "win32" else "[ANALYZE]",
    "sparkles": "✨" if sys.platform != "win32" else "[COMPLETE]",
    "file": "📄" if sys.platform != "win32" else "[FILE]",
    "lightbulb": "💡" if sys.platform != "win32" else "[TIP]",
}
