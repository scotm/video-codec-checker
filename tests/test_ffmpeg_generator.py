"""Tests for FFmpeg command generation."""

import unittest
from pathlib import Path

from video_codec_checker.ffmpeg_generator import (
    generate_ffmpeg_command,
    get_audio_bitrate,
)


class TestFFmpegGenerator(unittest.TestCase):
    """Test cases for FFmpeg command generation functions."""

    def test_get_audio_bitrate(self):
        """Test audio bitrate determination based on channel count."""
        # Test mono audio
        self.assertEqual(get_audio_bitrate(1), "48k")

        # Test stereo audio
        self.assertEqual(get_audio_bitrate(2), "128k")

        # Test 5.1 surround sound
        for channels in [3, 4, 5, 6]:
            self.assertEqual(get_audio_bitrate(channels), "256k")

        # Test 7.1 or higher surround sound
        for channels in [7, 8, 10]:
            self.assertEqual(get_audio_bitrate(channels), "320k")

    def test_generate_ffmpeg_command(self):
        """Test FFmpeg command generation."""
        # Test with a sample file path and mono audio
        input_file = Path("/path/to/video.mp4")
        channels = 1
        expected = (
            "ffmpeg -y -i '/path/to/video.mp4' -map_metadata -1 -map 0:v:0 -c:v "
            "libsvtav1 -preset 3 -crf 32 -map 0:a:0? -c:a libopus -b:a 48k "
            "'/path/to/video_av1.mkv'"
        )
        self.assertEqual(generate_ffmpeg_command(input_file, channels), expected)

        # Test with stereo audio
        channels = 2
        expected = (
            "ffmpeg -y -i '/path/to/video.mp4' -map_metadata -1 -map 0:v:0 -c:v "
            "libsvtav1 -preset 3 -crf 32 -map 0:a:0? -c:a libopus -b:a 128k "
            "'/path/to/video_av1.mkv'"
        )
        self.assertEqual(generate_ffmpeg_command(input_file, channels), expected)

        # Test with 5.1 surround sound
        channels = 6
        expected = (
            "ffmpeg -y -i '/path/to/video.mp4' -map_metadata -1 -map 0:v:0 -c:v "
            "libsvtav1 -preset 3 -crf 32 -map 0:a:0? -c:a libopus -b:a 256k "
            "'/path/to/video_av1.mkv'"
        )
        self.assertEqual(generate_ffmpeg_command(input_file, channels), expected)

        # Test with no audio (channels == 0) -> -an
        channels = 0
        expected = (
            "ffmpeg -y -i '/path/to/video.mp4' -map_metadata -1 -map 0:v:0 -c:v "
            "libsvtav1 -preset 3 -crf 32 -an '/path/to/video_av1.mkv'"
        )
        self.assertEqual(generate_ffmpeg_command(input_file, channels), expected)


if __name__ == "__main__":
    unittest.main()
