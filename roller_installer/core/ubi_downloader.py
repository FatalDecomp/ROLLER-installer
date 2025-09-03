"""UBI-based downloader for ROLLER binaries."""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable
from roller_installer.utils.ubi_resolver import get_ubi_command, check_ubi_available

logger = logging.getLogger(__name__)


class UbiDownloader:
    """Handles downloading ROLLER binaries using ubi."""

    def __init__(self):
        """Initialize UBI downloader for fataldecomp/roller repository."""
        self.repo_name = "FatalDecomp/ROLLER"
        self.ubi_command = get_ubi_command()

    def download(
        self,
        install_dir: Path,
        tag: str,
        exe_name: str = "roller",
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        """Download ROLLER binary using ubi.

        Args:
            install_dir: Directory to install the binary
            tag: Release tag to download
            exe_name: Name for the executable
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the downloaded binary

        Raises:
            RuntimeError: If download fails
        """
        install_dir = Path(install_dir)
        install_dir.mkdir(parents=True, exist_ok=True)

        # Build ubi command
        cmd = [
            self.ubi_command,
            "--project",
            self.repo_name,
            "--tag",
            tag,
            "--in",
            str(install_dir),
            "--extract-all",
        ]

        logger.info(f"Running ubi command: {' '.join(cmd)}")

        if progress_callback:
            progress_callback(f"Downloading ROLLER {tag}...")

        try:
            # Run ubi with output capture
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                error_msg = f"ubi download failed: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # Return the install directory since we extracted all files
            logger.info(f"Successfully extracted all ROLLER files to: {install_dir}")

            if progress_callback:
                progress_callback(f"Extracted all ROLLER {tag} files successfully")

            return install_dir

        except subprocess.SubprocessError as e:
            error_msg = f"Failed to run ubi: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def verify_ubi_available(self) -> bool:
        """Check if ubi is available and working.

        Returns:
            True if ubi is available, False otherwise
        """
        if not check_ubi_available():
            return False

        try:
            result = subprocess.run(
                [self.ubi_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
