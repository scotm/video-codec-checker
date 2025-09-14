#!/usr/bin/env python3
"""
Script to find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)
Outputs CSV: File,Codec,FFmpeg_Command
State-of-the-art: av1, hevc, h264
"""

import argparse
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from video_codec_checker.config import load_env_config, load_yaml_config
from video_codec_checker.ffmpeg_generator import (
    generate_ffmpeg_command,
    get_output_path,
)
from video_codec_checker.script_writer import (
    ScriptWriter,
    resolve_trash_config,
)
from video_codec_checker.video_processor import get_video_files, probe_video_metadata

GOOD_CODECS = {"av1", "hevc", "h264"}


class VideoCodecChecker:
    def __init__(self, output_file: str | None = None) -> None:
        self.output_file = (
            output_file
            or f"video_codec_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    def process_files(
        self,
        directory: str = ".",
        jobs: int | None = None,
        script_file: str | None = None,
        delete_original: bool = False,
        trash_original: bool = False,
        ffprobe_args: list[str] | None = None,
    ) -> int:
        """Process all video files and generate CSV output."""
        video_files = get_video_files(directory)
        print(f"Processing {len(video_files)} video files...", file=sys.stderr)

        processed_count = 0
        with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["File", "Codec", "Audio_Channels", "FFmpeg_Command"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            script: ScriptWriter | None = None
            if script_file:
                trash_cfg = resolve_trash_config(trash_original)
                script = ScriptWriter(
                    path=script_file,
                    delete_original=delete_original,
                    trash_config=trash_cfg,
                )
                script.open()

            # Determine worker count
            cpu_workers = os.cpu_count() or 1
            max_workers = jobs if jobs and jobs > 0 else min(32, cpu_workers)

            def _init_stats() -> dict:
                return {
                    "fast_attempted": 0,
                    "fast_succeeded": 0,
                    "fast_fallbacks": 0,
                    "fast_time": 0.0,
                    "full_probes": 0,
                    "full_time": 0.0,
                }

            def task(fp: Path) -> tuple[Path, str | None, int, dict]:
                local_stats = _init_stats()
                codec, channels = probe_video_metadata(fp, ffprobe_args, local_stats)
                return fp, codec, channels, local_stats

            # Run metadata probing with optional concurrency
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(task, fp) for fp in video_files]
                # Global stats aggregate
                agg = _init_stats()
                for fut in as_completed(futures):
                    file_path, codec, channels, local_stats = fut.result()
                    # Aggregate stats
                    for k in agg:
                        agg[k] += local_stats.get(k, 0)
                    if codec and codec not in GOOD_CODECS:
                        abs_in = file_path.resolve()
                        ffmpeg_cmd = generate_ffmpeg_command(abs_in, channels)
                        writer.writerow(
                            {
                                "File": str(file_path),
                                "Codec": codec,
                                "Audio_Channels": channels,
                                "FFmpeg_Command": ffmpeg_cmd,
                            }
                        )
                        if script is not None:
                            if delete_original or trash_original:
                                dst = get_output_path(abs_in)
                                script.write_command(ffmpeg_cmd, abs_in, dst)
                            else:
                                script.write_command_no_cleanup(ffmpeg_cmd)
                        processed_count += 1
                        print(f"Processed: {file_path}", file=sys.stderr)
                    else:
                        print(f"Skipped: {file_path}", file=sys.stderr)

            if script is not None:
                script.close()
                print(f"Script written to: {script_file}", file=sys.stderr)

        print(f"Results written to: {self.output_file}", file=sys.stderr)
        # Print probe stats summary if fast-probe was enabled
        if ffprobe_args is not None:
            total_fast = agg["fast_attempted"]
            print(
                (
                    "Probe stats: fast_attempted=%d, fast_ok=%d, "
                    "fast_fallbacks=%d, full_probes=%d"
                )
                % (
                    total_fast,
                    agg["fast_succeeded"],
                    agg["fast_fallbacks"],
                    agg["full_probes"],
                ),
                file=sys.stderr,
            )
            # Timings

            def _fmt(sec: float) -> str:
                return f"{sec:.3f}s"

            avg_fast = (
                agg["fast_time"] / total_fast if total_fast > 0 else 0.0
            )
            avg_full = (
                agg["full_time"] / agg["full_probes"]
                if agg["full_probes"] > 0
                else 0.0
            )
            print(
                (
                    "Timing: fast_total=%s, full_total=%s, avg_fast=%s, avg_full=%s"
                )
                % (
                    _fmt(agg["fast_time"]),
                    _fmt(agg["full_time"]),
                    _fmt(avg_fast),
                    _fmt(avg_full),
                ),
                file=sys.stderr,
            )
        return processed_count


def main() -> None:
    # Load environment variables from .env file
    env_config = load_env_config()

    parser = argparse.ArgumentParser(
        description=(
            "Find video files using codecs less than state-of-the-art "
            "(AV1, HEVC, H.264)"
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        default=env_config.get("output_file"),
        help="Specify output CSV filename",
    )
    parser.add_argument("--config", help="Specify config file path")
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=None,
        help=(
            "Number of worker threads to use for ffprobe (default: CPU count, up to 32)"
        ),
    )
    parser.add_argument(
        "-s",
        "--script",
        help=("Write a shell script with the generated FFmpeg commands; not executed"),
    )
    # Fast-probe is enabled by default unless explicitly disabled via env/CLI
    fast_probe_default = (
        env_config.get("fast_probe")
        if env_config.get("fast_probe") is not None
        else True
    )
    parser.add_argument(
        "--fast-probe",
        action=argparse.BooleanOptionalAction,
        default=fast_probe_default,
        help=(
            "Enable fast ffprobe (-probesize/-analyzeduration). "
            "Use --no-fast-probe to disable."
        ),
    )
    parser.add_argument(
        "--probe-size",
        default=env_config.get("ffprobe_probesize") or "5M",
        help=(
            "ffprobe -probesize value (used only with --fast-probe); "
            "accepts size suffixes like 1M"
        ),
    )
    parser.add_argument(
        "--analyze-duration",
        default=env_config.get("ffprobe_analyzeduration") or "10M",
        help=(
            "ffprobe -analyzeduration value (used only with --fast-probe); "
            "accepts microseconds; supports suffixes like 10M"
        ),
    )
    parser.add_argument(
        "-r",
        "--delete-original",
        action="store_true",
        default=env_config.get("delete_original", False),
        help=(
            "In generated script, remove source file after successful conversion"
        ),
    )
    parser.add_argument(
        "-t",
        "--trash-original",
        action="store_true",
        default=env_config.get("trash_original", False),
        help=(
            "In generated script, move source file to Trash on success "
            "(uses macOS Finder/gio/trash when available)"
        ),
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=env_config.get("scan_directory"),
        help="Directory to scan for video files (default: current directory)",
    )

    args = parser.parse_args()

    # Load configuration from YAML file
    yaml_config = load_yaml_config(args.config)

    # Override defaults with config values if not set by environment variables
    if not args.output:
        args.output = yaml_config.get("output_file")

    try:
        checker = VideoCodecChecker(args.output)
        # Build ffprobe args for fast-probe if requested
        fast_args: list[str] | None = None
        if args.fast_probe:
            fast_args = [
                "-probesize",
                str(args.probe_size),
                "-analyzeduration",
                str(args.analyze_duration),
            ]

        processed_count = checker.process_files(
            args.directory,
            jobs=args.jobs,
            script_file=args.script,
            delete_original=args.delete_original,
            trash_original=args.trash_original,
            ffprobe_args=fast_args,
        )
        print(f"Found {processed_count} files that need conversion.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
