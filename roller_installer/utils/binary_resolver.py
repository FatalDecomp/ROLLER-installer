"""
Generic utility for resolving external binary paths with fallback strategy.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, List, Callable


class BinaryResolver:
    """
    Generic binary resolver with configurable search paths.

    Search order:
    1. tools/ directory (where binaries are installed)
    2. Additional custom paths
    3. Binary on system PATH
    4. Install via install script to tools/ (if provided)
    """

    def __init__(self, binary_name: str, custom_paths: Optional[List[Path]] = None,
                 install_script: Optional[Callable[[Path], bool]] = None,
                 install_dir: Optional[Path] = None):
        """
        Initialize binary resolver.

        Args:
            binary_name: Base name of the binary (without extension)
            custom_paths: Additional paths to search
            install_script: Optional function to install the binary if not found.
                           Takes a target directory Path and returns True on success.
            install_dir: Directory where binaries should be installed when using install_script.
                        If None, defaults to tools/ directory.
        """
        self.binary_name = binary_name
        self.custom_paths = custom_paths or []
        self.install_script = install_script
        self.exe_suffix = ".exe" if os.name == "nt" else ""
        self.full_name = f"{binary_name}{self.exe_suffix}"
        
        # Determine base directory
        if getattr(sys, 'frozen', False):
            # Running from PyInstaller bundle - base is next to executable
            base_dir = Path(sys.executable).parent
        else:
            # Running from source - base is project root
            base_dir = Path(__file__).parent.parent.parent
        
        # Set install directory - always use tools/ subdirectory
        if install_dir:
            self.install_dir = install_dir
        else:
            self.install_dir = base_dir / "tools"
            # Ensure tools directory exists
            self.install_dir.mkdir(parents=True, exist_ok=True)

    def find_binary(self) -> Optional[Path]:
        """
        Find binary using the search strategy.

        Returns:
            Path to binary if found, None otherwise
        """
        # 1. ALWAYS check tools directory first (where we install binaries)
        tools_binary = self.install_dir / self.full_name
        if tools_binary.exists() and tools_binary.is_file():
            return tools_binary

        # 2. Check custom paths
        for custom_path in self.custom_paths:
            binary_path = custom_path / self.full_name
            if binary_path.exists() and binary_path.is_file():
                return binary_path

        # 3. Check system PATH
        system_binary = shutil.which(self.binary_name)
        if system_binary:
            return Path(system_binary)

        # 4. Try install script if available
        if self.install_script:
            # Install in the tools directory
            if self.install_script(self.install_dir):
                # Check if installation succeeded
                if tools_binary.exists() and tools_binary.is_file():
                    return tools_binary

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

def _install_ubi(target_dir: Path) -> bool:
    """
    Install ubi using the bootstrap script.
    
    Args:
        target_dir: Directory to install ubi to
        
    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            if os.name == "nt":
                # Windows: Download PowerShell bootstrap script
                script_url = "https://raw.githubusercontent.com/houseabsolute/ubi/master/bootstrap/bootstrap-ubi.ps1"
                script_file = temp_path / "bootstrap-ubi.ps1"
                
                # Download the script
                with urllib.request.urlopen(script_url) as response:
                    script_content = response.read()
                script_file.write_bytes(script_content)
                
                # Execute the PowerShell script
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_file)],
                    capture_output=True,
                    text=True,
                    cwd=str(target_dir),
                    env={**os.environ, "TARGET": str(target_dir)}
                )
            else:
                # Unix-like: Download shell bootstrap script
                script_url = "https://raw.githubusercontent.com/houseabsolute/ubi/master/bootstrap/bootstrap-ubi.sh"
                script_file = temp_path / "bootstrap-ubi.sh"
                
                # Download the script
                with urllib.request.urlopen(script_url) as response:
                    script_content = response.read()
                script_file.write_bytes(script_content)
                
                # Make it executable
                script_file.chmod(0o755)
                
                # Execute the shell script
                result = subprocess.run(
                    ["sh", str(script_file)],
                    capture_output=True,
                    text=True,
                    cwd=str(target_dir),
                    env={**os.environ, "TARGET": str(target_dir)}
                )
            
            return result.returncode == 0
    except Exception:
        return False


def get_ubi_resolver(install_dir: Optional[Path] = None) -> BinaryResolver:
    """Get a resolver configured for ubi with automatic installation fallback.
    
    Args:
        install_dir: Optional directory where ubi should be installed.
                    If None, defaults to next to executable (or utils for source).
    """
    resolver = BinaryResolver("ubi", install_script=_install_ubi, install_dir=install_dir)
    resolver.error_message = (
        "ubi binary not found and automatic installation failed. Please ensure ubi is either:\n"
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
