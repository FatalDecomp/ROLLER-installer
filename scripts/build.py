#!/usr/bin/env python3
"""Build optimized ROLLER installer binary."""

import subprocess
import sys
from pathlib import Path
from roller_installer.utils.icons import ICONS


def run_command(cmd, description=None):
    """Run a command and handle errors."""
    if description:
        print(f"{ICONS['hammer']} {description}...")

    # Stream output in real-time
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Print output as it comes
    for line in process.stdout:
        print(line, end="")

    process.wait()

    if process.returncode != 0:
        print(f"{ICONS['error']} Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)

    return process


def main():
    """Build the installer with optimizations."""

    # Build with PyInstaller
    print(f"{ICONS['build']} Building with PyInstaller...")

    # Use different flags based on platform
    if sys.platform == "win32":
        # Simplified build for Windows - avoid problematic optimizations
        pyinstaller_cmd = """
        poetry run pyinstaller \
          --onefile \
          --name roller-installer \
          --clean \
          --hidden-import roller_installer.core.handlers.zip_handler \
          --hidden-import roller_installer.core.handlers.iso_handler \
          --hidden-import roller_installer.core.handlers.cue_bin_handler \
          main.py
        """
    else:
        # Full optimizations for Unix systems
        pyinstaller_cmd = """
        poetry run pyinstaller \
          --onefile \
          --name roller-installer \
          --clean \
          --strip \
          --optimize 2 \
          --hidden-import roller_installer.core.handlers.zip_handler \
          --hidden-import roller_installer.core.handlers.iso_handler \
          --hidden-import roller_installer.core.handlers.cue_bin_handler \
          --exclude-module tkinter \
          --exclude-module test \
          --exclude-module unittest \
          --exclude-module pdb \
          --exclude-module multiprocessing \
          --exclude-module sqlite3 \
          --exclude-module numpy \
          --exclude-module pandas \
          --exclude-module matplotlib \
          --exclude-module PIL \
          --exclude-module cv2 \
          main.py
        """
    run_command(pyinstaller_cmd, "Building installer")

    # Determine binary path
    if sys.platform == "win32":
        binary_path = Path("dist/roller-installer.exe")
    else:
        binary_path = Path("dist/roller-installer")

    if not binary_path.exists():
        print(f"{ICONS['error']} Binary not found at {binary_path}")
        sys.exit(1)

    # Get final size
    final_size = binary_path.stat().st_size / (1024 * 1024)
    
    print(f"{ICONS['success']} Build complete!")
    print(f"{ICONS['size']} Final size: {final_size:.2f} MB")

    print(f"{ICONS['folder']} Binary location: {binary_path}")


if __name__ == "__main__":
    main()
