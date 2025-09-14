"""Concurrent probing utilities.

Provides a small executor wrapper for probing video metadata in parallel.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterable, Iterator, Tuple

from video_codec_checker.models import FileProbeResult
from video_codec_checker.stats import ProbeStats
from video_codec_checker.video_processor import probe_video_metadata


class ProbeExecutor:
    """Run metadata probes concurrently and aggregate stats."""

    def __init__(
        self,
        jobs: int | None = None,
        ffprobe_args: list[str] | None = None,
        probe_func: Callable[
            [Path, list[str] | None, dict | None], tuple[str | None, int]
        ] = probe_video_metadata,
    ) -> None:
        self.max_workers = self._resolve_workers(jobs)
        self.ffprobe_args = ffprobe_args
        self.stats = ProbeStats()
        self._probe = probe_func

    def _resolve_workers(self, jobs: int | None) -> int:
        if jobs and jobs > 0:
            return jobs
        cpu_workers = os.cpu_count() or 1
        return min(32, cpu_workers)

    def _task(self, fp: Path) -> Tuple[FileProbeResult, dict]:
        local_stats = self.stats.new_local()
        codec, channels = self._probe(fp, self.ffprobe_args, local_stats)
        return FileProbeResult(path=fp, codec=codec, channels=channels), local_stats

    def run(self, files: Iterable[Path]) -> Iterator[FileProbeResult]:
        """Yield FileProbeResult items as they complete."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._task, fp) for fp in files]
            for fut in as_completed(futures):
                result, local_stats = fut.result()
                self.stats.add(local_stats)
                yield result
