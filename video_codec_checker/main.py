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

from video_codec_checker.config import load_env_config, load_yaml_config
from video_codec_checker.ffmpeg_generator import generate_ffmpeg_command
from pathlib import Path
from video_codec_checker.video_processor import get_video_files, probe_video_metadata

GOOD_CODECS = {"av1", "hevc", "h264"}


class VideoCodecChecker:
    def __init__(self, output_file: str | None = None) -> None:
        self.output_file = (
            output_file
            or f"video_codec_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    def process_files(self, directory: str = ".", jobs: int | None = None) -> int:
        """Process all video files and generate CSV output."""
        video_files = get_video_files(directory)
        print(f"Processing {len(video_files)} video files...", file=sys.stderr)

        processed_count = 0
        with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["File", "Codec", "FFmpeg_Command"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Determine worker count
            cpu_workers = os.cpu_count() or 1
            max_workers = jobs if jobs and jobs > 0 else min(32, cpu_workers)

            def task(fp: Path) -> tuple[Path, str | None, int]:
                codec, channels = probe_video_metadata(fp)
                return fp, codec, channels

            # Run metadata probing with optional concurrency
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(task, fp) for fp in video_files]
                for fut in as_completed(futures):
                    file_path, codec, channels = fut.result()
                    if codec and codec not in GOOD_CODECS:
                        ffmpeg_cmd = generate_ffmpeg_command(
                            file_path.resolve(), channels
                        )
                        writer.writerow(
                            {
                                "File": str(file_path),
                                "Codec": codec,
                                "FFmpeg_Command": ffmpeg_cmd,
                            }
                        )
                        processed_count += 1
                        print(f"Processed: {file_path}", file=sys.stderr)
                    else:
                        print(f"Skipped: {file_path}", file=sys.stderr)

        print(f"Results written to: {self.output_file}", file=sys.stderr)
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
        processed_count = checker.process_files(args.directory, jobs=args.jobs)
        print(f"Found {processed_count} files that need conversion.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
