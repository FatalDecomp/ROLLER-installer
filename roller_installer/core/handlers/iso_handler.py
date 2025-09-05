"""ISO file handler for asset extraction with audio support."""

import logging
from pathlib import Path
from typing import Optional

import pycdlib

from ..asset_extractor import BaseAssetHandler, ExtractionResult

logger = logging.getLogger(__name__)


class IsoHandler(BaseAssetHandler):
    """Handler for ISO disc image files."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a valid ISO image."""
        try:
            iso = pycdlib.PyCdlib()
            iso.open(str(file_path))
            iso.close()
            return True
        except Exception:
            return False

    def find_fatdata_path(self, source_path: Path) -> Optional[str]:
        """Find FATDATA directory in ISO root (case-insensitive)."""
        try:
            iso = pycdlib.PyCdlib()
            iso.open(str(source_path))

            try:
                # List root directory entries
                for child in iso.list_children(iso_path="/"):
                    if child.file_identifier().decode("utf-8").upper() == "FATDATA":
                        logger.debug("Found FATDATA directory in ISO root")
                        return "/FATDATA"  # ISO paths are uppercase by convention

                return None

            finally:
                iso.close()

        except Exception as e:
            logger.error(f"Error reading ISO file {source_path}: {e}")
            return None

    def extract_fatdata(self, source_path: Path, output_dir: Path) -> ExtractionResult:
        """Extract FATDATA directory and audio tracks from ISO."""
        fatdata_path = self.find_fatdata_path(source_path)
        if not fatdata_path:
            raise FileNotFoundError(f"FATDATA directory not found in {source_path}")

        output_fatdata_dir = output_dir / "fatdata"
        output_fatdata_dir.mkdir(parents=True, exist_ok=True)

        try:
            iso = pycdlib.PyCdlib()
            iso.open(str(source_path))

            try:
                # Extract FATDATA directory
                self._extract_directory_recursive(iso, fatdata_path, output_fatdata_dir)
                logger.info(f"Successfully extracted FATDATA to: {output_fatdata_dir}")

                return ExtractionResult(fatdata_path=output_fatdata_dir)

            finally:
                iso.close()

        except Exception as e:
            raise RuntimeError(f"Failed to extract from ISO {source_path}: {e}")

    def _extract_directory_recursive(
        self, iso: pycdlib.PyCdlib, iso_path: str, output_dir: Path
    ):
        """Recursively extract a directory from ISO."""
        try:
            # List all entries in the directory
            for child in iso.list_children(iso_path=iso_path):
                child_name = child.file_identifier().decode("utf-8")

                # Skip '.' and '..' entries
                if child_name in (".", ".."):
                    continue

                child_iso_path = f"{iso_path}/{child_name}".replace("//", "/")
                child_output_path = (
                    output_dir / child_name.lower()
                )  # Use lowercase for output

                if child.is_dir():
                    # Create directory and recurse
                    child_output_path.mkdir(parents=True, exist_ok=True)
                    self._extract_directory_recursive(
                        iso, child_iso_path, child_output_path
                    )
                else:
                    # Extract file
                    with open(child_output_path, "wb") as output_file:
                        iso.get_file_from_iso_fp(output_file, iso_path=child_iso_path)
                    logger.debug(f"Extracted: {child_iso_path} -> {child_output_path}")

        except Exception as e:
            logger.error(f"Error extracting directory {iso_path}: {e}")
            raise
