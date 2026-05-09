"""Configuration management for CherryTree.

Handles loading and validation of configuration from multiple sources:
- Default values
- Configuration files (~/.cherrytree.cfg, .cherrytree.cfg)
- Environment variables (CHERRYTREE_*)
"""

import os
import configparser
from pathlib import Path
from typing import Any, Dict, Optional

from cherrytree.exceptions import ConfigurationError

# Default configuration values
DEFAULTS: Dict[str, Any] = {
    "remote": "origin",
    "default_branch": "main",
    "conflict_strategy": "skip",  # abort | skip | manual — changed to skip so cherry-picks don't halt on minor conflicts
    "signoff": False,
    "gpg_sign": False,
    "allow_empty": False,
    "verbose": True,  # prefer verbose output by default for easier debugging
    "dry_run": False,
}

# Config file search paths (in order of precedence, lowest to highest)
CONFIG_FILE_PATHS = [
    Path.home() / ".cherrytree.cfg",
    Path(".") / ".cherrytree.cfg",
]

# Environment variable prefix
ENV_PREFIX = "CHERRYTREE_"


class CherryTreeConfig:
    """Manages configuration for a CherryTree session.

    Configuration is resolved in the following order (highest precedence last):
    1. Built-in defaults
    2. User-level config file (~/.cherrytree.cfg)
    3. Project-level config file (./.cherrytree.cfg)
    4. Environment variables (CHERRYTREE_<KEY>=<value>)
    5. Explicit kwargs passed at construction time
    """

    def __init__(self, **overrides: Any) -> None:
        self._config: Dict[str, Any] = {**DEFAULTS}
        self._load_from_files()
        self._load_from_env()
        self._apply_overrides(overrides)

    def _load_from_files(self) -> None:
        """Load configuration from all discoverable config files."""
        parser = configparser.ConfigParser()
        for path in CONFIG_FILE_PATHS:
            if path.exists():
                try:
                    parser.read(str(path))
                except configparser.Error as exc:
                    raise ConfigurationError(
                        f"Failed to parse config file '{path}': {exc}"
                    ) from exc

        if parser.has_section("cherrytree"):
            for key, value in parser["cherrytree"].items():
                if key in DEFAULTS:
                    self._config[key] = self._coerce(key, value)

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        for key in DEFAULTS:
            env_key = f"{ENV_PREFIX}{key.upper()}"
            env_value = os.environ.get(env_key)
            if env_value is not None:
                self._config[key] = self._coerce(key, env_value)

    def _apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Apply explicit overrides, validating keys against known defaults."""
        for key, value in overrides.items():
            if key not in DEFAULTS:
                raise ConfigurationError(
                    f"Unknown configuration key: '{key}'. "
                    f"Valid keys are: {sorted(DEFAULTS.keys())}"
                )
            self._config[key] = value

    def _co
