"""Wizard surface — paste URL → live detection → scope → progress → summary."""

from __future__ import annotations

import time

from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Checkbox, Input, ProgressBar, RichLog, Static

from ..engine_protocol import CaptureOptions, CaptureResult, Detection, ProgressEvent
from ..theme import format_size
from ..widgets import Kicker, PasteInput, esc


def _is_valid_url(url: str) -> bool:
    return url.startswith(("http://", "https://")) and "." in url.split("//", 1)[-1]


def _split_patterns(raw: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in raw.split(",") if p.strip())


# ── Worker→UI messages ───────────────────────────────────────────────────


class WizardDetected(Message):
    def __init__(self, url: str, detection: Detection) -> None:
        self.url = url
        self.detection = detection
        super().__init__()


class WizardDetectFailed(Message):
    def __init__(self, url: str, error: str) -> None:
        self.url = url
        self.error = error
        super().__init__()


class WizardProgress(Message):
    def __init__(self, event: ProgressEvent) -> None:
        self.event = event
        super().__init__()


class WizardDone(Message):
    def __init__(self, result: CaptureResult, duration_s: float) -> None:
        self.result = result
        self.duration_s = duration_s
        super().__init__()


class WizardFailed(Message):
    def __init__(self, error: str) -> None:
        self.error = error
        super().__init__()


class WizardSurface(VerticalScroll):
    """The one action that matters: paste a URL, get Markdown."""

    BINDINGS = [
        ("escape", "cancel_capture", "Cancel"),
    ]

    DEFAULT_CSS = """
    WizardSurface {
        padding: 1 2;
        align-horizontal: center;
    }
    .lede {
        color: $ink-muted;
        margin-bottom: 1;
    }
    #url-input {
        margin-bottom: 0;
    }
    .detect-line {
        height: auto;
        color: $primary;
        text-style: bold;
    }
    .detect-line.detect-failed {
        color: $ink-faint;
        text-style: none;
    }
    #form-region {
        height: auto;
        margin-top: 1;
    }
    #scope-row {
        height: auto;
    }
    .scope-field {
        width: 1fr;
        margin-right: 1;
    }
    #versions-box {
        height: auto;
        margin-top: 1;
        background: $panel;
        border: solid $hairline;
        padding: 0 1;
    }
    #versions-title {
        color: $ink-muted;
        text-style: bold;
        width: auto;
        margin-right: 1;
        padding: 1 0;
    }
    #versions-box Checkbox {
        margin: 0 1 0 0;
    }
    #start-row {
        height: auto;
        margin-top: 1;
    }
    #start-btn {
        min-width: 18;
    }
    #form-hint {
        color: $ink-faint;
        padding: 1 0 0 2;
    }
    #progress-region {
        height: auto;
        margin-top: 1;
    }
    #progress-status-row {
        height: auto;
        align-vertical: middle;
        margin-top: 1;
        margin-bottom: 1;
    }
    #status-line {
        color: $ink-muted;
        width: 1fr;
    }
    #cancel-btn {
        min-width: 16;
        height: 3;
    }
    #event-log {
        height: 8;
    }
    #summary-card {
        margin-top: 1;
    }
    #summary-head {
        margin-bottom: 1;
    }
    #summary-warnings {
        margin-bottom: 1;
    }
    #summary-paths {
        margin-bottom: 1;
    }
    #summary-actions {
        height: auto;
    }
    #summary-actions Button {
        margin-right: 1;
    }
    #error-banner {
        margin-top: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._detection: Detection | None = None
        self._detection_url: str | None = None
        self._pending_start = False
        self._capture_running = False
        self._capture_worker = None
        self._options_used: CaptureOptions | None = None
        self._counts: dict[str, int] = {}
        self._started_at: float = 0.0

    # ── layout ───────────────────────────────────────────────────────

    def compose(self):
        yield Kicker("Capture a documentation site")
        yield Static(
            "Paste a docs URL (Ctrl+V). The provider is detected before anything downloads.",
            classes="lede",
        )
        yield PasteInput(
            placeholder="https://docs.example.com   (Enter to capture)",
            id="url-input",
            classes="mono",
        )
        yield Static("", id="detect-line", classes="detect-line hidden")
        with Vertical(id="form-region"):
            with Horizontal(id="scope-row"):
                with Vertical(classes="scope-field"):
                    yield Static("PATH SCOPE — comma-separated prefixes", classes="field-label")
                    yield PasteInput(
                        placeholder="/api/, /guides/   (empty = whole site)",
                        id="scope-input",
                        classes="mono",
                    )
                with Vertical(classes="scope-field"):
                    yield Static("EXCLUSIONS — patterns inside scope", classes="field-label")
                    yield PasteInput(
                        placeholder="/blog/, /forum/",
                        id="exclude-input",
                        classes="mono",
                    )
            with Horizontal(id="versions-box", classes="hidden"):
                yield Static("SITE VERSIONS:", id="versions-title")
            yield Checkbox(
                "Snapshot previous capture before overwrite", value=True, id="snapshot-check"
            )
            with Horizontal(id="start-row"):
                yield Button("Capture site", variant="primary", id="start-btn")
                yield Static(
                    "Press Enter or click Capture site to start.", id="form-hint"
                )
        yield Static("", id="error-banner", classes="hidden error-banner")
        # Result first, process detail below: the outcome must not sit
        # behind a tall log at short terminal heights.
        with Vertical(id="summary-card", classes="card hidden"):
            yield Static("", id="summary-head", markup=True)
            yield Static("", id="summary-warnings", markup=True)
            yield Static("", id="summary-paths", markup=True)
            with Horizontal(id="summary-actions"):
                yield Button("Open folder", id="open-folder-btn")
                yield Button("View diagnostics", id="view-diag-btn")
                yield Button("New capture", id="new-capture-btn")
        with Vertical(id="progress-region", classes="hidden"):
            yield ProgressBar(total=100, show_eta=False, id="progress-bar")
            with Horizontal(id="progress-status-row"):
                yield Static("", id="status-line", classes="mono")
                yield Button("Cancel capture", variant="error", id="cancel-btn")
            yield RichLog(id="event-log", markup=True, wrap=True, max_lines=400)

    def on_mount(self) -> None:
        self.query_one("#url-input", Input).focus()

    # ── public API used by the shell ─────────────────────────────────

    def prefill(self, url: str) -> None:
        """Fill the URL field (Library → Re-crawl handoff) and detect."""
        self.query_one("#url-input", Input).value = url
        self._run_detect()

    # ── detection flow ───────────────────────────────────────────────

    def _run_detect(self) -> None:
        url = self.query_one("#url-input", Input).value.strip()
        line = self.query_one("#detect-line", Static)
        if not _is_valid_url(url):
            line.remove_class("hidden")
            line.add_class("detect-failed")
            line.update("Enter a full http(s) URL to detect the provider.")
            return
        line.remove_class("hidden", "detect-failed")
        line.update("Detecting provider…")

        engine = self.app.engine

        def job() -> None:
            try:
                detection = engine.detect(url)
            except Exception as exc:  # noqa: BLE001 — surfaced verbatim
                self.app.call_from_thread(
                    self.post_message, WizardDetectFailed(url, str(exc))
                )
            else:
                self.app.call_from_thread(self.post_message, WizardDetected(url, detection))

        self.run_worker(job, thread=True, group="detect", exclusive=True)

    def on_wizard_detected(self, event: WizardDetected) -> None:
        self._detection = event.detection
        self._detection_url = event.url
        det = event.detection
        line = self.query_one("#detect-line", Static)
        line.remove_class("hidden", "detect-failed")
        evidence = f" — {esc(det.evidence)}" if det.evidence else ""
        line.update(f"Detected: [b]{esc(det.provider)}[/b]{evidence}")
        self._render_version_box(det)
        if self._pending_start:
            self._pending_start = False
            self._begin_capture()

    def on_wizard_detect_failed(self, event: WizardDetectFailed) -> None:
        line = self.query_one("#detect-line", Static)
        line.remove_class("hidden")
        line.add_class("detect-failed")
        line.update(f"Detection failed: {esc(event.error)}")
        if self._pending_start:
            self._pending_start = False
            self._begin_capture()

    def _render_version_box(self, detection: Detection) -> None:
        box = self.query_one("#versions-box", Horizontal)
        for child in list(box.query(Checkbox)):
            child.remove()
        versions = detection.site_versions
        if len(versions) > 1:
            box.remove_class("hidden")
            for v in versions:
                box.mount(Checkbox(v, value=True, classes="mono"))
        else:
            box.add_class("hidden")

    # ── capture flow ─────────────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._request_start()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "start-btn":
            self._request_start()
        elif bid == "cancel-btn":
            self.action_cancel_capture()
        elif bid == "open-folder-btn":
            self._open_output_folder()
        elif bid == "view-diag-btn":
            self.app.show_surface("diagnostics")
        elif bid == "new-capture-btn":
            self.reset()

    def action_cancel_capture(self) -> None:
        if not self._capture_running:
            return
        if self._capture_worker is not None:
            self._capture_worker.cancel()
            self._capture_worker = None
        self._capture_running = False
        self.query_one("#form-region", Vertical).disabled = False
        self.query_one("#start-btn", Button).disabled = False
        banner = self.query_one("#error-banner", Static)
        banner.remove_class("hidden")
        banner.update("Capture cancelled.")
        self.app.notify("Capture cancelled.", severity="warning")

    def _request_start(self) -> None:
        url = self.query_one("#url-input", Input).value.strip()
        if not _is_valid_url(url):
            line = self.query_one("#detect-line", Static)
            line.remove_class("hidden")
            line.add_class("detect-failed")
            line.update("Enter a full http(s) URL to detect the provider.")
            self.app.notify("Enter a valid http(s) URL first.", severity="warning")
            return
        if self._detection and self._detection_url == url:
            self._begin_capture()
        else:
            self._pending_start = True
            self._run_detect()

    def _selected_versions(self) -> tuple[str, ...] | None:
        box = self.query_one("#versions-box", Horizontal)
        if box.has_class("hidden"):
            return None
        boxes = list(box.query(Checkbox))
        if not boxes:
            return None
        selected = tuple(
            str(cb.label) for cb in boxes if cb.value
        )
        if len(selected) == len(boxes):
            return None  # all versions == no filter
        return selected or None

    def _begin_capture(self) -> None:
        if self._capture_running:
            return
        url = self.query_one("#url-input", Input).value.strip()
        options = CaptureOptions(
            path_scope=_split_patterns(self.query_one("#scope-input", Input).value),
            exclude_paths=_split_patterns(self.query_one("#exclude-input", Input).value),
            site_versions=self._selected_versions(),
            snapshot=self.query_one("#snapshot-check", Checkbox).value,
        )
        self._options_used = options
        self._counts = {}
        self._capture_running = True
        self._started_at = time.monotonic()

        self.query_one("#form-region", Vertical).disabled = True
        self.query_one("#start-btn", Button).disabled = True
        self.query_one("#error-banner", Static).add_class("hidden")
        self.query_one("#summary-card", Vertical).add_class("hidden")
        progress_region = self.query_one("#progress-region", Vertical)
        progress_region.remove_class("hidden")
        bar = self.query_one("#progress-bar", ProgressBar)
        bar.total = 0
        bar.progress = 0
        log = self.query_one("#event-log", RichLog)
        log.clear()
        log.write(f"[dim]$ gitbook-dl capture {esc(url)}[/dim]")
        self.query_one("#status-line", Static).update("Starting capture…")

        engine = self.app.engine

        def emit(ev: ProgressEvent) -> None:
            self.app.call_from_thread(self.post_message, WizardProgress(ev))

        def job() -> None:
            try:
                result = engine.capture(url, options, progress=emit)
            except Exception as exc:  # noqa: BLE001 — surfaced verbatim
                self.app.call_from_thread(self.post_message, WizardFailed(str(exc)))
            else:
                duration = time.monotonic() - self._started_at
                self.app.call_from_thread(
                    self.post_message, WizardDone(result, duration)
                )

        self._capture_worker = self.run_worker(job, thread=True, group="capture", exclusive=True)

    def on_wizard_progress(self, event: WizardProgress) -> None:
        ev = event.event
        self._counts[ev.kind] = self._counts.get(ev.kind, 0) + 1
        bar = self.query_one("#progress-bar", ProgressBar)
        status = self.query_one("#status-line", Static)
        log = self.query_one("#event-log", RichLog)
        if ev.total:
            if bar.total != ev.total:
                bar.total = ev.total
            bar.progress = ev.done
        if ev.kind == "discovered":
            status.update(f"{ev.total} pages discovered")
            log.write(f"[dim]discovered {ev.total} pages[/dim]")
        elif ev.kind == "downloaded":
            status.update(f"{ev.done}/{ev.total} pages")
            log.write(f"[dim]+ {esc(ev.url)}[/dim]")
        elif ev.kind == "failed":
            detail = f" — {esc(ev.message)}" if ev.message else ""
            # RichLog speaks Rich markup, not Textual $variables.
            log.write(f"[bold red]x {esc(ev.url)}{detail}[/]")
            status.update(f"{ev.done}/{ev.total} pages · failures so far")
        elif ev.kind == "written":
            status.update("Writing output contract…")
            log.write("[dim]wrote page tree · book file · llms.txt[/dim]")

    def on_wizard_done(self, event: WizardDone) -> None:
        self._capture_running = False
        result = event.result
        duration = event.duration_s
        run = self.app.record_run(
            url=result.source_url,
            options=self._options_used or CaptureOptions(),
            detection=self._detection,
            result=result,
            duration_s=duration,
            event_counts=dict(self._counts),
        )
        self.query_one("#form-region", Vertical).disabled = False
        self.query_one("#start-btn", Button).disabled = False
        self.query_one("#status-line", Static).update(
            f"Captured {result.pages_captured} pages in {duration:.1f}s"
        )
        self._render_summary(run)
        # Bring the result into view regardless of terminal height.
        self.query_one("#summary-card").scroll_visible(duration=0)
        self.app.notify(
            f"Captured {result.pages_captured} pages from {result.source_url}",
            severity="information",
        )

    def on_wizard_failed(self, event: WizardFailed) -> None:
        self._capture_running = False
        url = self.query_one("#url-input", Input).value.strip()
        self.app.record_run(
            url=url,
            options=self._options_used or CaptureOptions(),
            detection=self._detection,
            result=None,
            error=event.error,
            duration_s=time.monotonic() - self._started_at,
            event_counts=dict(self._counts),
        )
        self.query_one("#form-region", Vertical).disabled = False
        self.query_one("#start-btn", Button).disabled = False
        banner = self.query_one("#error-banner", Static)
        banner.remove_class("hidden")
        banner.update(f"Capture failed: {esc(event.error)}")
        self.app.notify("Capture failed.", severity="error")

    # ── summary rendering ────────────────────────────────────────────

    def _render_summary(self, run) -> None:
        result = run.result
        assert result is not None
        head = self.query_one("#summary-head", Static)
        chip = f"[reverse] {result.provider.upper()} [/]"
        stats = (
            f"  [b]{result.pages_captured}[/b] pages captured"
            f" · {result.skipped} skipped"
            f" · {run.duration_s:.1f}s"
        )
        head.update(chip + stats)

        warns = self.query_one("#summary-warnings", Static)
        if result.warnings:
            lines = "\n".join(
                f"[$warning]![/] {esc(w)}" for w in result.warnings
            )
            warns.update(lines)
        else:
            warns.update("[dim]No extraction warnings.[/dim]")

        paths = self.query_one("#summary-paths", Static)

        def row(label: str, path) -> str:
            value = str(path) if path else "—"
            return f"[dim]{label:<9}[/dim] {esc(value)}"

        paths.update(
            "\n".join(
                [
                    row("LIBRARY", result.library_path),
                    row("LOCAL", result.local_path),
                    row("BOOK", result.book_file),
                    row("MANIFEST", result.manifest_file),
                    row("SNAPSHOT", result.version_id),
                ]
            )
        )
        self.query_one("#summary-card", Vertical).remove_class("hidden")

    def _open_output_folder(self) -> None:
        run = self.app.state.last_run
        target = None
        if run and run.result:
            target = run.result.local_path or run.result.library_path
        if target is None:
            self.app.notify("Nothing captured yet.", severity="warning")
            return
        self.app.opener(target)

    def reset(self) -> None:
        """Back to a clean form, keeping the URL for a quick re-run."""
        self._detection = None
        self._detection_url = None
        self._pending_start = False
        self._capture_running = False
        self.query_one("#detect-line", Static).add_class("hidden")
        self.query_one("#versions-box", Vertical).add_class("hidden")
        self.query_one("#progress-region", Vertical).add_class("hidden")
        self.query_one("#summary-card", Vertical).add_class("hidden")
        self.query_one("#error-banner", Static).add_class("hidden")
        self.query_one("#form-region", Vertical).disabled = False
        self.query_one("#start-btn", Button).disabled = False
        self.query_one("#url-input", Input).focus()
