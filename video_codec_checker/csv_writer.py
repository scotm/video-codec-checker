"""CSV writer for codec check results.

Encapsulates streaming CSV writing with a stable header.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import IO


CSV_FIELDS = ["File", "Codec", "Audio_Channels", "FFmpeg_Command"]


class CsvResultsWriter:
    """Write results rows to a CSV file with a fixed header."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._fh: IO[str] | None = None
        self._writer: csv.DictWriter | None = None

    def open(self) -> None:
        fh = self.path.open("w", newline="", encoding="utf-8")
        self._fh = fh
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        self._writer = writer

    def write_row(self, file: str, codec: str, channels: int, command: str) -> None:
        if self._writer is None:
            raise RuntimeError("CSV writer is not open")
        self._writer.writerow(
            {
                "File": file,
                "Codec": codec,
                "Audio_Channels": channels,
                "FFmpeg_Command": command,
            }
        )

    def close(self) -> None:
        if self._fh is not None:
            self._fh.flush()
            self._fh.close()
            self._fh = None
            self._writer = None

