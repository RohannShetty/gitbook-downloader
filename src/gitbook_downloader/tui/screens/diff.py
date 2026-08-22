"""Diff surface — pick a domain + two snapshots, see what changed."""

from __future__ import annotations

from rich.text import Text

from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Select, Static

from ..engine_protocol import DiffReport, PageChange, SnapshotInfo
from ..theme import format_count
from ..widgets import EmptyState, Kicker, esc

_STATUS_GLYPH = {"added": "+", "removed": "-", "changed": "~"}
_STATUS_STYLE = {
    "added": "$success",
    "removed": "$error",
    "changed": "$primary",
}


class DiffSurface(VerticalScroll):
    DEFAULT_CSS = """
    DiffSurface {
        padding: 1 2;
    }
    #diff-controls {
        height: auto;
        margin-bottom: 1;
    }
    #diff-controls Select {
        width: 1fr;
    }
    #diff-controls Select#diff-domain {
        width: 2fr;
    }
    #compare-btn {
        margin-left: 1;
    }
    #diff-summary {
        color: $ink-muted;
        margin-bottom: 1;
    }
    #changes-table {
        height: 1fr;
        min-height: 6;
        margin-bottom: 1;
    }
    #diff-panes {
        height: 16;
    }
    .diff-pane {
        width: 1fr;
    }
    #pane-old {
        margin-right: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._snapshots: list[SnapshotInfo] = []
        self._report: DiffReport | None = None

    def compose(self):
        yield Kicker("Snapshot diff")
        with Horizontal(id="diff-controls"):
            yield Select([], prompt="Domain", id="diff-domain", allow_blank=True)
            yield Select([], prompt="Older snapshot", id="diff-old", allow_blank=True)
            yield Select([], prompt="Newer snapshot", id="diff-new", allow_blank=True)
            yield Button("Compare", variant="primary", id="compare-btn")
        yield Static("", id="diff-summary")
        yield DataTable(id="changes-table", cursor_type="row", zebra_stripes=True)
        yield EmptyState(
            "Pick two snapshots",
            "Every re-crawl snapshots the previous capture — compare any pair.",
            id="diff-empty",
        )
        with Horizontal(id="diff-panes", classes="hidden"):
            with Vertical(classes="diff-pane", id="pane-old"):
                yield Static("OLD", classes="diff-pane-title")
                yield Static("", id="old-excerpt", markup=True)
            with Vertical(classes="diff-pane", id="pane-new"):
                yield Static("NEW", classes="diff-pane-title")
                yield Static("", id="new-excerpt", markup=True)

    def on_mount(self) -> None:
        table = self.query_one("#changes-table", DataTable)
        table.add_columns("STATUS", "PAGE", "+ LINES", "- LINES")
        self.refresh_domains()

    def refresh_domains(self) -> None:
        select = self.query_one("#diff-domain", Select)
        try:
            entries = self.app.engine.list_library()
        except Exception:  # noqa: BLE001
            entries = []
        select.set_options([(e.domain, e.domain) for e in entries])

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "diff-domain":
            return
        domain = event.value
        if not domain:
            return
        try:
            self._snapshots = list(self.app.engine.list_snapshots(domain))
        except Exception as exc:  # noqa: BLE001
            self.app.notify(f"Could not list snapshots: {exc}", severity="error")
            self._snapshots = []

        def label(s: SnapshotInfo) -> str:
            return f"{s.version_id} · {s.created_at} · {format_count(s.pages)}p"

        old_sel = self.query_one("#diff-old", Select)
        new_sel = self.query_one("#diff-new", Select)
        options = [(label(s), s.version_id) for s in self._snapshots]
        old_sel.set_options(options)
        new_sel.set_options(options)
        if len(self._snapshots) >= 2:
            new_sel.value = self._snapshots[0].version_id
            old_sel.value = self._snapshots[1].version_id
        elif len(self._snapshots) == 1:
            new_sel.value = self._snapshots[0].version_id
            old_sel.value = Select.BLANK

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "compare-btn":
            return
        domain_sel = self.query_one("#diff-domain", Select)
        old_sel = self.query_one("#diff-old", Select)
        new_sel = self.query_one("#diff-new", Select)

        def chosen(select: Select) -> str | None:
            # Blank selects hold a sentinel (Select.NULL), never a real string.
            value = select.value
            return value if isinstance(value, str) and value else None

        domain = chosen(domain_sel)
        old_version = chosen(old_sel)
        new_version = chosen(new_sel)
        if not (domain and old_version and new_version):
            self.app.notify(
                "Pick a domain and two snapshots first.", severity="warning"
            )
            return
        try:
            report = self.app.engine.diff_snapshots(domain, old_version, new_version)
        except Exception as exc:  # noqa: BLE001
            self.app.notify(f"Diff failed: {exc}", severity="error")
            return
        self._render_report(report)

    def _render_report(self, report: DiffReport) -> None:
        self._report = report
        table = self.query_one("#changes-table", DataTable)
        table.clear()
        summary = self.query_one("#diff-summary", Static)
        counts = {"added": 0, "removed": 0, "changed": 0}
        for i, change in enumerate(report.changes):
            counts[change.status] = counts.get(change.status, 0) + 1
            glyph = _STATUS_GLYPH.get(change.status, "?")
            style = _STATUS_STYLE.get(change.status, "")
            table.add_row(
                Text(f"{glyph} {change.status}", style=style),
                Text(change.page),
                Text(format_count(change.lines_added), justify="right"),
                Text(format_count(change.lines_removed), justify="right"),
                key=str(i),
            )
        summary.update(
            f"[b]{esc(report.domain)}[/b] · {esc(report.old_version)} → "
            f"{esc(report.new_version)} · "
            f"{counts['changed']} changed, {counts['added']} added, "
            f"{counts['removed']} removed · {report.unchanged_pages} unchanged"
        )
        empty = self.query_one("#diff-empty", EmptyState)
        panes = self.query_one("#diff-panes", Horizontal)
        if report.changes:
            table.remove_class("hidden")
            panes.remove_class("hidden")
            empty.add_class("hidden")
            self._show_excerpt(0)
        else:
            table.add_class("hidden")
            panes.add_class("hidden")
            empty.remove_class("hidden")
            empty.update("These snapshots are identical.")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        try:
            index = int(str(event.row_key.value))
        except (TypeError, ValueError):
            return
        self._show_excerpt(index)

    def _show_excerpt(self, index: int) -> None:
        if self._report is None or not (0 <= index < len(self._report.changes)):
            return
        change: PageChange = self._report.changes[index]
        old_text = change.old_excerpt or "— no prior content —"
        new_text = change.new_excerpt or "— removed —" if change.status != "added" else "— new page —"
        self.query_one("#old-excerpt", Static).update(esc(old_text))
        self.query_one("#new-excerpt", Static).update(esc(new_text))
