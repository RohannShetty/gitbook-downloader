"""Shell-lane tests — config wiring (utils/config.py).

Precedence: built-in defaults < global < project < preset < CLI overrides.
No network; config files are written to temp dirs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gitbook_downloader.api import CaptureOptions
from gitbook_downloader.utils.config import (
    AppConfig,
    capture_options_from_config,
    find_config_files,
    init_default_config,
    load_full_config,
)


def write_toml(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


GLOBAL_TOML = """\
[defaults]
workers = 3
timeout = 30.0
"""

PROJECT_TOML = """\
[defaults]
workers = 7
path_scope = ["/api/"]

[presets.api-docs]
url = "https://docs.example.com/"
max_pages = 500
exclude_paths = ["/forum/"]
site_versions = ["v2"]
output_mode = "local"
snapshot = false
"""


@pytest.fixture
def cfg(tmp_path) -> AppConfig:
    global_path = write_toml(tmp_path / "global.toml", GLOBAL_TOML)
    project_path = write_toml(tmp_path / "project.toml", PROJECT_TOML)
    return load_full_config(project_path=project_path,
                            global_path=global_path)


# ── Precedence ──────────────────────────────────────────────────────────


class TestMergePrecedence:
    def test_defaults_survive_without_files(self, tmp_path):
        cfg = load_full_config(
            project_path=tmp_path / "nope.toml",
            global_path=tmp_path / "also-nope.toml",
        )
        options = capture_options_from_config(cfg)
        assert isinstance(options, CaptureOptions)
        assert options.workers == 5          # built-in default
        assert options.timeout == 20.0
        assert options.max_pages is None     # unlimited
        assert options.snapshot is True
        assert options.output_mode == "both"

    def test_project_overrides_global(self, cfg):
        options = capture_options_from_config(cfg)
        assert options.workers == 7            # project beats global(3)
        assert options.timeout == 30.0         # only global set it
        assert options.path_scope == ("/api/",)

    def test_preset_overrides_files(self, cfg):
        options = capture_options_from_config(cfg, preset="api-docs")
        assert options.max_pages == 500
        assert options.exclude_paths == ("/forum/",)
        assert options.site_versions == ("v2",)
        assert options.output_mode == "local"
        assert options.snapshot is False
        # File-level values still apply where the preset is silent.
        assert options.workers == 7
        assert options.path_scope == ("/api/",)

    def test_cli_overrides_everything(self, cfg):
        options = capture_options_from_config(
            cfg, preset="api-docs",
            cli_overrides={"workers": 9, "max_pages": 10,
                           "output_mode": "library"},
        )
        assert options.workers == 9
        assert options.max_pages == 10
        assert options.output_mode == "library"

    def test_none_cli_overrides_are_ignored(self, cfg):
        options = capture_options_from_config(
            cfg, cli_overrides={"workers": None, "timeout": None},
        )
        assert options.workers == 7   # file value survives a None flag
        assert options.timeout == 30.0


class TestPresetLookup:
    def test_unknown_preset_raises_keyerror(self, cfg):
        with pytest.raises(KeyError, match="nope"):
            capture_options_from_config(cfg, preset="nope")

    def test_preset_url_not_swallowed_into_options(self, cfg):
        table = cfg.preset("api-docs")
        assert table["url"] == "https://docs.example.com/"
        options = capture_options_from_config(cfg, preset="api-docs")
        # CaptureOptions has no url field — the caller consumes it.
        assert not hasattr(options, "url")

    def test_case_insensitive_preset_lookup(self, cfg):
        assert cfg.preset("API-DOCS") is not None


# ── Value coercion ──────────────────────────────────────────────────────


class TestValueCoercion:
    def test_max_pages_zero_means_unlimited(self, tmp_path):
        project = write_toml(tmp_path / "p.toml", "[defaults]\nmax_pages = 0\n")
        options = capture_options_from_config(
            load_full_config(project_path=project))
        assert options.max_pages is None

    def test_max_pages_positive_kept(self, tmp_path):
        project = write_toml(tmp_path / "p.toml",
                             "[defaults]\nmax_pages = 25\n")
        options = capture_options_from_config(
            load_full_config(project_path=project))
        assert options.max_pages == 25

    def test_comma_separated_string_becomes_tuple(self, tmp_path):
        project = write_toml(
            tmp_path / "p.toml",
            '[defaults]\npath_scope = "/api/, /sdk/"\n',
        )
        options = capture_options_from_config(
            load_full_config(project_path=project))
        assert options.path_scope == ("/api/", "/sdk/")

    def test_local_dir_expanded(self, tmp_path, monkeypatch):
        project = write_toml(
            tmp_path / "p.toml",
            f"[defaults]\nlocal_dir = '{tmp_path / 'out'}'\n",  # TOML literal string
        )
        options = capture_options_from_config(
            load_full_config(project_path=project))
        assert options.local_dir == tmp_path / "out"

    def test_invalid_output_mode_falls_back_to_both(self, tmp_path):
        project = write_toml(tmp_path / "p.toml",
                             '[defaults]\noutput_mode = "sideways"\n')
        options = capture_options_from_config(
            load_full_config(project_path=project))
        assert options.output_mode == "both"


# ── Legacy compatibility ────────────────────────────────────────────────


class TestLegacyCompat:
    def test_v6_download_section_still_flattens(self, tmp_path):
        legacy = write_toml(
            tmp_path / "legacy.toml",
            "[download]\nworkers = 4\ntimeout = 12\n\n"
            "[output]\ndir = \"~/docs\"\n",
        )
        cfg = load_full_config(project_path=legacy,
                               global_path=tmp_path / "none.toml")
        assert cfg.values["workers"] == 4
        assert cfg.values["timeout"] == 12
        assert cfg.values["dir"] == "~/docs"

    def test_init_default_config_creates_valid_template(self, tmp_path):
        dest = tmp_path / "sub" / "config.toml"
        result = init_default_config(str(dest))
        assert Path(result).is_absolute()
        content = dest.read_text(encoding="utf-8")
        assert "[defaults]" in content
        assert "[presets]" in content
        # Legacy sections documented for v6 upgraders.
        assert "[download]" in content
        assert "[output]" in content

    def test_find_config_files_reports_existing_only(self, tmp_path):
        existing = write_toml(tmp_path / "found.toml", "")
        files = find_config_files()  # real FS: may or may not have configs
        assert all(Path(p).is_file() for _label, p in files)
