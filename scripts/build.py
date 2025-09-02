#!/usr/bin/env python3
"""Build optimized ROLLER installer binary."""

import subprocess
import sys
from pathlib import Path
from icons import ICONS


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

    # Get size before compression
    size_before = binary_path.stat().st_size / (1024 * 1024)
    print(f"{ICONS['size']} Size before UPX: {size_before:.2f} MB")

    # Try to compress with UPX if available
    upx_result = subprocess.run(["which", "upx"], capture_output=True)
    if upx_result.returncode == 0:
        print(f"{ICONS['compress']} Compressing with UPX...")
        upx_cmd = f"upx --best --lzma {binary_path}"
        try:
            run_command(upx_cmd, "Applying UPX compression")

            # Show final size with compression
            size_after = binary_path.stat().st_size / (1024 * 1024)
            reduction = ((size_before - size_after) / size_before) * 100
            print(f"{ICONS['success']} Build complete!")
            print(
                f"{ICONS['size']} Final size: {size_after:.2f} MB (reduced by {reduction:.1f}%)"
            )
        except Exception as e:
            print(f"{ICONS['warning']} UPX compression failed: {e}")
            print(f"{ICONS['success']} Build complete!")
            print(f"{ICONS['size']} Final size: {size_before:.2f} MB (uncompressed)")
    else:
        print(f"{ICONS['info']} UPX not found, skipping compression")
        print(f"{ICONS['success']} Build complete!")
        print(f"{ICONS['size']} Final size: {size_before:.2f} MB (uncompressed)")

    print(f"{ICONS['folder']} Binary location: {binary_path}")


if __name__ == "__main__":
    main()
