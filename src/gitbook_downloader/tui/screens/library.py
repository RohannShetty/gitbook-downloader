"""Library surface — downloaded sources, sizes, snapshots, actions."""

from __future__ import annotations

from rich.text import Text

from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Static

from ..engine_protocol import LibraryEntry
from ..theme import format_count, format_size
from ..widgets import ConfirmModal, EmptyState, Kicker, esc


class LibrarySurface(VerticalScroll):
    DEFAULT_CSS = """
    LibrarySurface {
        padding: 1 2;
    }
    #domains-table {
        height: 1fr;
        min-height: 8;
        margin-bottom: 1;
    }
    #library-detail {
        height: auto;
        color: $ink-muted;
        padding: 1 0;
    }
    #library-actions {
        height: auto;
        margin-bottom: 1;
    }
    #library-actions Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("r", "recrawl", "Re-crawl"),
        ("o", "open_folder", "Open folder"),
        ("d", "delete", "Delete"),
        ("f5", "refresh", "Refresh"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._entries: list[LibraryEntry] = []
        self._selected: LibraryEntry | None = None

    def compose(self):
        yield Kicker("Library")
        yield EmptyState(
            "No sources yet",
            "Press 1 and paste a documentation URL to capture your first source.",
            id="library-empty",
            classes="hidden",
        )
        yield DataTable(id="domains-table", cursor_type="row", zebra_stripes=True)
        yield Static("", id="library-detail", markup=True)
        with Horizontal(id="library-actions"):
            yield Button("Re-crawl", variant="primary", id="recrawl-btn")
            yield Button("Open folder", id="open-folder-btn")
            yield Button("Delete", variant="error", id="delete-btn")
            yield Button("Refresh", id="refresh-btn")

    def on_mount(self) -> None:
        table = self.query_one("#domains-table", DataTable)
        table.add_columns(
            "DOMAIN",
            "PROVIDER",
            "PAGES",
            "SIZE",
            "LAST CRAWL",
        )
        self.reload()

    def reload(self) -> None:
        table = self.query_one("#domains-table", DataTable)
        table.clear()
        try:
            self._entries = list(self.app.engine.list_library())
        except Exception as exc:  # noqa: BLE001
            self.app.notify(f"Could not read the Library: {exc}", severity="error")
            self._entries = []
        for entry in self._entries:
            table.add_row(
                Text(entry.domain, style="bold"),
                entry.provider,
                Text(format_count(entry.pages), justify="right"),
                Text(format_size(entry.size_bytes), justify="right"),
                Text(entry.last_crawled[:10], style="dim"),
                key=entry.domain,
            )
        empty = self.query_one("#library-empty", EmptyState)
        detail = self.query_one("#library-detail", Static)
        actions = self.query_one("#library-actions", Horizontal)
        if not self._entries:
            table.add_class("hidden")
            actions.add_class("hidden")
            detail.update("")
            empty.remove_class("hidden")
        else:
            table.remove_class("hidden")
            actions.remove_class("hidden")
            empty.add_class("hidden")
            if self._selected is None or not any(
                e.domain == self._selected.domain for e in self._entries
            ):
                self._selected = self._entries[0]
            self._render_detail()

    def _render_detail(self) -> None:
        entry = self._selected
        detail = self.query_one("#library-detail", Static)
        if entry is None:
            detail.update("")
            return
        detail.update(
            f"[b]{esc(entry.title)}[/b]  [dim]{esc(entry.url)}[/dim]\n"
            f"{entry.snapshot_count} snapshots · {format_size(entry.size_bytes)} · "
            f"last crawl {entry.last_crawled[:10]}"
        )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        domain = str(event.row_key.value or "")
        for entry in self._entries:
            if entry.domain == domain:
                self._selected = entry
                break
        self._render_detail()

    def _current_entry(self) -> LibraryEntry | None:
        if self._selected is not None:
            return self._selected
        table = self.query_one("#domains-table", DataTable)
        keys = [str(k.value) for k in table.rows]
        if not keys:
            return None
        domain = keys[table.cursor_row] if table.cursor_row < len(keys) else keys[0]
        for entry in self._entries:
            if entry.domain == domain:
                return entry
        return None

    # ── actions ──────────────────────────────────────────────────────

    def action_refresh(self) -> None:
        self.reload()

    def action_recrawl(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        wizard = self.app.surface("wizard")
        wizard.prefill(entry.url)
        self.app.show_surface("wizard")

    def action_open_folder(self) -> None:
        entry = self._current_entry()
        if entry is None or entry.local_path is None:
            self.app.notify("No folder recorded for this source.", severity="warning")
            return
        self.app.opener(entry.local_path)

    def action_delete(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return

        def check_delete(confirmed: bool | None) -> None:
            if not confirmed:
                return
            try:
                removed = self.app.engine.delete_domain(entry.domain)
            except Exception as exc:  # noqa: BLE001
                self.app.notify(f"Delete failed: {exc}", severity="error")
                return
            if removed:
                self._selected = None
                self.reload()
                self.app.notify(f"Deleted {entry.domain} from the Library.")

        self.app.push_screen(
            ConfirmModal(
                "Delete source?",
                f"[b]{esc(entry.domain)}[/b] and its {entry.snapshot_count} "
                "snapshots will be removed from the Library.\n"
                "[dim]This cannot be undone.[/dim]",
            ),
            check_delete,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "recrawl-btn":
            self.action_recrawl()
        elif event.button.id == "open-folder-btn":
            self.action_open_folder()
        elif event.button.id == "delete-btn":
            self.action_delete()
        elif event.button.id == "refresh-btn":
            self.action_refresh()
