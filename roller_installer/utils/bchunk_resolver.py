"""
Utility for resolving bchunk binary path - uses generic binary resolver.
"""

from pathlib import Path
from typing import Optional
from .binary_resolver import get_bchunk_resolver


def find_bchunk_binary() -> Optional[Path]:
    """
    Find bchunk binary with preference order:
    1. Local bchunk binary in same directory as this script
    2. Local bchunk binary in project root
    3. bchunk on system PATH

    Returns:
        Path to bchunk binary if found, None otherwise
    """
    resolver = get_bchunk_resolver()
    return resolver.find_binary()


def get_bchunk_command() -> str:
    """
    Get bchunk command path, raising error if not found.

    Returns:
        String path to bchunk binary

    Raises:
        RuntimeError: If bchunk binary cannot be found
    """
    resolver = get_bchunk_resolver()
    return resolver.get_command()


def check_bchunk_available() -> bool:
    """
    Check if bchunk binary is available without raising errors.

    Returns:
        True if bchunk is available, False otherwise
    """
    resolver = get_bchunk_resolver()
    return resolver.is_available()


if __name__ == "__main__":
    # Test the resolution
    bchunk_path = find_bchunk_binary()
    if bchunk_path:
        print(f"Found bchunk at: {bchunk_path}")

        # Test that it works
        import subprocess

        try:
            result = subprocess.run(
                [str(bchunk_path)], capture_output=True, text=True, timeout=5
            )
            # bchunk shows usage when run without args
            if "usage:" in result.stderr.lower() or "usage:" in result.stdout.lower():
                print("bchunk is working correctly")
            else:
                print(f"bchunk may not be working: {result.stderr or result.stdout}")
        except Exception as e:
            print(f"Failed to run bchunk: {e}")
    else:
        print("bchunk not found")