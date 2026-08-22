"""Diagnostics surface — the per-capture explanation.

Answers three questions after every run: why this provider was chosen,
what was excluded, and what extraction warnings were raised.
"""

from __future__ import annotations

from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static

from ..engine_protocol import CaptureRun
from ..theme import format_count
from ..widgets import EmptyState, Kicker, esc


def _rows(pairs: list[tuple[str, str]]) -> str:
    return "\n".join(f"[dim]{label:<14}[/dim] {value}" for label, value in pairs)


class DiagnosticsSurface(VerticalScroll):
    DEFAULT_CSS = """
    DiagnosticsSurface {
        padding: 1 2;
        max-width: 110;
    }
    #diag-cards {
        height: auto;
    }
    .diag-card {
        margin-bottom: 1;
    }
    .diag-title {
        color: $ink-faint;
        text-style: bold;
        margin-bottom: 1;
    }
    #diag-provider-line {
        margin-bottom: 1;
    }
    """

    def compose(self):
        yield Kicker("Diagnostics")
        yield EmptyState(
            "No capture yet",
            "Press 1 and run the Wizard — every decision it makes is explained here.",
            id="diag-empty",
        )
        with Vertical(id="diag-cards", classes="hidden"):
            with Vertical(classes="card diag-card", id="provider-card"):
                yield Static("WHY THIS PROVIDER", classes="diag-title")
                yield Static("", id="diag-provider-line", markup=True)
                yield Static("", id="diag-evidence", markup=True)
            with Vertical(classes="card diag-card", id="scoping-card"):
                yield Static("SCOPING & OPTIONS", classes="diag-title")
                yield Static("", id="diag-scoping", markup=True)
            with Vertical(classes="card diag-card", id="activity-card"):
                yield Static("ACTIVITY", classes="diag-title")
                yield Static("", id="diag-activity", markup=True)
            with Vertical(classes="card diag-card", id="warnings-card"):
                yield Static("EXTRACTION WARNINGS", classes="diag-title")
                yield Static("", id="diag-warnings", markup=True)
            with Vertical(classes="card diag-card", id="output-card"):
                yield Static("OUTPUT CONTRACT", classes="diag-title")
                yield Static("", id="diag-output", markup=True)

    def on_mount(self) -> None:
        self.refresh_from_state()

    def refresh_from_state(self) -> None:
        """Re-render from app.state.last_run (called on surface switch)."""
        run = self.app.state.last_run
        cards = self.query_one("#diag-cards", Vertical)
        empty = self.query_one("#diag-empty", EmptyState)
        if run is None:
            cards.add_class("hidden")
            empty.remove_class("hidden")
            return
        empty.add_class("hidden")
        cards.remove_class("hidden")

        provider_line = self.query_one("#diag-provider-line", Static)
        evidence = self.query_one("#diag-evidence", Static)
        if run.detection is not None:
            chip = f"[reverse] {run.detection.provider.upper()} [/]"
            provider_line.update(chip + f"  {esc(run.url)}")
            if run.detection.evidence:
                evidence.update(
                    f"Chosen because of: [b]{esc(run.detection.evidence)}[/b]."
                )
            else:
                evidence.update(
                    "[dim]No detection evidence recorded for this run.[/dim]"
                )
        else:
            provider_line.update(
                f"[reverse] UNKNOWN [/]  {esc(run.url)}"
            )
            evidence.update(
                "[dim]Detection never completed for this run.[/dim]"
            )

        opts = run.options
        scope = ", ".join(opts.path_scope) if opts.path_scope else "whole site"
        excludes = (
            ", ".join(opts.exclude_paths) if opts.exclude_paths else "none"
        )
        versions = (
            ", ".join(opts.site_versions)
            if opts.site_versions
            else "all detected"
        )
        self.query_one("#diag-scoping", Static).update(
            _rows(
                [
                    ("Path scope", scope),
                    ("Exclusions", excludes),
                    ("Site versions", versions),
                    ("Output mode", opts.output_mode),
                    ("Workers", str(opts.workers)),
                    ("Max pages", "unlimited" if opts.max_pages is None else format_count(opts.max_pages)),
                    ("Snapshot", "on" if opts.snapshot else "off"),
                    ("Timeout", f"{opts.timeout:g}s"),
                ]
            )
        )

        activity = self.query_one("#diag-activity", Static)
        if run.result is not None:
            counts = run.event_counts
            activity.update(
                _rows(
                    [
                        ("Pages captured", format_count(run.result.pages_captured)),
                        ("Skipped", format_count(run.result.skipped)),
                        ("Discovered", format_count(counts.get("discovered", 0))),
                        ("Downloaded", format_count(counts.get("downloaded", 0))),
                        ("Failed", format_count(counts.get("failed", 0))),
                        ("Duration", f"{run.duration_s:.1f}s"),
                    ]
                )
            )
        else:
            activity.update(
                f"[$error]The capture failed before producing output:[/]\n{esc(run.error or 'unknown error')}"
            )

        warnings = self.query_one("#diag-warnings", Static)
        if run.result is not None and run.result.warnings:
            warnings.update(
                "\n".join(f"[$warning]![/] {esc(w)}" for w in run.result.warnings)
            )
        elif run.result is not None:
            warnings.update("[dim]None — extraction ran clean.[/dim]")
        else:
            warnings.update("[dim]Not applicable — no output produced.[/dim]")

        output = self.query_one("#diag-output", Static)
        if run.result is not None:
            result = run.result

            def row(label: str, value) -> str:
                shown = str(value) if value else "—"
                return f"[dim]{label:<14}[/dim] {esc(shown)}"

            output.update(
                "\n".join(
                    [
                        row("Library", result.library_path),
                        row("Local", result.local_path),
                        row("Book file", result.book_file),
                        row("Manifest", result.manifest_file),
                        row("Snapshot id", result.version_id),
                    ]
                )
            )
        else:
            output.update("[dim]Not applicable — no output produced.[/dim]")
