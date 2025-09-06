"""CUE/BIN file handler using bchunk for conversion and ISO extraction."""

import logging
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List

from ..asset_extractor import BaseAssetHandler, ExtractionResult
from .iso_handler import IsoHandler
from ...utils.binary_resolver import get_bchunk_resolver

logger = logging.getLogger(__name__)


class CueBinHandler(BaseAssetHandler):
    """Handler for CUE/BIN disc image files."""

    def __init__(self):
        """Initialize CUE/BIN handler."""
        bchunk_resolver = get_bchunk_resolver()
        bchunk_path = bchunk_resolver.find_binary()
        self.bchunk_cmd = str(bchunk_path) if bchunk_path else None
        self.iso_handler = IsoHandler()

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a CUE file with corresponding BIN."""
        if file_path.suffix.lower() not in (".cue", ".bin"):
            return False
        
        # Get both CUE and BIN paths
        if file_path.suffix.lower() == ".cue":
            cue_path = file_path
            bin_path = file_path.with_suffix(".bin")
            # Also check for uppercase .BIN
            if not bin_path.exists():
                bin_path = file_path.with_suffix(".BIN")
        else:  # .bin file
            bin_path = file_path
            cue_path = file_path.with_suffix(".cue")
            # Also check for uppercase .CUE
            if not cue_path.exists():
                cue_path = file_path.with_suffix(".CUE")
        
        # Both files must exist
        if not (cue_path.exists() and bin_path.exists()):
            return False
        
        # bchunk must be available
        if not self.bchunk_cmd:
            logger.warning("bchunk not found in PATH - cannot handle CUE/BIN files")
            return False
        
        return True

    def find_fatdata_path(self, source_path: Path) -> Optional[str]:
        """Find FATDATA by converting to ISO first."""
        # We need to convert to ISO to check for FATDATA
        # This is expensive, so we'll just assume it exists if we can handle the file
        return "/FATDATA" if self.can_handle(source_path) else None

    def extract_fatdata(self, source_path: Path, output_dir: Path) -> ExtractionResult:
        """Extract FATDATA and audio tracks from CUE/BIN."""
        if not self.can_handle(source_path):
            raise ValueError(f"Cannot handle file: {source_path}")
        
        # Get both CUE and BIN paths
        if source_path.suffix.lower() == ".cue":
            cue_path = source_path
            bin_path = source_path.with_suffix(".bin")
            if not bin_path.exists():
                bin_path = source_path.with_suffix(".BIN")
        else:
            bin_path = source_path
            cue_path = source_path.with_suffix(".cue")
            if not cue_path.exists():
                cue_path = source_path.with_suffix(".CUE")
        
        # Use a temporary directory for conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            logger.info(f"Converting CUE/BIN to ISO: {cue_path}")
            
            # Run bchunk to convert
            iso_path, audio_tracks = self._convert_with_bchunk(
                bin_path, cue_path, temp_path
            )
            
            if not iso_path:
                raise RuntimeError("No data track found in CUE/BIN file")
            
            # Extract FATDATA from the ISO using ISO handler
            logger.info("Extracting FATDATA from converted ISO")
            result = self.iso_handler.extract_fatdata(iso_path, output_dir)
            
            # Copy audio tracks to output directory if present
            if audio_tracks:
                audio_output_dir = output_dir / "audio"
                audio_output_dir.mkdir(parents=True, exist_ok=True)
                
                copied_audio_tracks = []
                for track in audio_tracks:
                    dest = audio_output_dir / track.name
                    shutil.copy2(track, dest)
                    copied_audio_tracks.append(dest)
                    logger.info(f"Copied audio track: {track.name}")
                
                # Add audio tracks to result
                result.music_paths = copied_audio_tracks
            
            return result

    def _convert_with_bchunk(self, bin_path: Path, cue_path: Path, output_dir: Path) -> tuple[Optional[Path], List[Path]]:
        """Convert CUE/BIN to ISO and audio tracks using bchunk.
        
        Returns:
            Tuple of (iso_path, audio_track_paths)
        """
        # bchunk syntax: bchunk [-v] [-p] [-r] [-w] [-s] <image.bin> <image.cue> <basename>
        output_base = output_dir / "track"
        
        cmd = [
            self.bchunk_cmd,
            "-w",  # Output audio as WAV files
            str(bin_path),
            str(cue_path),
            str(output_base)
        ]
        
        logger.debug(f"Running bchunk: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                # Log the error but continue - sometimes bchunk returns non-zero even on success
                logger.warning(f"bchunk returned non-zero: {result.stderr}")
            
            # Find generated files
            iso_path = None
            audio_tracks = []
            
            for file in sorted(output_dir.glob("track*")):
                if file.suffix.lower() == ".iso":
                    iso_path = file
                    logger.debug(f"Found data track: {file}")
                elif file.suffix.lower() in (".wav", ".cdr"):
                    audio_tracks.append(file)
                    logger.debug(f"Found audio track: {file}")
            
            return iso_path, audio_tracks
            
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to run bchunk: {e}")
