"""
Utility for resolving ubi binary path - uses generic binary resolver.
"""

from pathlib import Path
from typing import Optional
from .binary_resolver import get_ubi_resolver


def find_ubi_binary() -> Optional[Path]:
    """
    Find ubi binary with preference order:
    1. Local ubi binary in same directory as this script
    2. Local ubi binary in project root
    3. ubi on system PATH

    Returns:
        Path to ubi binary if found, None otherwise
    """
    resolver = get_ubi_resolver()
    return resolver.find_binary()


def get_ubi_command() -> str:
    """
    Get ubi command path, raising error if not found.

    Returns:
        String path to ubi binary

    Raises:
        RuntimeError: If ubi binary cannot be found
    """
    resolver = get_ubi_resolver()
    return resolver.get_command()


def check_ubi_available() -> bool:
    """
    Check if ubi binary is available without raising errors.

    Returns:
        True if ubi is available, False otherwise
    """
    resolver = get_ubi_resolver()
    return resolver.is_available()


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