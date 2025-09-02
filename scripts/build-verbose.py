#!/usr/bin/env python3
"""Build with verbose logging for analysis."""

import subprocess
import sys
from icons import ICONS


def main():
    """Build with verbose output."""

    print(f"{ICONS['build']} Building with verbose output...")

    # Build command with verbose logging
    cmd = [
        "poetry",
        "run",
        "pyinstaller",
        "--onefile",
        "--name",
        "roller-installer",
        "--clean",
        "--strip",
        "--optimize",
        "2",
        "--log-level",
        "DEBUG",
        "--exclude-module",
        "tkinter",
        "--exclude-module",
        "test",
        "--exclude-module",
        "unittest",
        "--exclude-module",
        "pdb",
        "--exclude-module",
        "multiprocessing",
        "--exclude-module",
        "sqlite3",
        "main.py",
    ]

    # Run with output capture to file
    with open("build.log", "w") as log_file:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )

        # Stream output to both console and file
        for line in process.stdout:
            print(line, end="")
            log_file.write(line)

        process.wait()

        if process.returncode != 0:
            print(f"{ICONS['error']} Build failed with exit code {process.returncode}")
            sys.exit(process.returncode)

    # Check for UPX
    upx_check = subprocess.run(["which", "upx"], capture_output=True, text=True)
    if upx_check.returncode == 0:
        upx_path = upx_check.stdout.strip()
        print(f"\n{ICONS['success']} UPX found at: {upx_path}")

        version_result = subprocess.run(
            ["upx", "--version"], capture_output=True, text=True
        )
        if version_result.returncode == 0:
            version_line = version_result.stdout.split("\n")[0]
            print(f"   Version: {version_line}")
    else:
        print(f"\n{ICONS['warning']} UPX not found")

    print(f"\n{ICONS['file']} Build log saved to build.log")
    print(f"{ICONS['info']} Run 'mise run build:analyze' to analyze the build")


if __name__ == "__main__":
    main()
