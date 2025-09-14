"""Shared dataclasses and protocols for program state and results."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from video_codec_checker.script_writer import TrashConfig


class CleanupMode(str, Enum):
    NONE = "none"
    DELETE = "delete"
    TRASH = "trash"


@dataclass(frozen=True)
class CleanupPolicy:
    """Represents post-conversion cleanup policy."""

    mode: CleanupMode = CleanupMode.NONE
    trash: TrashConfig | None = None

    @property
    def delete_original(self) -> bool:
        return self.mode == CleanupMode.DELETE

    @property
    def trash_original(self) -> bool:
        return self.mode == CleanupMode.TRASH


@dataclass(frozen=True)
class ProbeSettings:
    """ffprobe behavior configuration."""

    fast_probe: bool = True
    probe_size: str = "5M"
    analyze_duration: str = "10M"

    @property
    def args(self) -> list[str] | None:
        if not self.fast_probe:
            return None
        return [
            "-probesize",
            str(self.probe_size),
            "-analyzeduration",
            str(self.analyze_duration),
        ]


@dataclass(frozen=True)
class AppConfig:
    """Top-level configuration normalized from CLI/env/YAML."""

    directory: Path
    output: Path
    jobs: int | None
    script_file: Path | None
    cleanup: CleanupPolicy
    probe: ProbeSettings


@dataclass(frozen=True)
class FileProbeResult:
    """Result of probing a single file."""

    path: Path
    codec: str | None
    channels: int

    def needs_conversion(self, good_codecs: set[str]) -> bool:
        return bool(self.codec) and str(self.codec) not in good_codecs


@dataclass(frozen=True)
class CsvRow:
    """Represents a CSV result row."""

    file: str
    codec: str
    channels: int
    command: str

    def as_dict(self) -> dict[str, str | int]:
        return {
            "File": self.file,
            "Codec": self.codec,
            "Audio_Channels": self.channels,
            "FFmpeg_Command": self.command,
        }


class Prober(Protocol):
    def __call__(
        self, path: Path, args: list[str] | None, stats: dict | None
    ) -> tuple[str | None, int]: ...
