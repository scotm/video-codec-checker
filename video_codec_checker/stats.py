"""Probe statistics aggregation and reporting.

Maintains counters and timings for fast and full ffprobe calls.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ProbeStats:
    """Aggregates ffprobe stats across many files.

    Keys mirror those produced by video_processor.probe_video_metadata when a stats
    dict is provided: fast_attempted, fast_succeeded, fast_fallbacks, fast_time,
    full_probes, full_time.
    """

    fast_attempted: int = 0
    fast_succeeded: int = 0
    fast_fallbacks: int = 0
    fast_time: float = 0.0
    full_probes: int = 0
    full_time: float = 0.0

    def new_local(self) -> Dict[str, float | int]:
        """Return a fresh local stats dict for a single file probe."""
        return {
            "fast_attempted": 0,
            "fast_succeeded": 0,
            "fast_fallbacks": 0,
            "fast_time": 0.0,
            "full_probes": 0,
            "full_time": 0.0,
        }

    def add(self, local: Dict[str, float | int]) -> None:
        """Merge a local stats dict produced during a single file probe."""
        self.fast_attempted += int(local.get("fast_attempted", 0))
        self.fast_succeeded += int(local.get("fast_succeeded", 0))
        self.fast_fallbacks += int(local.get("fast_fallbacks", 0))
        self.fast_time += float(local.get("fast_time", 0.0))
        self.full_probes += int(local.get("full_probes", 0))
        self.full_time += float(local.get("full_time", 0.0))

    def _fmt(self, sec: float) -> str:
        return f"{sec:.3f}s"

    def print_summary(self, fast_probe_enabled: bool, stream = sys.stderr) -> None:
        """Print a short stats + timing summary if fast-probe was used."""
        if not fast_probe_enabled:
            return
        total_fast = self.fast_attempted
        print(
            (
                "Probe stats: fast_attempted=%d, fast_ok=%d, fast_fallbacks=%d, full_probes=%d"
            )
            % (
                total_fast,
                self.fast_succeeded,
                self.fast_fallbacks,
                self.full_probes,
            ),
            file=stream,
        )
        avg_fast = (self.fast_time / total_fast) if total_fast > 0 else 0.0
        avg_full = (self.full_time / self.full_probes) if self.full_probes > 0 else 0.0
        print(
            (
                "Timing: fast_total=%s, full_total=%s, avg_fast=%s, avg_full=%s"
            )
            % (
                self._fmt(self.fast_time),
                self._fmt(self.full_time),
                self._fmt(avg_fast),
                self._fmt(avg_full),
            ),
            file=stream,
        )

