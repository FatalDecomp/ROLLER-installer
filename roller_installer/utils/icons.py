"""Cross-platform icon mapping for ROLLER Installer CLI."""

import sys

# Cross-platform emoji/text mapping for ROLLER Installer
# Uses emojis on Unix systems, text brackets on Windows for console compatibility
ICONS = {
    # Status icons
    "check": "✓" if sys.platform != "win32" else "[OK]",
    "success": "✅" if sys.platform != "win32" else "[SUCCESS]", 
    "warning": "⚠️" if sys.platform != "win32" else "[WARNING]",
    "error": "❌" if sys.platform != "win32" else "[ERROR]",
    "info": "ℹ️" if sys.platform != "win32" else "[INFO]",
    
    # Action icons
    "download": "📥" if sys.platform != "win32" else "[DOWNLOAD]",
    "tools": "🔧" if sys.platform != "win32" else "[TOOLS]",
    "install": "📦" if sys.platform != "win32" else "[INSTALL]",
    
    # Interface icons
    "rocket": "🚀" if sys.platform != "win32" else "[LAUNCH]",
    "desktop": "🖥️" if sys.platform != "win32" else "[TUI]",
    
    # Build-specific icons
    "build": "📦" if sys.platform != "win32" else "[BUILD]",
    "size": "📏" if sys.platform != "win32" else "[SIZE]",
    "compress": "🗜️" if sys.platform != "win32" else "[COMPRESS]",
    "folder": "📂" if sys.platform != "win32" else "[FOLDER]",
    "hammer": "🔨" if sys.platform != "win32" else "[BUILDING]",
}