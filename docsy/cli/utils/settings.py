import os
import json
from pathlib import Path
from xdg_base_dirs import (
    xdg_config_home,
)

DEFAULT_CONFIG = {
    "targets": {"getdocsy/docs": "/Users/felix/Documents/getdocsy/docs"}
}


def load_settings():
    """Load settings from config file in XDG config directory."""
    config_path = Path(xdg_config_home()) / "docsy" / "config.json"

    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        # Create default config file if it doesn't exist
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: Invalid config file. Using default settings.")
        return DEFAULT_CONFIG


def save_settings(settings):
    """Save settings to config file in XDG config directory."""
    config_path = Path(xdg_config_home()) / "docsy" / "config.json"

    with open(config_path, "w") as f:
        json.dump(settings, f, indent=4)


# Load settings when module is imported
settings = load_settings()
