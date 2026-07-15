"""Configuration file loader for GitBook Downloader v6.

Searches for TOML config files in conventional locations, merges them with
built-in defaults, and allows CLI arguments to take precedence.

Config search order (first found wins):
  1. ``./gitbook-downloader.toml``
  2. ``~/.gitbook-downloader/config.toml``
  3. ``~/.config/gitbook-downloader/config.toml``
"""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── TOML parser: use stdlib tomllib (3.11+), fall back to tomli ──
try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

# ── Default configuration values ──
DEFAULTS: dict[str, Any] = {
    "workers": 5,
    "timeout": 20,
    "retry_attempts": 3,
    "output_dir": "~/.gitbook-downloader",
    "max_pages": 0,
    "prefer_md": True,
    "use_llms_txt": True,
    "min_content_chars": 60,
}

# Locations where a config file might live (relative → home-expanded).
_CONFIG_SEARCH_PATHS: list[str] = [
    "./gitbook-downloader.toml",
    "~/.gitbook-downloader/config.toml",
    "~/.config/gitbook-downloader/config.toml",
]

# ── Default TOML template written by init_default_config() ──
_DEFAULT_TOML = """\
# GitBook Downloader v6 configuration
# Uncomment and modify values as needed.

[download]
# workers        = 5
# timeout        = 20
# retry_attempts = 3
# max_pages      = 0        # 0 = unlimited
# prefer_md      = true
# use_llms_txt   = true
# min_content_chars = 60

[output]
# dir = "~/.gitbook-downloader"
"""


def _find_config_file() -> str | None:
    """Return the first existing config file path from the search list, or None."""
    for pattern in _CONFIG_SEARCH_PATHS:
        expanded = os.path.expanduser(pattern)
        if os.path.isfile(expanded):
            logger.debug("Found config file: %s", expanded)
            return expanded
    return None


def _read_toml(path: str) -> dict[str, Any]:
    """Read a TOML file and return its contents as a flat dict.

    Handles the common case where config values sit under sections
    (e.g. ``[download] workers = 5``) by flattening to a single-level dict
    with just the leaf keys.  Top-level keys are kept as-is.
    """
    if tomllib is None:
        logger.warning("No TOML parser available (need tomllib or tomli). Config file ignored.")
        return {}

    with open(path, "rb") as fh:
        data = tomllib.load(fh)

    flat: dict[str, Any] = {}
    for _section, values in data.items():
        if isinstance(values, dict):
            flat.update(values)
        else:
            # Top-level scalar (e.g. bare `workers = 5`)
            flat[_section] = values
    return flat


def load_config() -> dict[str, Any]:
    """Load and merge configuration from the first found config file.

    Returns:
        A dict of configuration values.  Values present in the config file
        override :data:`DEFAULTS`; missing keys fall back to defaults.
    """
    config_path = _find_config_file()
    if config_path is None:
        logger.info("No config file found; using defaults.")
        return dict(DEFAULTS)

    file_cfg = _read_toml(config_path)
    merged = {**DEFAULTS, **file_cfg}
    logger.info("Loaded config from %s (%d overrides)", config_path, len(file_cfg))
    return merged


def merge_config(cli_args: dict[str, Any], file_config: dict[str, Any]) -> dict[str, Any]:
    """Merge CLI arguments on top of file-loaded configuration.

    CLI arguments that are ``None`` (meaning "not provided") are ignored
    so the file/default value survives.  Boolean flags like ``--no-llms-txt``
    that are explicitly set by argparse are always respected.

    Args:
        cli_args: Dict of CLI argument values (e.g. from ``vars(args)``).
        file_config: Config dict from :func:`load_config`.

    Returns:
        Merged configuration dict (CLI wins when not ``None``).
    """
    merged = dict(file_config)
    for key, value in cli_args.items():
        if value is not None:
            merged[key] = value
    return merged


def init_default_config(path: str | None = None) -> str:
    """Write a default config file so users can edit it.

    Args:
        path: Destination path.  Defaults to ``~/.gitbook-downloader/config.toml``.

    Returns:
        The absolute path of the written file.
    """
    if path is None:
        path = os.path.expanduser("~/.gitbook-downloader/config.toml")

    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        logger.info("Config file already exists at %s — skipping write.", dest)
        return str(dest.resolve())

    dest.write_text(_DEFAULT_TOML, encoding="utf-8")
    logger.info("Wrote default config to %s", dest)
    return str(dest.resolve())
