"""
Generic utility for resolving external binary paths with fallback strategy.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List


class BinaryResolver:
    """
    Generic binary resolver with configurable search paths.

    Search order:
    1. Local binary in same directory as script
    2. Local binary in project root
    3. Binary on system PATH
    4. Additional custom paths
    """

    def __init__(self, binary_name: str, custom_paths: Optional[List[Path]] = None):
        """
        Initialize binary resolver.

        Args:
            binary_name: Base name of the binary (without extension)
            custom_paths: Additional paths to search
        """
        self.binary_name = binary_name
        self.custom_paths = custom_paths or []
        self.exe_suffix = ".exe" if os.name == "nt" else ""
        self.full_name = f"{binary_name}{self.exe_suffix}"

    def find_binary(self) -> Optional[Path]:
        """
        Find binary using the search strategy.

        Returns:
            Path to binary if found, None otherwise
        """
        # 1. Check same directory as this script
        script_dir = Path(__file__).parent
        local_binary = script_dir / self.full_name
        if local_binary.exists() and local_binary.is_file():
            return local_binary

        # 2. Check project root (assuming roller_installer is in project root)
        project_root = script_dir.parent.parent
        root_binary = project_root / self.full_name
        if root_binary.exists() and root_binary.is_file():
            return root_binary

        # 3. Check custom paths
        for custom_path in self.custom_paths:
            binary_path = custom_path / self.full_name
            if binary_path.exists() and binary_path.is_file():
                return binary_path

        # 4. Check system PATH
        system_binary = shutil.which(self.binary_name)
        if system_binary:
            return Path(system_binary)

        return None

    def get_command(self, error_message: Optional[str] = None) -> str:
        """
        Get binary command path, raising error if not found.

        Args:
            error_message: Custom error message

        Returns:
            String path to binary

        Raises:
            RuntimeError: If binary cannot be found
        """
        binary_path = self.find_binary()
        if binary_path is None:
            if not error_message:
                error_message = (
                    f"{self.binary_name} binary not found. Please ensure {self.binary_name} is either:\n"
                    f"1. Bundled alongside the installer\n"
                    f"2. Available in your system PATH"
                )
            raise RuntimeError(error_message)

        return str(binary_path)

    def is_available(self) -> bool:
        """
        Check if binary is available without raising errors.

        Returns:
            True if binary is available, False otherwise
        """
        return self.find_binary() is not None

    def verify_working(self, test_args: Optional[List[str]] = None,
                      expected_output: Optional[str] = None,
                      check_stderr: bool = True) -> bool:
        """
        Verify that the binary is working correctly.

        Args:
            test_args: Arguments to pass for testing (default: --version or -h)
            expected_output: String expected in output
            check_stderr: Also check stderr for expected output

        Returns:
            True if binary appears to be working
        """
        binary_path = self.find_binary()
        if not binary_path:
            return False

        if test_args is None:
            # Try common version/help flags
            test_args = ["--version"]

        try:
            result = subprocess.run(
                [str(binary_path)] + test_args,
                capture_output=True,
                text=True,
                timeout=5
            )

            # If we have expected output, check for it
            if expected_output:
                output = result.stdout.lower()
                if check_stderr:
                    output += " " + result.stderr.lower()
                return expected_output.lower() in output

            # Otherwise just check for reasonable exit codes
            # Many tools return 1 for help, so accept 0 or 1
            return result.returncode in (0, 1)

        except (subprocess.SubprocessError, FileNotFoundError):
            return False


# Convenience functions for specific binaries

def get_ubi_resolver() -> BinaryResolver:
    """Get a resolver configured for ubi."""
    resolver = BinaryResolver("ubi")
    resolver.error_message = (
        "ubi binary not found. Please ensure ubi is either:\n"
        "1. Bundled alongside the installer\n"
        "2. Available in your system PATH\n"
        "3. Download from: https://github.com/houseabsolute/ubi"
    )
    return resolver


def get_bchunk_resolver() -> BinaryResolver:
    """Get a resolver configured for bchunk."""
    resolver = BinaryResolver("bchunk")
    resolver.error_message = (
        "bchunk binary not found. Please ensure bchunk is either:\n"
        "1. Bundled alongside the installer\n"
        "2. Available in your system PATH\n"
        "3. Build from source: https://github.com/extramaster/bchunk"
    )
    return resolver
