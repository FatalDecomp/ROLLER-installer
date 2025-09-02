"""
Utility for resolving ubi binary path with fallback strategy.
"""

import os
import shutil
from pathlib import Path
from typing import Optional


def find_ubi_binary() -> Optional[Path]:
    """
    Find ubi binary with preference order:
    1. Local ubi binary in same directory as this script
    2. Local ubi binary in project root
    3. ubi on system PATH

    Returns:
        Path to ubi binary if found, None otherwise
    """
    exe_suffix = ".exe" if os.name == "nt" else ""
    ubi_name = f"ubi{exe_suffix}"

    # 1. Check same directory as this script
    script_dir = Path(__file__).parent
    local_ubi = script_dir / ubi_name
    if local_ubi.exists() and local_ubi.is_file():
        return local_ubi

    # 2. Check project root (assuming roller_installer is in project root)
    project_root = script_dir.parent.parent
    root_ubi = project_root / ubi_name
    if root_ubi.exists() and root_ubi.is_file():
        return root_ubi

    # 3. Check system PATH
    system_ubi = shutil.which("ubi")
    if system_ubi:
        return Path(system_ubi)

    return None


def get_ubi_command() -> str:
    """
    Get ubi command path, raising error if not found.

    Returns:
        String path to ubi binary

    Raises:
        RuntimeError: If ubi binary cannot be found
    """
    ubi_path = find_ubi_binary()
    if ubi_path is None:
        raise RuntimeError(
            "ubi binary not found. Please ensure ubi is either:\n"
            "1. Bundled alongside the installer\n"
            "2. Available in your system PATH\n"
            "3. Download from: https://github.com/houseabsolute/ubi"
        )

    return str(ubi_path)


def check_ubi_available() -> bool:
    """
    Check if ubi binary is available without raising errors.

    Returns:
        True if ubi is available, False otherwise
    """
    return find_ubi_binary() is not None


if __name__ == "__main__":
    # Test the resolution
    ubi_path = find_ubi_binary()
    if ubi_path:
        print(f"Found ubi at: {ubi_path}")

        # Test that it works
        import subprocess

        try:
            result = subprocess.run(
                [str(ubi_path), "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"ubi version: {result.stdout.strip()}")
            else:
                print(f"ubi error: {result.stderr}")
        except Exception as e:
            print(f"Failed to run ubi: {e}")
    else:
        print("ubi not found")
