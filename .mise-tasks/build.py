#!/usr/bin/env python3
# MISE description="Build native ROLLER installer binary with optimizations"
"""Build optimized ROLLER installer binary."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=None):
    """Run a command and handle errors."""
    if description:
        print(f"🔨 {description}...")

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)
    return result


def main():
    """Build the installer with optimizations."""

    # Build with PyInstaller
    print("📦 Building with PyInstaller...")
    pyinstaller_cmd = """
    poetry run pyinstaller \
      --onefile \
      --name roller-installer \
      --clean \
      --strip \
      --optimize 2 \
      --exclude-module tkinter \
      --exclude-module test \
      --exclude-module unittest \
      --exclude-module email \
      --exclude-module html \
      --exclude-module http \
      --exclude-module xml \
      --exclude-module pdb \
      --exclude-module multiprocessing \
      --exclude-module sqlite3 \
      main.py
    """
    run_command(pyinstaller_cmd, "Building installer")

    # Determine binary path
    if sys.platform == "win32":
        binary_path = Path("dist/roller-installer.exe")
    else:
        binary_path = Path("dist/roller-installer")

    if not binary_path.exists():
        print(f"❌ Binary not found at {binary_path}")
        sys.exit(1)

    # Get size before compression
    size_before = binary_path.stat().st_size / (1024 * 1024)
    print(f"📏 Size before UPX: {size_before:.2f} MB")

    # Compress with UPX
    print("🗜️  Compressing with UPX...")
    upx_cmd = f"upx --best --lzma {binary_path}"
    run_command(upx_cmd, "Applying UPX compression")

    # Show final size
    size_after = binary_path.stat().st_size / (1024 * 1024)
    reduction = ((size_before - size_after) / size_before) * 100

    print("✅ Build complete!")
    print(f"📏 Final size: {size_after:.2f} MB (reduced by {reduction:.1f}%)")
    print(f"📂 Binary location: {binary_path}")


if __name__ == "__main__":
    main()
