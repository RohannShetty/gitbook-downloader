"""
GitBook Downloader v5.0 — Glass Dashboard

Modern glassmorphism-themed GUI. Dark frosted-glass panels,
purple accents, macOS-inspired blur aesthetics for customtkinter.
"""

import os
import sys
import json
import time
import queue
import threading
from datetime import datetime

# ── PyInstaller onefile fix: must run BEFORE any local imports ──
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    pkg_dir = os.path.join(sys._MEIPASS, 'gitbook_downloader')
    if os.path.isdir(pkg_dir) and pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)

import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    from .engine import stream_download, load_history, add_to_history
    from .splitter import split_markdown
except ImportError:
    from engine import stream_download, load_history, add_to_history
    from splitter import split_markdown

# ── Glass Design Tokens ────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

C = {
    "bg":           "#0d0d12",       # deep space
    "card_bg":      "#1a1a24",       # frosted glass base
    "card_border":  "#2a2a3a",       # subtle border
    "glass_light":  "#ffffff08",     # highlight
    "glass_dark":   "#00000030",     # shadow
    "accent":       "#7c3aed",       # vibrant purple
    "accent_hover": "#8b5cf6",       # lighter purple
    "accent_dim":   "#5b21b6",       # deep purple
    "text_primary": "#e8e8f0",       # white-ish
    "text_secondary":"#9090a8",       # muted
    "text_muted":   "#505068",       # very muted
    "green":        "#22c55e",       # success
    "green_bg":     "#22c55e15",
    "red":          "#ef4444",       # error
    "red_bg":       "#ef444415",
    "amber":        "#f59e0b",       # warning
    "amber_bg":     "#f59e0b15",
    "blue":         "#3b82f6",       # info
    "blue_bg":      "#3b82f615",
    "radius":       "16",            # px
}

FONT = {}
HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".gitbook-downloader")


# ═══════════════════════════════════════════════════════════
class DownloadPipeline(threading.Thread):
    """Runs stream_download in background, feeds events to queue."""

    def __init__(self, url, output, max_pages, workers, update_existing, event_queue):
        super().__init__(daemon=True)
        self.url = url
        self.output = output
        self.max_pages = max_pages
        self.workers = workers
        self.update_existing = update_existing
        self.event_queue = event_queue
        self._stop = threading.Event()

    def run(self):
        def cb(data):
            if self._stop.is_set():
                raise SystemExit()
            self.event_queue.put(data)
        try:
            stream_download(self.url, self.output,
                          max_pages=self.max_pages,
                          workers=self.workers,
                          update_existing=self.update_existing,
                          progress_callback=cb)
        except SystemExit:
            pass
        except Exception as e:
            self.event_queue.put({"phase": "error", "message": str(e)})

    def stop(self):
        self._stop.set()


# ═══════════════════════════════════════════════════════════
class GlassCard(ctk.CTkFrame):
    """Frosted glass card component."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", C["card_bg"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", C["card_border"])
        kwargs.setdefault("corner_radius", 16)
        super().__init__(master, **kwargs)


class GlassButton(ctk.CTkButton):
    """Glassmorphism accent button."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", C["accent"])
        kwargs.setdefault("hover_color", C["accent_hover"])
        kwargs.setdefault("text_color", "#ffffff")
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 0)
        kwargs.setdefault("font", ("Segoe UI", 13, "bold"))
        kwargs.setdefault("height", 40)
        super().__init__(master, **kwargs)


class StatCard(GlassCard):
    """Single stat card with label + value + optional icon."""

    def __init__(self, master, label, value="—", icon="", width=160, height=90):
        super().__init__(master, width=width, height=height)
        self.pack_propagate(False)

        self._icon = ctk.CTkLabel(self, text=icon, font=("Segoe UI", 22),
                                  text_color=C["text_muted"])
        self._icon.pack(anchor="nw", padx=14, pady=(12, 0))

        self._label = ctk.CTkLabel(self, text=label, font=("Segoe UI", 10),
                                   text_color=C["text_muted"])
        self._label.pack(anchor="sw", padx=14, pady=(0, 2))

        self._value = ctk.CTkLabel(self, text=value, font=("Segoe UI", 20, "bold"),
                                   text_color=C["text_primary"])
        self._value.pack(anchor="sw", padx=14, pady=(0, 10))

    def set_value(self, text, color=None):
        self._value.configure(text=str(text), text_color=color or C["text_primary"])


# ═══════════════════════════════════════════════════════════
class App(ctk.CTk):
    """Glassmorphism GitBook Downloader dashboard."""

    def __init__(self):
        super().__init__()
        self._init_fonts()
        self.title("GitBook Downloader v5.0")
        self.geometry("1060x720")
        self.configure(fg_color=C["bg"])
        self.minsize(860, 560)
        self._pipeline = None

        self._build_ui()
        self._show_dashboard()
        self._poll_events()

    def _init_fonts(self):
        try:
            ctk.FontManager.load_font("Segoe UI")
        except Exception:
            pass
        FONT["heading"] = ("Segoe UI", 24, "bold")
        FONT["sub"] = ("Segoe UI", 13)
        FONT["body"] = ("Segoe UI", 12)
        FONT["small"] = ("Segoe UI", 10)
        FONT["mono"] = ("Segoe UI", 11)

    # ── Layout ────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent", height=64)
        header.pack(fill="x", padx=32, pady=(24, 8))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="⬡ GitBook Downloader",
                     font=("Segoe UI", 22, "bold"),
                     text_color=C["text_primary"]).pack(side="left")

        self._version_label = ctk.CTkLabel(header, text="v5.0",
                                           font=("Segoe UI", 12),
                                           text_color=C["text_muted"])
        self._version_label.pack(side="left", padx=(8, 0))

        # ── Views container ──
        self._views = ctk.CTkFrame(self, fg_color="transparent")
        self._views.pack(fill="both", expand=True, padx=32, pady=(8, 24))

        # ── Footer ──
        footer = ctk.CTkFrame(self, fg_color="transparent", height=32)
        footer.pack(fill="x", side="bottom", padx=32, pady=(0, 12))
        ctk.CTkLabel(footer, text="Made with ⬡ for the docs community",
                     font=("Segoe UI", 10), text_color=C["text_muted"]).pack()

    # ── Dashboard view ─────────────────────────────────────

    def _clear_views(self):
        for w in self._views.winfo_children():
            w.destroy()

    def _show_dashboard(self):
        self._clear_views()
        container = ctk.CTkFrame(self._views, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # ── New download card ──
        new_card = GlassCard(container)
        new_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(new_card, text="New Download",
                     font=FONT["heading"], text_color=C["text_primary"]
                     ).pack(anchor="nw", padx=24, pady=(20, 4))
        ctk.CTkLabel(new_card, text="Paste a GitBook URL to download its documentation",
                     font=FONT["body"], text_color=C["text_secondary"]
                     ).pack(anchor="nw", padx=24, pady=(0, 16))

        row = ctk.CTkFrame(new_card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 20))

        self._url_entry = ctk.CTkEntry(row, placeholder_text="https://docs.example.com/",
                                        font=FONT["body"],
                                        fg_color=C["bg"], text_color=C["text_primary"],
                                        border_color=C["card_border"],
                                        corner_radius=12, height=44)
        self._url_entry.pack(side="left", fill="x", expand=True, ipadx=8)
        self._url_entry.bind("<Return>", lambda e: self._start_download())

        GlassButton(row, text="Start", width=120, command=self._start_download
                    ).pack(side="right", padx=(12, 0))

        # ── History ──
        history = load_history()
        if history.get("downloads"):
            ctk.CTkLabel(container, text="Download History",
                         font=FONT["heading"], text_color=C["text_primary"]
                         ).pack(anchor="nw", pady=(0, 12))
            for entry in history["downloads"]:
                self._build_history_card(container, entry)

        self._update_poll = True

    def _build_history_card(self, parent, entry):
        card = GlassCard(parent)
        card.pack(fill="x", pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=14)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        url = entry.get("url", "").rstrip("/").split("/")[-1] or entry["url"]
        ctk.CTkLabel(info, text=url, font=("Segoe UI", 14, "bold"),
                     text_color=C["text_primary"]).pack(anchor="w")
        detail = f"{entry.get('pages', 0)} pages · {entry.get('size_kb', 0)/1024:.1f} MB"
        if entry.get("new_pages"):
            detail += f" · {entry['new_pages']} new"
        detail += f" · {entry.get('date', '')}"
        ctk.CTkLabel(info, text=detail, font=("Segoe UI", 11),
                     text_color=C["text_secondary"]).pack(anchor="w")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="right")

        out = entry.get("output", "")
        GlassButton(actions, text="Open", width=72, height=32,
                    font=("Segoe UI", 11),
                    command=lambda p=out: self._open_file(p)
                    ).pack(side="left", padx=2)
        GlassButton(actions, text="Split", width=72, height=32,
                    font=("Segoe UI", 11),
                    command=lambda p=out: self._split_output(p)
                    ).pack(side="left", padx=2)
        GlassButton(actions, text="Update", width=80, height=32,
                    font=("Segoe UI", 11),
                    command=lambda e=entry: self._update_download(e)
                    ).pack(side="left", padx=2)

    # ── Download view ──────────────────────────────────────

    def _show_download(self, url):
        self._clear_views()
        container = ctk.CTkFrame(self._views, fg_color="transparent")
        container.pack(fill="both", expand=True)

        card = GlassCard(container)
        card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card, text="Downloading",
                     font=FONT["heading"], text_color=C["text_primary"]
                     ).pack(anchor="nw", padx=24, pady=(20, 4))
        url_label = ctk.CTkLabel(card, text=url, font=("Segoe UI", 12),
                                 text_color=C["text_secondary"], wraplength=600)
        url_label.pack(anchor="nw", padx=24, pady=(0, 16))

        # ── Stats row ──
        stats_row = ctk.CTkFrame(card, fg_color="transparent")
        stats_row.pack(fill="x", padx=24, pady=(0, 20))

        self._stat_discovered = StatCard(stats_row, "Discovered", "0", "🔍")
        self._stat_discovered.pack(side="left", padx=(0, 10))
        self._stat_downloaded = StatCard(stats_row, "Downloaded", "0", "✅",
                                         text_color=C["green"])
        self._stat_downloaded.pack(side="left", padx=10)
        self._stat_errors = StatCard(stats_row, "Errors", "0", "⚠️")
        self._stat_errors.pack(side="left", padx=10)
        self._stat_size = StatCard(stats_row, "Size", "—", "📄")
        self._stat_size.pack(side="left", padx=10)
        self._stat_elapsed = StatCard(stats_row, "Elapsed", "0s", "⏱")
        self._stat_elapsed.pack(side="left", padx=(10, 0))

        # ── Progress bar ──
        progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        progress_frame.pack(fill="x", padx=24, pady=(0, 16))

        self._progress_bar = ctk.CTkProgressBar(
            progress_frame, fg_color=C["card_border"],
            progress_color=C["accent"], corner_radius=8, height=6)
        self._progress_bar.pack(fill="x")
        self._progress_bar.set(0)

        self._status_label = ctk.CTkLabel(progress_frame, text="Starting...",
                                           font=("Segoe UI", 11),
                                           text_color=C["text_secondary"])
        self._status_label.pack(anchor="w", pady=(6, 0))

        # ── Log ──
        log_frame = GlassCard(container)
        log_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(log_frame, text="Activity Log",
                     font=("Segoe UI", 14, "bold"), text_color=C["text_primary"]
                     ).pack(anchor="nw", padx=20, pady=(14, 8))

        self._log_text = ctk.CTkTextbox(
            log_frame, fg_color="transparent", border_width=0,
            text_color=C["text_secondary"], font=("Consolas", 10),
            corner_radius=0)
        self._log_text.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        # ── Cancel button ──
        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(14, 0))
        self._cancel_btn = GlassButton(btn_row, text="Cancel", width=100,
                                       command=self._cancel_download)
        self._cancel_btn.pack(side="right")

        self._download_t0 = time.time()
        self._log("Starting download...")
        self._start_time = time.time()

    # ── Actions ────────────────────────────────────────────

    def _start_download(self):
        url = self._url_entry.get().strip()
        if not url:
            return
        self._url = url
        self._output = "downloaded_docs.md"

        self._show_download(url)
        self._pipeline = DownloadPipeline(
            url, self._output, max_pages=0, workers=5,
            update_existing=False, event_queue=self._event_queue)
        self._pipeline.start()

    def _update_download(self, entry):
        url = entry["url"]
        out = entry["output"]
        self._url = url
        self._output = out

        self._show_download(url + " (update)")
        self._log("Updating existing download...")
        self._pipeline = DownloadPipeline(
            url, out, max_pages=0, workers=5,
            update_existing=True, event_queue=self._event_queue)
        self._pipeline.start()

    def _cancel_download(self):
        if self._pipeline:
            self._pipeline.stop()
            self._pipeline = None
        self._log("Cancelled by user")
        self._cancel_btn.configure(state="disabled")
        self._enable_done_buttons()

    def _split_output(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Error", f"File not found:\n{path}")
            return
        try:
            chunks = split_markdown(path, path.replace(".md", "_chunks"))
            msg = f"Split into {len(chunks)} chunks"
            messagebox.showinfo("Done", msg)
            self._log(msg)
            os.startfile(os.path.dirname(chunks[0][0]) if chunks else "")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _open_file(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Not Found", f"File was moved:\n{path}")

    def _enable_done_buttons(self):
        btn_row = ctk.CTkFrame(self._views.winfo_children()[0] if
                               self._views.winfo_children() else self,
                               fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))

        GlassButton(btn_row, text="Dashboard", width=120,
                    command=self._show_dashboard).pack(side="left", padx=2)
        GlassButton(btn_row, text="Split", width=80,
                    command=lambda: self._split_output(self._output)
                    ).pack(side="left", padx=2)
        GlassButton(btn_row, text="Open File", width=100,
                    command=lambda: self._open_file(self._output)
                    ).pack(side="left", padx=2)

    # ── Logging ────────────────────────────────────────────

    def _log(self, msg, color=None):
        try:
            tag = "default"
            if color:
                self._log_text.tag_config(tag, foreground=color)
            self._log_text.insert("end", f"{msg}\n", tag)
            self._log_text.see("end")
        except Exception:
            pass

    # ── Event loop ─────────────────────────────────────────

    def _poll_events(self):
        self._event_queue = queue.Queue()
        self._poll_loop()

    def _poll_loop(self):
        try:
            while True:
                data = self._event_queue.get_nowait()
                self._handle_event(data)
        except queue.Empty:
            pass
        self.after(100, self._poll_loop)

    def _handle_event(self, data):
        phase = data.get("phase", "")
        disc = data.get("discovered", 0)
        dl = data.get("downloaded", 0)
        err = data.get("errors", 0)
        size_kb = data.get("size_kb", 0)
        elapsed = data.get("elapsed", 0)

        self._stat_discovered.set_value(disc)
        self._stat_downloaded.set_value(dl, C["green"] if dl > 0 else C["text_primary"])
        self._stat_errors.set_value(err, C["red"] if err > 0 else C["text_primary"])

        if size_kb:
            size_str = f"{size_kb/1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
            self._stat_size.set_value(size_str)

        if elapsed:
            self._stat_elapsed.set_value(f"{elapsed:.0f}s")

        url = data.get("url", "")
        title = data.get("title", "")

        if phase == "progress":
            self._status_label.configure(text=f"Downloading: {url[:60]}...")
            if disc > 0:
                self._progress_bar.set(dl / disc if disc else 0)

        elif phase == "downloaded":
            kb = data.get("size_kb", 0)
            self._log(f"  {url[:70]:70s}  {kb:.1f} KB  {title[:30]}",
                      C["green"])

        elif phase == "error":
            self._log(f"Error: {data.get('message', '')}", C["red"])

        elif phase == "done":
            t = time.time() - self._download_t0
            self._status_label.configure(
                text=f"Done — {dl} pages | {err} errors | {t:.0f}s",
                text_color=C["green"])
            self._progress_bar.set(1.0)
            self._log(f"Done. {dl} pages downloaded, {err} errors, {t:.0f}s",
                      C["green"])
            self._pipeline = None
            self._cancel_btn.configure(state="disabled")
            self._enable_done_buttons()
            # Auto-prompt to split
            if dl > 0:
                if messagebox.askyesno("Split?", "Split into AI-ready chunks?"):
                    self._split_output(self._output)


# ═══════════════════════════════════════════════════════════
def ModernDashboard():
    """Entry point for PyInstaller (returned by dashboard())."""
    return App()


if __name__ == "__main__":
    App().mainloop()
