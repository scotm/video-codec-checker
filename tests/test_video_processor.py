"""Tests for video processing functionality."""

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from video_codec_checker.video_processor import (
    get_audio_channels,
    get_video_codec,
    get_video_files,
    probe_video_metadata,
)


class TestVideoProcessor(unittest.TestCase):
    """Test cases for video processing functions."""

    def test_get_video_files_default_extensions(self):
        """Test get_video_files with default extensions."""
        # Mock Path.rglob to return specific files
        with patch("video_codec_checker.video_processor.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance

            # Mock rglob to return specific files for each extension
            mock_files = [
                Path("test.mp4"),
                Path("test.avi"),
                Path("test.mkv"),
            ]
            mock_path_instance.rglob.return_value = mock_files

            result = get_video_files(".")
            # Should return a list of Path objects
            self.assertIsInstance(result, list)
            # Single directory walk expected
            mock_path_instance.rglob.assert_called_with("*")
            self.assertEqual(mock_path_instance.rglob.call_count, 1)

    def test_get_video_files_custom_extensions(self):
        """Test get_video_files with custom extensions."""
        custom_extensions = {".mov", ".wmv"}

        with patch("video_codec_checker.video_processor.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            mock_path_instance.rglob.return_value = [Path("test.mov")]

            result = get_video_files(".", custom_extensions)
            self.assertIsInstance(result, list)

    def test_get_video_codec_success(self):
        """Test get_video_codec with successful ffprobe execution."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "h264\n"
            mock_run.return_value = mock_result

            result = get_video_codec(Path("test.mp4"))
            self.assertEqual(result, "h264")

    def test_get_video_codec_failure(self):
        """Test get_video_codec when ffprobe fails."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_run.return_value = mock_result

            result = get_video_codec(Path("test.mp4"))
            self.assertIsNone(result)

    def test_get_video_codec_timeout(self):
        """Test get_video_codec when ffprobe times out."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("ffprobe", 30)

            result = get_video_codec(Path("test.mp4"))
            self.assertIsNone(result)

    def test_get_video_codec_file_not_found(self):
        """Test get_video_codec when ffprobe is not found."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = get_video_codec(Path("test.mp4"))
            self.assertIsNone(result)

    def test_get_audio_channels_success(self):
        """Test get_audio_channels with successful ffprobe execution."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "2\n"
            mock_run.return_value = mock_result

            result = get_audio_channels(Path("test.mp4"))
            self.assertEqual(result, 2)

    def test_get_audio_channels_non_digit(self):
        """Test get_audio_channels when ffprobe returns non-digit output."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "invalid\n"
            mock_run.return_value = mock_result

            result = get_audio_channels(Path("test.mp4"))
            self.assertEqual(result, 0)

    def test_get_audio_channels_failure(self):
        """Test get_audio_channels when ffprobe fails."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_run.return_value = mock_result

            result = get_audio_channels(Path("test.mp4"))
            self.assertEqual(result, 0)

    def test_get_audio_channels_timeout(self):
        """Test get_audio_channels when ffprobe times out."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("ffprobe", 30)

            result = get_audio_channels(Path("test.mp4"))
            self.assertEqual(result, 0)

    def test_get_audio_channels_value_error(self):
        """Test get_audio_channels when conversion to int fails."""
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "not_a_number\n"
            mock_run.return_value = mock_result

            result = get_audio_channels(Path("test.mp4"))
            self.assertEqual(result, 0)

    def test_probe_video_metadata_json(self):
        """Test single ffprobe call returns codec and channels from JSON output."""
        json_output = {
            "streams": [
                {"index": 0, "codec_type": "video", "codec_name": "mpeg4"},
                {"index": 1, "codec_type": "audio", "channels": 2},
            ]
        }
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps(json_output)
            mock_run.return_value = mock_result

            codec, channels = probe_video_metadata(Path("test.avi"))
            self.assertEqual(codec, "mpeg4")
            self.assertEqual(channels, 2)

    def test_probe_video_metadata_errors(self):
        """Test probe_video_metadata handling of bad output and exceptions."""
        # Non-zero return
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_run.return_value = mock_result
            codec, channels = probe_video_metadata(Path("bad.mkv"))
            self.assertIsNone(codec)
            self.assertEqual(channels, 0)

        # Timeout
        with patch("video_codec_checker.video_processor.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("ffprobe", 30)
            codec, channels = probe_video_metadata(Path("timeout.mp4"))
            self.assertIsNone(codec)
            self.assertEqual(channels, 0)


if __name__ == "__main__":
    unittest.main()
