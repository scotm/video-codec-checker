"""Configuration handling for video codec checker."""

import os
from pathlib import Path
from dotenv import load_dotenv
import yaml


def load_yaml_config(config_file=None):
    """Load configuration from YAML file."""
    # Use provided config file or default location
    if config_file:
        config_path = Path(config_file)
    else:
        # Cross-platform config location
        config_path = Path.home() / ".config" / "check-video-codecs.yml"

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return config_data if config_data else {}
        except Exception:
            # We don't have access to sys.stderr here, so we'll just return empty dict
            return {}

    return {}


def load_env_config():
    """Load environment variables from .env file."""
    load_dotenv()

    return {
        "output_file": os.environ.get("OUTPUT_FILE"),
        "scan_directory": os.environ.get("SCAN_DIRECTORY", "."),
    }
