"""ARCHON CLI configuration."""
import os
import json
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

CONFIG_DIR = Path.home() / ".archon"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class ArchonConfig:
    """CLI configuration."""
    api_url: str = "https://api.archon.dev"
    api_key: str = ""


def get_config() -> ArchonConfig:
    """Load config from file, env vars, or defaults."""
    load_dotenv()

    config = ArchonConfig()

    # Try config file first
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            config.api_url = data.get("api_url", config.api_url)
            config.api_key = data.get("api_key", config.api_key)
        except (json.JSONDecodeError, KeyError):
            pass

    # Env vars override
    config.api_url = os.getenv("ARCHON_API_URL", config.api_url)
    config.api_key = os.getenv("ARCHON_API_KEY", config.api_key)

    return config


def save_config(api_url: str, api_key: str) -> None:
    """Save config to ~/.archon/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({
        "api_url": api_url,
        "api_key": api_key,
    }, indent=2))
    # Set restrictive permissions
    CONFIG_FILE.chmod(0o600)
