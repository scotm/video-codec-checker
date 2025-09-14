"""Configuration handling for video codec checker."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


def _to_bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    v = val.strip().lower()
    return v in {"1", "true", "yes", "on"}


def load_yaml_config(config_file: str | None = None) -> dict:
    """Load configuration from YAML file."""
    # Use provided config file or default location
    if config_file:
        config_path = Path(config_file)
    else:
        # Cross-platform config location
        config_path = Path.home() / ".config" / "check-video-codecs.yml"

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
                return config_data if config_data else {}
        except Exception:
            # We don't have access to sys.stderr here, so we'll just return empty dict
            return {}

    return {}


def load_env_config() -> dict:
    """Load environment variables from .env file."""
    load_dotenv()

    return {
        "output_file": os.environ.get("OUTPUT_FILE"),
        "scan_directory": os.environ.get("SCAN_DIRECTORY", "."),
        "delete_original": _to_bool(os.environ.get("DELETE_ORIGINAL"), False),
        "trash_original": _to_bool(os.environ.get("TRASH_ORIGINAL"), False),
    }
