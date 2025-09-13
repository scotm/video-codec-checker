#!/usr/bin/env python3
"""
Script to find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)
Outputs CSV: File,Codec,FFmpeg_Command
State-of-the-art: av1, hevc, h264
"""

import argparse
import csv
import sys
from datetime import datetime

from video_codec_checker.config import load_env_config, load_yaml_config
from video_codec_checker.ffmpeg_generator import generate_ffmpeg_command
from video_codec_checker.video_processor import (
    get_audio_channels,
    get_video_codec,
    get_video_files,
)

GOOD_CODECS = {"av1", "hevc", "h264"}


class VideoCodecChecker:
    def __init__(self, output_file=None):
        self.output_file = (
            output_file
            or f"video_codec_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    def process_files(self, directory="."):
        """Process all video files and generate CSV output."""
        video_files = get_video_files(directory)
        results = []

        print(f"Processing {len(video_files)} video files...", file=sys.stderr)

        for file_path in video_files:
            abs_file = file_path.resolve()
            codec = get_video_codec(file_path)
            channels = get_audio_channels(file_path)

            if codec and codec not in GOOD_CODECS:
                ffmpeg_cmd = generate_ffmpeg_command(abs_file, channels)
                results.append(
                    {
                        "file": str(file_path),
                        "codec": codec,
                        "ffmpeg_command": ffmpeg_cmd,
                    }
                )
                print(f"Processed: {file_path}", file=sys.stderr)
            else:
                print(f"Skipped: {file_path}", file=sys.stderr)

        # Write CSV output
        with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["File", "Codec", "FFmpeg_Command"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow(
                    {
                        "File": result["file"],
                        "Codec": result["codec"],
                        "FFmpeg_Command": result["ffmpeg_command"],
                    }
                )

        print(f"Results written to: {self.output_file}", file=sys.stderr)
        return len(results)


def main():
    # Load environment variables from .env file
    env_config = load_env_config()

    parser = argparse.ArgumentParser(
        description="Find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default=env_config.get("output_file"),
        help="Specify output CSV filename",
    )
    parser.add_argument("--config", help="Specify config file path")
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
        processed_count = checker.process_files(args.directory)
        print(f"Found {processed_count} files that need conversion.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
