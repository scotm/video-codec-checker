"""CLI argument parsing for video codec checker.

Separates environment and YAML config resolution from the main module.
"""

from __future__ import annotations

import argparse
from typing import Any

from video_codec_checker.config import load_env_config, load_yaml_config


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments and merge env/YAML defaults.

    Returns an argparse.Namespace with attributes used by the application.
    """
    env_config = load_env_config()

    parser = argparse.ArgumentParser(
        description=(
            "Find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)"
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
        env_config.get("fast_probe") if env_config.get("fast_probe") is not None else True
    )
    parser.add_argument(
        "--fast-probe",
        action=argparse.BooleanOptionalAction,
        default=fast_probe_default,
        help=(
            "Enable fast ffprobe (-probesize/-analyzeduration). Use --no-fast-probe to disable."
        ),
    )
    parser.add_argument(
        "--probe-size",
        default=env_config.get("ffprobe_probesize") or "5M",
        help=(
            "ffprobe -probesize value (used only with --fast-probe); accepts size suffixes like 1M"
        ),
    )
    parser.add_argument(
        "--analyze-duration",
        default=env_config.get("ffprobe_analyzeduration") or "10M",
        help=(
            "ffprobe -analyzeduration value (used only with --fast-probe); accepts microseconds; supports suffixes like 10M"
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
            "In generated script, move source file to Trash on success (uses macOS Finder/gio/trash when available)"
        ),
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=env_config.get("scan_directory"),
        help="Directory to scan for video files (default: current directory)",
    )

    args = parser.parse_args(argv)

    # Merge YAML config if provided/available
    yaml_config = load_yaml_config(args.config)
    if not args.output:
        args.output = yaml_config.get("output_file")

    return args

