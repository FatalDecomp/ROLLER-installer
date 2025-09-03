"""
Asset extraction system for ROLLER installer.

Provides a modular system for extracting FATDATA directories from various archive formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Type, Optional, List
import logging

logger = logging.getLogger(__name__)


class ExtractionResult:
    """Result of asset extraction operation."""

    def __init__(self, fatdata_path: Path, music_paths: Optional[List[Path]] = None):
        self.fatdata_path = fatdata_path
        self.music_paths = music_paths or []

    @property
    def has_music(self) -> bool:
        """Check if music files were extracted."""
        return bool(self.music_paths)

    def validate(self) -> None:
        """Validate that extraction was successful.

        Raises:
            FileNotFoundError: If FATDATA directory doesn't exist or is empty
        """
        if not self.fatdata_path.exists():
            raise FileNotFoundError(f"FATDATA directory not found: {self.fatdata_path}")

        if not self.fatdata_path.is_dir():
            raise FileNotFoundError(
                f"FATDATA path is not a directory: {self.fatdata_path}"
            )

        # Check if directory has any files
        if not any(self.fatdata_path.iterdir()):
            raise FileNotFoundError(f"FATDATA directory is empty: {self.fatdata_path}")

        logger.debug(f"FATDATA validation passed: {self.fatdata_path}")

        # Validate music files if present
        invalid_music_files = []
        for music_path in self.music_paths:
            if not music_path.exists() or not music_path.is_file():
                invalid_music_files.append(music_path)

        if invalid_music_files:
            logger.warning(f"Some music files are invalid: {invalid_music_files}")
            # Remove invalid files from the list
            self.music_paths = [
                p for p in self.music_paths if p not in invalid_music_files
            ]


class BaseAssetHandler(ABC):
    """Abstract base class for asset extraction handlers."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Check if this handler can process the given file.

        Args:
            file_path: Path to the archive file

        Returns:
            True if this handler can process the file
        """
        pass

    @abstractmethod
    def extract_fatdata(self, source_path: Path, output_dir: Path) -> ExtractionResult:
        """Extract FATDATA directory from the archive.

        Args:
            source_path: Path to the source archive
            output_dir: Directory to extract files to

        Returns:
            ExtractionResult containing paths to extracted assets

        Raises:
            FileNotFoundError: If FATDATA directory not found in archive
            RuntimeError: If extraction fails
        """
        pass

    @abstractmethod
    def find_fatdata_path(self, source_path: Path) -> Optional[str]:
        """Find the path to FATDATA directory within the archive.

        Args:
            source_path: Path to the source archive

        Returns:
            Path to FATDATA directory within archive, or None if not found
        """
        pass


class AssetExtractorRegistry:
    """Registry for asset extraction handlers."""

    def __init__(self):
        self._handlers: Dict[str, Type[BaseAssetHandler]] = {}
        self._register_default_handlers()

    def register_handler(self, extension: str, handler_class: Type[BaseAssetHandler]):
        """Register a handler for a file extension.

        Args:
            extension: File extension (e.g., '.zip', '.iso')
            handler_class: Handler class to register
        """
        self._handlers[extension.lower()] = handler_class
        logger.debug(f"Registered handler {handler_class.__name__} for {extension}")

    def get_handler(self, file_path: Path) -> Optional[BaseAssetHandler]:
        """Get appropriate handler for a file.

        Args:
            file_path: Path to the file

        Returns:
            Handler instance, or None if no handler available
        """
        extension = file_path.suffix.lower()
        handler_spec = self._handlers.get(extension)

        if handler_spec:
            # Import handler class dynamically
            if isinstance(handler_spec, str):
                module_path, class_name = handler_spec.split(":")
                import importlib

                module = importlib.import_module(module_path)
                handler_class = getattr(module, class_name)
            else:
                handler_class = handler_spec

            handler = handler_class()
            if handler.can_handle(file_path):
                return handler

        return None

    def _register_default_handlers(self):
        """Register built-in handlers."""
        # Register handler classes by name to avoid circular imports
        self._handlers[".zip"] = "roller_installer.core.handlers.zip_handler:ZipHandler"
        self._handlers[".iso"] = "roller_installer.core.handlers.iso_handler:IsoHandler"


# Global registry instance
_registry = AssetExtractorRegistry()


def extract_fatdata(source_path: Path, output_dir: Path) -> ExtractionResult:
    """Main API for extracting FATDATA from archive files.

    Args:
        source_path: Path to the source archive (ZIP, ISO, etc.)
        output_dir: Directory to extract files to

    Returns:
        ExtractionResult containing paths to extracted assets

    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If FATDATA directory not found
        RuntimeError: If extraction fails
    """
    source_path = Path(source_path)
    output_dir = Path(output_dir)

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    handler = _registry.get_handler(source_path)
    if not handler:
        raise ValueError(f"Unsupported file format: {source_path.suffix}")

    logger.info(
        f"Extracting FATDATA from {source_path} using {handler.__class__.__name__}"
    )

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = handler.extract_fatdata(source_path, output_dir)

        # Validate the extraction result
        result.validate()

        logger.info(f"Successfully extracted FATDATA from {source_path}")
        if result.has_music:
            logger.info(f"Also extracted {len(result.music_paths)} music tracks")

        return result

    except Exception as e:
        logger.error(f"Extraction failed for {source_path}: {e}")
        raise


def register_handler(extension: str, handler_class: Type[BaseAssetHandler]):
    """Register a custom handler for a file extension.

    Args:
        extension: File extension (e.g., '.7z', '.bin')
        handler_class: Handler class to register
    """
    _registry.register_handler(extension, handler_class)
