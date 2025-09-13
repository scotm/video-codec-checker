#!/usr/bin/env python3
"""
Script to find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)
Outputs CSV: File,Codec,FFmpeg_Command
State-of-the-art: av1, hevc, h264
"""

import argparse
import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import os

# Try to import dotenv, but handle case where it's not available
try:
    from dotenv import load_dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False


class VideoCodecChecker:
    GOOD_CODECS = {"av1", "hevc", "h264"}
    VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp", ".ogv"}

    def __init__(self, output_file=None):
        self.output_file = output_file or f"video_codec_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    def get_video_files(self, directory="."):
        """Find all video files recursively in the given directory."""
        path = Path(directory)
        video_files = []

        for ext in self.VIDEO_EXTENSIONS:
            video_files.extend(path.rglob(f"*{ext}"))
            video_files.extend(path.rglob(f"*{ext.upper()}"))

        return sorted(set(video_files))  # Remove duplicates and sort

    def get_video_codec(self, file_path):
        """Extract video codec from file using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def get_audio_channels(self, file_path):
        """Extract audio channels from file using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-select_streams", "a:0",
                "-show_entries", "stream=channels",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            channels = result.stdout.strip()
            return int(channels) if channels.isdigit() else 0
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            return 0

    def get_audio_bitrate(self, channels):
        """Determine optimal Opus bitrate based on audio channels."""
        if channels == 1:
            return "48k"  # Mono
        elif channels == 2:
            return "128k"  # Stereo
        elif 3 <= channels <= 6:
            return "256k"  # 5.1 surround
        else:
            return "320k"  # 7.1 or higher

    def generate_ffmpeg_command(self, input_file, channels):
        """Generate FFmpeg command to convert video to AV1 and audio to Opus."""
        output_file = input_file.with_stem(input_file.stem + "_av1").with_suffix(".mkv")
        audio_bitrate = self.get_audio_bitrate(channels)

        cmd_parts = [
            "ffmpeg",
            "-i", f"'{input_file}'",
            "-map_metadata", "-1",
            "-c:v", "libsvtav1",
            "-preset", "4",
            "-crf", "32",
            "-c:a", "libopus",
            "-b:a", audio_bitrate,
            f"'{output_file}'"
        ]

        return " ".join(cmd_parts)

    def process_files(self, directory="."):
        """Process all video files and generate CSV output."""
        video_files = self.get_video_files(directory)
        results = []

        print(f"Processing {len(video_files)} video files...", file=sys.stderr)

        for file_path in video_files:
            abs_file = file_path.resolve()
            codec = self.get_video_codec(file_path)
            channels = self.get_audio_channels(file_path)

            if codec and codec not in self.GOOD_CODECS:
                ffmpeg_cmd = self.generate_ffmpeg_command(abs_file, channels)
                results.append({
                    "file": str(file_path),
                    "codec": codec,
                    "ffmpeg_command": ffmpeg_cmd
                })
                print(f"Processed: {file_path}", file=sys.stderr)
            else:
                print(f"Skipped: {file_path}", file=sys.stderr)

        # Write CSV output
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["File", "Codec", "FFmpeg_Command"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow({
                    "File": result["file"],
                    "Codec": result["codec"],
                    "FFmpeg_Command": result["ffmpeg_command"]
                })

        print(f"Results written to: {self.output_file}", file=sys.stderr)
        return len(results)


def main():
    # Load environment variables from .env file if dotenv is available
    if dotenv_available:
        load_dotenv()

    parser = argparse.ArgumentParser(
        description="Find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)"
    )
    parser.add_argument(
        "-o", "--output",
        default=os.environ.get("OUTPUT_FILE") if dotenv_available else None,
        help="Specify output CSV filename"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.environ.get("SCAN_DIRECTORY", ".") if dotenv_available else ".",
        help="Directory to scan for video files (default: current directory)"
    )

    args = parser.parse_args()

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
