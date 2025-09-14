"""Tests for CLI-level behavior in main module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from video_codec_checker.main import VideoCodecChecker


class TestMainScriptOutput(unittest.TestCase):
    """Verify script generation writes expected commands."""

    def test_generates_shell_script_with_commands(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "out.csv")
            sh_path = os.path.join(tmpdir, "convert.sh")

            # Patch file discovery and metadata probing
            with (
                patch(
                    "video_codec_checker.main.get_video_files",
                    return_value=[Path("a.avi"), Path("b.mkv")],
                ),
                patch(
                    "video_codec_checker.main.probe_video_metadata",
                    side_effect=[("mpeg4", 2), ("h264", 2)],
                ),
                patch(
                    "video_codec_checker.main.generate_ffmpeg_command",
                    side_effect=["ffmpeg CMD1"],
                ),
            ):
                checker = VideoCodecChecker(csv_path)
                count = checker.process_files(
                    directory=".", jobs=1, script_file=sh_path
                )

            # Only one legacy file expected
            self.assertEqual(count, 1)

            # Verify script content
            with open(sh_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertTrue(content.startswith("#!/usr/bin/env bash\n"))
            self.assertIn("set -euo pipefail", content)
            self.assertIn("ffmpeg CMD1", content)

    def test_generates_script_with_cleanup_flag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "out.csv")
            sh_path = os.path.join(tmpdir, "convert.sh")

            with patch(
                "video_codec_checker.main.get_video_files",
                return_value=[Path("a.avi")],
            ), patch(
                "video_codec_checker.main.probe_video_metadata",
                return_value=("mpeg4", 2),
            ), patch(
                "video_codec_checker.main.generate_ffmpeg_command",
                return_value="ffmpeg CMD1",
            ), patch(
                "video_codec_checker.main.get_output_path",
                return_value=Path("/abs/out.mkv"),
            ):
                checker = VideoCodecChecker(csv_path)
                count = checker.process_files(
                    directory=".", jobs=1, script_file=sh_path, delete_original=True
                )

            self.assertEqual(count, 1)
            with open(sh_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("run_and_cleanup", content)
            self.assertIn("ffmpeg CMD1", content)

    def test_generates_script_with_trash_flag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "out.csv")
            sh_path = os.path.join(tmpdir, "convert.sh")

            with patch(
                "video_codec_checker.main.get_video_files",
                return_value=[Path("a.avi")],
            ), patch(
                "video_codec_checker.main.probe_video_metadata",
                return_value=("mpeg4", 2),
            ), patch(
                "video_codec_checker.main.generate_ffmpeg_command",
                return_value="ffmpeg CMD1",
            ), patch(
                "video_codec_checker.main.get_output_path",
                return_value=Path("/abs/out.mkv"),
            ), patch(
                "video_codec_checker.main.which",
                side_effect=lambda name: "/usr/bin/trash" if name == "trash" else None,
            ):
                checker = VideoCodecChecker(csv_path)
                count = checker.process_files(
                    directory=".", jobs=1, script_file=sh_path, trash_original=True
                )

            self.assertEqual(count, 1)
            with open(sh_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("cleanup_source", content)
            self.assertIn("USE_TRASH=1", content)
            self.assertIn("TRASH_BIN=trash", content)


if __name__ == "__main__":
    unittest.main()
