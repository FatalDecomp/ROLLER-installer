"""CUE/BIN file handler using bchunk for conversion and ISO extraction.

Supports both single-bin and multi-bin (Redump-style) CUE sheets.
"""

import logging
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ...utils.binary_resolver import get_bchunk_resolver
from ..asset_extractor import BaseAssetHandler, ExtractionResult
from .iso_handler import IsoHandler

logger = logging.getLogger(__name__)


@dataclass
class CueTrack:
    """A track parsed from a CUE sheet."""

    file_path: Path
    track_num: int
    track_type: str  # e.g. "MODE1/2352", "AUDIO"
    indexes: dict = field(default_factory=dict)

    @property
    def is_data(self) -> bool:
        return self.track_type != "AUDIO"


class CueBinHandler(BaseAssetHandler):
    """Handler for CUE/BIN disc image files.

    Supports both single-bin and multi-bin (Redump-style) CUE sheets.
    """

    def __init__(self):
        """Initialize CUE/BIN handler."""
        bchunk_resolver = get_bchunk_resolver()
        bchunk_path = bchunk_resolver.find_binary()
        self.bchunk_cmd = str(bchunk_path) if bchunk_path else None
        self.iso_handler = IsoHandler()

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a CUE file (or BIN with a matching CUE)."""
        if file_path.suffix.lower() not in (".cue", ".bin"):
            return False

        cue_path = self._resolve_cue_path(file_path)
        if not cue_path or not cue_path.exists():
            return False

        # Parse the CUE sheet and verify all referenced BIN files exist
        tracks = self._parse_cue(cue_path)
        if not tracks:
            return False

        missing = [t.file_path for t in tracks if not t.file_path.exists()]
        if missing:
            logger.warning(f"CUE references missing BIN files: {missing}")
            return False

        # bchunk must be available
        if not self.bchunk_cmd:
            raise RuntimeError(
                "CUE/BIN support requires bchunk, but it was not found. "
                "Run 'roller-installer cli download-tools' to install it, "
                "or install bchunk manually and ensure it is on your PATH."
            )

        return True

    def find_fatdata_path(self, source_path: Path) -> Optional[str]:
        """Find FATDATA by converting to ISO first."""
        return "/FATDATA" if self.can_handle(source_path) else None

    def extract_fatdata(self, source_path: Path, output_dir: Path) -> ExtractionResult:
        """Extract FATDATA and audio tracks from CUE/BIN."""
        if not self.can_handle(source_path):
            raise ValueError(f"Cannot handle file: {source_path}")

        cue_path = self._resolve_cue_path(source_path)
        tracks = self._parse_cue(cue_path)

        data_tracks = [t for t in tracks if t.is_data]
        audio_tracks = [t for t in tracks if not t.is_data]

        if not data_tracks:
            raise RuntimeError("No data track found in CUE/BIN file")

        is_multi_bin = len({str(t.file_path) for t in tracks}) > 1

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            logger.info(
                f"Converting CUE/BIN to ISO ({'multi-bin' if is_multi_bin else 'single-bin'}): {cue_path}"
            )

            if is_multi_bin:
                iso_path, wav_paths = self._convert_multi_bin(
                    data_tracks, audio_tracks, temp_path
                )
            else:
                bin_path = tracks[0].file_path
                iso_path, wav_paths = self._convert_single_bin(
                    bin_path, cue_path, temp_path
                )

            if not iso_path:
                raise RuntimeError("bchunk did not produce an ISO from the data track")

            # Extract FATDATA from the ISO
            logger.info("Extracting FATDATA from converted ISO")
            result = self.iso_handler.extract_fatdata(iso_path, output_dir)

            # Copy audio tracks to output directory
            if wav_paths:
                audio_output_dir = output_dir / "audio"
                audio_output_dir.mkdir(parents=True, exist_ok=True)

                copied = []
                for wav in wav_paths:
                    dest = audio_output_dir / wav.name
                    shutil.copy2(wav, dest)
                    copied.append(dest)
                    logger.info(f"Copied audio track: {wav.name}")

                result.music_paths = copied

            return result

    # ------------------------------------------------------------------
    # CUE parsing
    # ------------------------------------------------------------------

    def _resolve_cue_path(self, file_path: Path) -> Optional[Path]:
        """Resolve the CUE file path from either a .cue or .bin path."""
        if file_path.suffix.lower() == ".cue":
            return file_path if file_path.exists() else None

        # Given a .bin, try exact name match first
        for ext in (".cue", ".CUE"):
            cue = file_path.with_suffix(ext)
            if cue.exists():
                return cue

        # For multi-bin, the .bin name won't match the .cue name.
        # Look for a lone .cue in the same directory.
        cue_files = list(file_path.parent.glob("*.cue")) + list(
            file_path.parent.glob("*.CUE")
        )
        if len(cue_files) == 1:
            return cue_files[0]

        return None

    def _parse_cue(self, cue_path: Path) -> List[CueTrack]:
        """Parse a CUE sheet and return a list of tracks."""
        try:
            text = cue_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.error(f"Failed to read CUE file: {e}")
            return []

        tracks: List[CueTrack] = []
        current_file: Optional[Path] = None
        current_num: Optional[int] = None
        current_type: Optional[str] = None
        current_indexes: dict = {}

        def _flush():
            if current_file and current_num is not None:
                tracks.append(
                    CueTrack(
                        file_path=current_file,
                        track_num=current_num,
                        track_type=current_type or "AUDIO",
                        indexes=dict(current_indexes),
                    )
                )

        for line in text.splitlines():
            line = line.strip()

            # FILE "filename.bin" BINARY
            m = re.match(r'^FILE\s+"([^"]+)"\s+\w+', line)
            if m:
                _flush()
                current_num = None
                current_indexes = {}
                ref = m.group(1)
                current_file = cue_path.parent / ref
                if not current_file.exists():
                    current_file = (
                        self._find_case_insensitive(cue_path.parent, ref)
                        or current_file
                    )
                continue

            # TRACK 01 MODE1/2352
            m = re.match(r"^TRACK\s+(\d+)\s+(\S+)", line)
            if m:
                _flush()
                current_num = int(m.group(1))
                current_type = m.group(2)
                current_indexes = {}
                continue

            # INDEX 01 00:00:00
            m = re.match(r"^INDEX\s+(\d+)\s+(\S+)", line)
            if m:
                current_indexes[int(m.group(1))] = m.group(2)
                continue

        _flush()
        return tracks

    @staticmethod
    def _find_case_insensitive(directory: Path, filename: str) -> Optional[Path]:
        """Find a file by name with case-insensitive matching."""
        lower = filename.lower()
        for p in directory.iterdir():
            if p.name.lower() == lower:
                return p
        return None

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def _convert_multi_bin(
        self,
        data_tracks: List[CueTrack],
        audio_tracks: List[CueTrack],
        output_dir: Path,
    ) -> tuple[Optional[Path], List[Path]]:
        """Convert a multi-bin CUE/BIN by processing each track individually.

        For multi-bin, each .bin file contains exactly one track, so we create
        a minimal single-track CUE for bchunk to read the sector layout.
        """
        iso_path = None
        wav_paths: List[Path] = []

        # Convert data track(s) to ISO
        for track in data_tracks:
            temp_cue = output_dir / f"data{track.track_num:02d}.cue"
            temp_cue.write_text(
                f'FILE "{track.file_path.name}" BINARY\n'
                f"  TRACK 01 {track.track_type}\n"
                f"    INDEX 01 00:00:00\n"
            )

            prefix = output_dir / f"data{track.track_num:02d}"
            cmd = [
                self.bchunk_cmd,
                str(track.file_path),
                str(temp_cue),
                str(prefix),
            ]
            logger.debug(f"bchunk data track {track.track_num}: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.warning(
                    f"bchunk data track {track.track_num} stderr: {result.stderr}"
                )

            for f in sorted(output_dir.glob(f"data{track.track_num:02d}*.iso")):
                iso_path = f
                logger.info(f"Converted data track {track.track_num} -> {f.name}")
                break

        # Convert audio tracks to WAV
        for track in audio_tracks:
            temp_cue = output_dir / f"audio{track.track_num:02d}.cue"
            temp_cue.write_text(
                f'FILE "{track.file_path.name}" BINARY\n'
                f"  TRACK 01 AUDIO\n"
                f"    INDEX 01 00:00:00\n"
            )

            prefix = output_dir / f"audio{track.track_num:02d}"
            cmd = [
                self.bchunk_cmd,
                "-w",
                str(track.file_path),
                str(temp_cue),
                str(prefix),
            ]
            logger.debug(f"bchunk audio track {track.track_num}: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.warning(
                    f"bchunk audio track {track.track_num} stderr: {result.stderr}"
                )

            for f in sorted(output_dir.glob(f"audio{track.track_num:02d}*.wav")):
                wav_paths.append(f)
                logger.info(f"Converted audio track {track.track_num} -> {f.name}")
                break

        return iso_path, wav_paths

    def _convert_single_bin(
        self,
        bin_path: Path,
        cue_path: Path,
        output_dir: Path,
    ) -> tuple[Optional[Path], List[Path]]:
        """Convert a single-bin CUE/BIN to ISO + WAV tracks using bchunk."""
        output_base = output_dir / "track"

        cmd = [
            self.bchunk_cmd,
            "-w",
            str(bin_path),
            str(cue_path),
            str(output_base),
        ]

        logger.debug(f"Running bchunk: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                logger.warning(f"bchunk returned non-zero: {result.stderr}")

            iso_path = None
            audio_tracks: List[Path] = []

            for f in sorted(output_dir.glob("track*")):
                if f.suffix.lower() == ".iso":
                    iso_path = f
                    logger.debug(f"Found data track: {f}")
                elif f.suffix.lower() in (".wav", ".cdr"):
                    audio_tracks.append(f)
                    logger.debug(f"Found audio track: {f}")

            return iso_path, audio_tracks

        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to run bchunk: {e}")
