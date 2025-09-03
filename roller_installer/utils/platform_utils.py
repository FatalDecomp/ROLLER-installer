"""Platform detection and utilities."""

import logging
import platform
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_platform_identifier() -> str:
    """Return platform identifier for asset matching.

    Returns:
        Platform identifier string (e.g., 'windows-x64', 'linux-x64', 'macos-arm64')
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize system names
    if system == "darwin":
        system = "macos"

    # Normalize architecture names
    arch_map = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}

    arch = arch_map.get(machine, machine)

    return f"{system}-{arch}"


def get_executable_extension() -> str:
    """Return appropriate executable extension for platform.

    Returns:
        '.exe' for Windows, empty string for Unix-like systems
    """
    return ".exe" if platform.system() == "Windows" else ""


def get_default_install_dir() -> Path:
    """Get platform-appropriate default installation directory.

    Returns:
        Default installation path for ROLLER
    """
    system = platform.system()

    if system == "Windows":
        # Try %LOCALAPPDATA% first, fall back to Program Files
        local_appdata = Path.home() / "AppData" / "Local"
        if local_appdata.exists():
            return local_appdata / "Programs" / "ROLLER"
        return Path("C:/Program Files/ROLLER")

    elif system == "Darwin":  # macOS
        return Path.home() / "Applications" / "ROLLER"

    else:  # Linux and other Unix-like
        # Use XDG_DATA_HOME if set, otherwise ~/.local/share
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data) / "ROLLER"
        return Path.home() / ".local" / "share" / "ROLLER"


def get_config_dir() -> Path:
    """Get platform-appropriate configuration directory.

    Returns:
        Configuration directory path for ROLLER
    """
    system = platform.system()

    if system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "ROLLER"

    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "ROLLER"

    else:  # Linux and other Unix-like
        # Use XDG_CONFIG_HOME if set, otherwise ~/.config
        import os

        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "ROLLER"
        return Path.home() / ".config" / "ROLLER"


def is_admin() -> bool:
    """Check if the current process has administrator/root privileges.

    Returns:
        True if running with elevated privileges, False otherwise
    """
    system = platform.system()

    if system == "Windows":
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False

    else:  # Unix-like systems
        import os

        return os.geteuid() == 0


def get_desktop_dir() -> Optional[Path]:
    """Get the user's desktop directory.

    Returns:
        Path to desktop directory, or None if not found
    """
    system = platform.system()

    if system == "Windows":
        return Path.home() / "Desktop"

    elif system == "Darwin":  # macOS
        return Path.home() / "Desktop"

    else:  # Linux
        # Try XDG_DESKTOP_DIR first
        import subprocess

        try:
            result = subprocess.run(
                ["xdg-user-dir", "DESKTOP"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting desktop directory: {e}")

        # Fall back to ~/Desktop
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return desktop

        return None
