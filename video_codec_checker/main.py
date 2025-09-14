#!/usr/bin/env python3
"""
Script to find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)
Outputs CSV: File,Codec,FFmpeg_Command
State-of-the-art: av1, hevc, h264
"""

import sys
from datetime import datetime

from video_codec_checker.cli import parse_args
from video_codec_checker.concurrency import ProbeExecutor
from video_codec_checker.csv_writer import CsvResultsWriter
from video_codec_checker.ffmpeg_generator import (
    generate_ffmpeg_command,
    get_output_path,
)
from video_codec_checker.models import AppConfig, CsvRow
from video_codec_checker.script_writer import (
    ScriptWriter,
    resolve_trash_config,
)
from video_codec_checker.video_processor import (
    compute_bpp,
    get_video_files,
    probe_video_metadata,
)

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
        # Initialize CSV writer
        csv_writer = CsvResultsWriter(self.output_file)
        csv_writer.open()

        # Optional script writer (lazy creation only when a conversion is needed)
        script: ScriptWriter | None = None
        want_script = bool(script_file)

        # Run metadata probing concurrently
        executor = ProbeExecutor(
            jobs=jobs, ffprobe_args=ffprobe_args, probe_func=probe_video_metadata
        )
        for result in executor.run(video_files):
            file_path = result.path
            codec = result.codec
            channels = result.channels
            # Determine if the file should be included in the report
            include_in_report = bool(codec) and (
                codec not in GOOD_CODECS or codec == "h264"
            )

            if include_in_report:
                abs_in = file_path.resolve()
                # Compute bits-per-pixel for reporting
                bpp = compute_bpp(abs_in, ffprobe_args) or 0.0

                # Generate conversion command only for legacy codecs (not h264)
                ffmpeg_cmd = ""
                if codec and codec not in GOOD_CODECS:
                    ffmpeg_cmd = generate_ffmpeg_command(abs_in, channels)
                    if want_script and script is None:
                        trash_cfg = resolve_trash_config(trash_original)
                        script = ScriptWriter(
                            path=script_file,  # type: ignore[arg-type]
                            delete_original=delete_original,
                            trash_config=trash_cfg,
                        )
                        script.open()
                    if script is not None:
                        if delete_original or trash_original:
                            dst = get_output_path(abs_in)
                            script.write_command(ffmpeg_cmd, abs_in, dst)
                        else:
                            script.write_command_no_cleanup(ffmpeg_cmd)
                    processed_count += 1
                    print(f"Processed: {file_path}", file=sys.stderr)
                else:
                    print(f"Analyzed (h264): {file_path}", file=sys.stderr)

                csv_writer.write_row_dc(
                    CsvRow(
                        file=str(file_path),
                        codec=codec or "",
                        channels=channels,
                        bpp=bpp,
                        command=ffmpeg_cmd,
                    )
                )
            else:
                print(f"Skipped: {file_path}", file=sys.stderr)

        # Close resources
        if script is not None:
            script.close()
            print(f"Script written to: {script_file}", file=sys.stderr)
        csv_writer.close()
        print(f"Results written to: {self.output_file}", file=sys.stderr)

        # Print probe stats summary if fast-probe was enabled
        executor.stats.print_summary(ffprobe_args is not None, stream=sys.stderr)
        return processed_count

    def process_config(self, cfg: AppConfig) -> int:
        """Process using a typed AppConfig."""
        ffargs = cfg.probe.args
        delete = cfg.cleanup.delete_original
        trash = cfg.cleanup.trash_original
        return self.process_files(
            directory=str(cfg.directory),
            jobs=cfg.jobs,
            script_file=str(cfg.script_file) if cfg.script_file else None,
            delete_original=delete,
            trash_original=trash,
            ffprobe_args=ffargs,
        )


def main() -> None:
    cfg = parse_args()

    try:
        checker = VideoCodecChecker(str(cfg.output))
        processed_count = checker.process_config(cfg)
        print(f"Found {processed_count} files that need conversion.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
