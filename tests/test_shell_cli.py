"""Shell-lane tests — the v7 CLI surface (plan §5).

Parser-level tests only: no network, no real captures. The facade and TUI
launcher are monkeypatched.
"""

from __future__ import annotations

import pytest

from gitbook_downloader import cli


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Every CLI test runs in a temp CWD with a temp library — never the
    real ~/.gitbook-downloader, never the repo."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path / "library"))
    return tmp_path


@pytest.fixture
def no_tui(monkeypatch):
    """Replace GUI and TUI launchers so bare invocations don't open windows."""
    calls = []
    monkeypatch.setattr(cli, "_launch_gui", lambda: calls.append("gui") or 0)
    monkeypatch.setattr(cli, "_launch_tui", lambda: calls.append("tui") or 0)
    return calls


@pytest.fixture
def fake_capture(monkeypatch):
    """Replace the facade entry used by cmd_capture."""
    recorded = {}

    def fake_capture_fn(url, options, progress=None):
        recorded["url"] = url
        recorded["options"] = options
        result = pytest.importorskip("gitbook_downloader.api").CaptureResult(
            source_url=url, provider="gitbook",
            site_versions_found=("v2",), pages_captured=2, skipped=1,
            warnings=(), library_path=None, local_path=None,
            book_file=None, manifest_file=None, version_id=None,
        )
        return result

    from gitbook_downloader import api
    monkeypatch.setattr(api, "capture", fake_capture_fn)
    return recorded


# ── Command surface ─────────────────────────────────────────────────────


class TestCommandSurface:
    def test_help_lists_v7_commands(self, capsys):
        with pytest.raises(SystemExit) as exc:
            cli.main(["--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        for command in ("capture", "search", "ls", "history", "diff",
                        "split", "config", "mcp", "tui", "gui"):
            assert command in out

    def test_gui_subcommand_exists(self, no_tui):
        parser = cli.build_parser()
        args = parser.parse_args(["gui"])
        assert args.command == "gui"

    def test_no_customtkinter_references(self):
        source = cli.__file__
        text = open(source, encoding="utf-8").read()
        assert "customtkinter" not in text
        assert "dashboard" not in text

    @pytest.mark.parametrize("alias", ["dl", "list"])
    def test_aliases_exist(self, alias):
        parser = cli.build_parser()
        args = parser.parse_args([alias])
        assert args.command == alias

    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as exc:
            cli.main(["--version"])
        assert exc.value.code == 0
        assert "gitbook-downloader" in capsys.readouterr().out


# ── Bare-URL sugar & bare invocation ────────────────────────────────────


class TestBareInvocation:
    def test_bare_invocation_launches_gui(self, no_tui):
        assert cli.main([]) == 0
        assert no_tui == ["gui"]

    def test_gui_subcommand_launches_gui(self, no_tui):
        assert cli.main(["gui"]) == 0
        assert no_tui == ["gui"]

    def test_tui_subcommand_launches_tui(self, no_tui):
        assert cli.main(["tui"]) == 0
        assert no_tui == ["tui"]

    @pytest.mark.parametrize("url", [
        "https://docs.example.com/",
        "http://docs.example.com/guide",
    ])
    def test_bare_url_is_sugar_for_capture(self, url, no_tui,
                                           fake_capture, tmp_path,
                                           monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = cli.main([url])
        assert rc == 0
        assert fake_capture["url"] == url

    def test_missing_tui_prints_friendly_message(self, monkeypatch, capsys):
        def missing_tui():
            raise ImportError("No module named 'textual'")

        monkeypatch.setattr(cli, "_import_tui_run", missing_tui)
        rc = cli._launch_tui()
        assert rc == 1
        err = capsys.readouterr().err
        assert "TUI" in err
        assert "gitbook-dl capture" in err



# ── Capture flag parsing ────────────────────────────────────────────────


class TestCaptureFlags:
    def test_all_flags_reach_the_facade(self, tmp_path, monkeypatch,
                                        fake_capture):
        monkeypatch.chdir(tmp_path)
        rc = cli.main([
            "capture", "https://docs.example.com/",
            "--scope", "/api/", "--scope", "/sdk/",
            "--exclude", "/forum/",
            "--max-pages", "50",
            "--workers", "4",
            "--versions", "v1,v2",
            "--output", "local",
            "-o", str(tmp_path / "out"),
        ])
        assert rc == 0
        options = fake_capture["options"]
        assert options.path_scope == ("/api/", "/sdk/")
        assert options.exclude_paths == ("/forum/",)
        assert options.max_pages == 50
        assert options.workers == 4
        assert options.site_versions == ("v1", "v2")
        assert options.output_mode == "local"
        assert options.local_dir == tmp_path / "out"
        assert options.snapshot is True

    def test_latest_only_maps_to_sentinel(self, tmp_path, monkeypatch,
                                          fake_capture):
        from gitbook_downloader.api import LATEST_ONLY

        monkeypatch.chdir(tmp_path)
        cli.main(["dl", "https://docs.example.com/", "--latest-only"])
        assert fake_capture["options"].site_versions == (LATEST_ONLY,)

    def test_no_snapshot_flag(self, tmp_path, monkeypatch, fake_capture):
        monkeypatch.chdir(tmp_path)
        cli.main(["capture", "https://docs.example.com/", "--no-snapshot"])
        assert fake_capture["options"].snapshot is False

    def test_preset_supplies_url(self, tmp_path, monkeypatch,
                                 fake_capture):
        config = tmp_path / "gitbook-downloader.toml"
        config.write_text(
            '[presets.api]\nurl = "https://docs.example.com/"\n',
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        rc = cli.main(["capture", "--preset", "api"])
        assert rc == 0
        assert fake_capture["url"] == "https://docs.example.com/"

    def test_unknown_preset_exits_2(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = cli.main(["capture", "--preset", "ghost"])
        assert rc == 2
        assert "ghost" in capsys.readouterr().err

    def test_no_url_and_no_preset_exits_2(self, tmp_path, monkeypatch,
                                          capsys):
        monkeypatch.chdir(tmp_path)
        rc = cli.main(["capture"])
        assert rc == 2

    def test_bad_max_pages_exits_nonzero(self, tmp_path, monkeypatch,
                                         capsys):
        monkeypatch.chdir(tmp_path)
        rc = cli.main(["capture", "https://docs.example.com/",
                       "--max-pages", "0"])
        assert rc != 0


# ── Config subcommands ──────────────────────────────────────────────────


class TestConfigCommands:
    def test_config_show_runs(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        assert cli.main(["config", "show"]) == 0
        assert "Configuration" in capsys.readouterr().out

    def test_config_init_creates_project_file(self, tmp_path, monkeypatch,
                                              capsys):
        monkeypatch.chdir(tmp_path)
        assert cli.main(["config", "init", "--project"]) == 0
        assert (tmp_path / "gitbook-downloader.toml").exists()

    def test_config_path_lists_search_order(self, tmp_path, monkeypatch,
                                            capsys):
        monkeypatch.chdir(tmp_path)
        assert cli.main(["config", "path"]) == 0
        out = capsys.readouterr().out
        assert "global" in out and "project" in out

    def test_config_defaults_to_show(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        assert cli.main(["config"]) == 0
        assert "Configuration" in capsys.readouterr().out


# ── History / diff argument handling ────────────────────────────────────


class TestHistoryAndDiff:
    def test_history_unknown_domain_exits_1(self, tmp_path, monkeypatch,
                                            capsys):
        monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path))
        rc = cli.main(["history", "ghost.example.com"])
        assert rc == 1

    def test_diff_unknown_domain_exits_1(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path))
        rc = cli.main(["diff", "ghost.example.com", "v1.0.0", "v1.0.1"])
        assert rc == 1

    def test_history_shows_snapshots(self, tmp_path, monkeypatch, capsys):
        from gitbook_downloader.storage import StorageManager, VersionManager

        monkeypatch.setenv("GITBOOK_DOWNLOADER_HOME", str(tmp_path))
        sm = StorageManager(base_dir=tmp_path)
        sm.save_doc(domain="d.com", content="C", url="u", title="T",
                    pages=1, provider="g", new_pages=1, size_kb=0.1)
        VersionManager(sm).snapshot("d.com")

        assert cli.main(["history", "d.com"]) == 0
        out = capsys.readouterr().out
        assert "v1.0.1" in out


# ── Console encoding robustness ─────────────────────────────────────────


class TestConsoleEncoding:
    def test_configure_console_streams_handles_non_utf8(self, monkeypatch):
        class FakeStream:
            def __init__(self):
                self.reconfigured_with = None

            def reconfigure(self, **kwargs):
                self.reconfigured_with = kwargs

        fake_out = FakeStream()
        fake_err = FakeStream()
        monkeypatch.setattr(cli.sys, "stdout", fake_out)
        monkeypatch.setattr(cli.sys, "stderr", fake_err)

        cli._configure_console_streams()
        assert fake_out.reconfigured_with == {"encoding": "utf-8", "errors": "replace"}
        assert fake_err.reconfigured_with == {"encoding": "utf-8", "errors": "replace"}

