"""Tests for configuration handling."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from video_codec_checker.config import load_yaml_config, load_env_config


class TestConfig(unittest.TestCase):
    """Test cases for configuration functions."""

    @patch("video_codec_checker.config.Path.exists")
    @patch("video_codec_checker.config.open")
    @patch("video_codec_checker.config.yaml.safe_load")
    def test_load_yaml_config_with_file(self, mock_safe_load, mock_open, mock_exists):
        """Test load_yaml_config when config file exists."""
        mock_exists.return_value = True
        mock_safe_load.return_value = {
            "output_file": "test.csv",
            "scan_directory": "/videos",
        }

        result = load_yaml_config("test_config.yml")
        self.assertEqual(
            result, {"output_file": "test.csv", "scan_directory": "/videos"}
        )

    @patch("video_codec_checker.config.Path.exists")
    def test_load_yaml_config_without_file(self, mock_exists):
        """Test load_yaml_config when config file doesn't exist."""
        mock_exists.return_value = False

        result = load_yaml_config("nonexistent_config.yml")
        self.assertEqual(result, {})

    @patch("video_codec_checker.config.Path.exists")
    @patch("video_codec_checker.config.open")
    @patch("video_codec_checker.config.yaml.safe_load")
    def test_load_yaml_config_with_exception(
        self, mock_safe_load, mock_open, mock_exists
    ):
        """Test load_yaml_config when yaml loading fails."""
        mock_exists.return_value = True
        mock_safe_load.side_effect = Exception("YAML error")

        result = load_yaml_config("test_config.yml")
        self.assertEqual(result, {})

    @patch("video_codec_checker.config.Path.exists")
    @patch("video_codec_checker.config.open")
    @patch("video_codec_checker.config.yaml.safe_load")
    def test_load_yaml_config_empty_data(self, mock_safe_load, mock_open, mock_exists):
        """Test load_yaml_config when yaml file is empty or contains null data."""
        mock_exists.return_value = True
        mock_safe_load.return_value = None

        result = load_yaml_config("test_config.yml")
        self.assertEqual(result, {})

    @patch("video_codec_checker.config.Path.home")
    @patch("video_codec_checker.config.Path.exists")
    @patch("video_codec_checker.config.open")
    @patch("video_codec_checker.config.yaml.safe_load")
    def test_load_yaml_config_default_location(
        self, mock_safe_load, mock_open, mock_exists, mock_home
    ):
        """Test load_yaml_config with default config location."""
        mock_home.return_value = Path("/home/user")
        mock_exists.return_value = True
        mock_safe_load.return_value = {"output_file": "default.csv"}

        result = load_yaml_config()
        self.assertEqual(result, {"output_file": "default.csv"})

    @patch.dict(
        os.environ, {"OUTPUT_FILE": "env_output.csv", "SCAN_DIRECTORY": "/env_videos"}
    )
    @patch("video_codec_checker.config.load_dotenv")
    def test_load_env_config_with_values(self, mock_load_dotenv):
        """Test load_env_config when environment variables are set."""
        mock_load_dotenv.return_value = True

        result = load_env_config()
        self.assertEqual(result["output_file"], "env_output.csv")
        self.assertEqual(result["scan_directory"], "/env_videos")

    @patch.dict(os.environ, {}, clear=True)
    @patch("video_codec_checker.config.load_dotenv")
    def test_load_env_config_without_values(self, mock_load_dotenv):
        """Test load_env_config when environment variables are not set."""
        mock_load_dotenv.return_value = True

        result = load_env_config()
        self.assertIsNone(result["output_file"])
        self.assertEqual(result["scan_directory"], ".")


if __name__ == "__main__":
    unittest.main()
