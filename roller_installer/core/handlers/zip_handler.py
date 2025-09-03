"""ZIP file handler for asset extraction."""

import zipfile
import logging
from pathlib import Path
from typing import Optional

from ..asset_extractor import BaseAssetHandler, ExtractionResult

logger = logging.getLogger(__name__)


class ZipHandler(BaseAssetHandler):
    """Handler for ZIP archive files."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a valid ZIP archive."""
        try:
            with zipfile.ZipFile(file_path, "r"):
                # Try to read the ZIP file header
                return True
        except (zipfile.BadZipFile, OSError):
            return False

    def find_fatdata_path(self, source_path: Path) -> Optional[str]:
        """Find FATDATA directory in ZIP archive (case-insensitive)."""
        try:
            with zipfile.ZipFile(source_path, "r") as zf:
                # Get all directory paths in the ZIP
                all_paths = set()
                for name in zf.namelist():
                    # Add all parent directories
                    parts = Path(name).parts
                    for i in range(1, len(parts) + 1):
                        dir_path = "/".join(parts[:i])
                        if dir_path.endswith("/") or i < len(parts):
                            all_paths.add(dir_path.rstrip("/"))

                # Look for FATDATA (case-insensitive)
                for path in all_paths:
                    path_parts = path.split("/")
                    for part in path_parts:
                        if part.lower() == "fatdata":
                            # Find the full path to this FATDATA directory
                            fatdata_index = path_parts.index(part)
                            fatdata_path = "/".join(path_parts[: fatdata_index + 1])
                            logger.debug(f"Found FATDATA at: {fatdata_path}")
                            return fatdata_path

                return None

        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file {source_path}: {e}")
            return None

    def extract_fatdata(self, source_path: Path, output_dir: Path) -> ExtractionResult:
        """Extract FATDATA directory from ZIP archive."""
        fatdata_path = self.find_fatdata_path(source_path)
        if not fatdata_path:
            raise FileNotFoundError(f"FATDATA directory not found in {source_path}")

        output_fatdata_dir = output_dir / "fatdata"
        output_fatdata_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(source_path, "r") as zf:
                # Find all files within the FATDATA directory
                fatdata_files = []
                for name in zf.namelist():
                    # Check if this file is within our FATDATA directory
                    if name.startswith(fatdata_path + "/") or name == fatdata_path:
                        # Skip directories themselves
                        if not name.endswith("/"):
                            fatdata_files.append(name)

                if not fatdata_files:
                    raise FileNotFoundError(
                        f"No files found in FATDATA directory at {fatdata_path}"
                    )

                logger.info(
                    f"Extracting {len(fatdata_files)} files from FATDATA directory"
                )

                # Extract each file
                for file_name in fatdata_files:
                    # Calculate relative path within FATDATA
                    if file_name.startswith(fatdata_path + "/"):
                        relative_path = file_name[len(fatdata_path) + 1 :]
                    else:
                        relative_path = Path(file_name).name

                    # Create target path
                    target_path = output_fatdata_dir / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Extract file
                    with (
                        zf.open(file_name) as source,
                        open(target_path, "wb") as target,
                    ):
                        target.write(source.read())

                    logger.debug(f"Extracted: {file_name} -> {target_path}")

                logger.info(f"Successfully extracted FATDATA to: {output_fatdata_dir}")
                return ExtractionResult(fatdata_path=output_fatdata_dir)

        except zipfile.BadZipFile as e:
            raise RuntimeError(f"Failed to read ZIP file {source_path}: {e}")
        except OSError as e:
            raise RuntimeError(f"Failed to extract files from {source_path}: {e}")
