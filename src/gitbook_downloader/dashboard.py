"""
GitBook Downloader v5.0 — Glassmorphism Dashboard

Dark frosted-glass UI inspired by Linear's dark-mode native design and
Stripe's purple accent system. Uses customtkinter with semi-transparent
panels, layered depth, and non-blocking in-app notifications.
"""

import os
import sys
import json
import time
import queue
import threading
from datetime import datetime
from tkinter import filedialog

# ── PyInstaller onefile fix ──
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    pkg_dir = os.path.join(sys._MEIPASS, 'gitbook_downloader')
    if os.path.isdir(pkg_dir) and pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)

import customtkinter as ctk

try:
    from .engine import stream_download, load_history, add_to_history
    from .splitter import split_markdown
except ImportError:
    from engine import stream_download, load_history, add_to_history
    from splitter import split_markdown


# ═══════════════════════════════════════════════════════════
# GLASS DESIGN TOKENS
# ═══════════════════════════════════════════════════════════

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Glass:
    """Design token namespace — inspired by Linear + Stripe."""
    # Backgrounds — near-black canvas with blue-cast
    BG = "#07070d"           # deepest void
    BG_SOFT = "#0c0c14"      # card/panel background
    BG_ELEVATED = "#12121e"  # elevated surface
    BG_HOVER = "#1a1a2a"     # hover state

    # Glass frosted surfaces (semi-transparent)
    GLASS = "#14141e"        # frosted card base
    GLASS_BORDER = "#1e1e32" # frosted edge
    GLASS_GLOW = "#2a2a4e"   # glow around active elements

    # Accent — deep indigo-violet
    ACCENT = "#6c47ff"       # primary interactive
    ACCENT_HOVER = "#7f5cff" # hover
    ACCENT_DIM = "#4a30b3"   # pressed/active
    ACCENT_GLOW = "#2a2055"  # glow behind accent elements

    # Brand gradients
    GRADIENT_START = "#6c47ff"
    GRADIENT_END = "#9b6dff"

    # Text — silvery white scale
    TEXT_PRIMARY = "#e8e8f2"
    TEXT_SECONDARY = "#9494ac"
    TEXT_MUTED = "#5c5c74"
    TEXT_DIM = "#3c3c54"

    # Status
    SUCCESS = "#22c55e"
    SUCCESS_BG = "#062b12"
    ERROR = "#ef4444"
    ERROR_BG = "#2b0a0a"
    WARNING = "#f59e0b"
    INFO = "#3b82f6"

    # Layout
    RADIUS = 12              # card radius
    RADIUS_BTN = 8           # button radius
    RADIUS_INPUT = 8         # input radius
    PADDING = 20

    # Font system
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"


# ═══════════════════════════════════════════════════════════
# CUSTOM GLASS WIDGETS
# ═══════════════════════════════════════════════════════════

class GlassCard(ctk.CTkFrame):
    """Frosted glass card with layered depth."""

    def __init__(self, master, hover_glow=False, **kwargs):
        kwargs.setdefault("fg_color", Glass.GLASS)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", Glass.GLASS_BORDER)
        kwargs.setdefault("corner_radius", Glass.RADIUS)
        super().__init__(master, **kwargs)

        # Inner glow line
        self._glow = ctk.CTkFrame(self, height=1, fg_color=Glass.GLASS_GLOW,
                                   corner_radius=0)
        self._glow.place(relx=0, rely=0, relwidth=1)


class GlassButton(ctk.CTkButton):
    """Gradient glass button."""

    def __init__(self, master, variant="primary", **kwargs):
        cfg = {
            "primary": {
                "fg_color": Glass.ACCENT,
                "hover_color": Glass.ACCENT_HOVER,
                "text_color": "#ffffff",
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": Glass.BG_HOVER,
                "text_color": Glass.TEXT_SECONDARY,
                "border_width": 1,
                "border_color": Glass.GLASS_BORDER,
            },
            "success": {
                "fg_color": Glass.SUCCESS,
                "hover_color": "#16a34a",
                "text_color": "#ffffff",
            },
        }
        c = cfg.get(variant, cfg["primary"])
        c.setdefault("corner_radius", Glass.RADIUS_BTN)
        c.setdefault("font", (Glass.FONT_FAMILY, 12, "bold"))
        c.setdefault("height", 36)
        c.update(kwargs)
        super().__init__(master, **c)


class StatTile(GlassCard):
    """Compact stat tile with label + animated value."""

    def __init__(self, master, label, icon="", width=140, height=80):
        super().__init__(master, width=width, height=height)
        self.pack_propagate(False)

        ctk.CTkLabel(self, text=icon, font=(Glass.FONT_FAMILY, 16),
                     text_color=Glass.TEXT_DIM).pack(anchor="w", padx=12, pady=(10, 0))

        ctk.CTkLabel(self, text=label, font=(Glass.FONT_FAMILY, 9),
                     text_color=Glass.TEXT_MUTED).pack(anchor="w", padx=12, pady=(0, 1))

        self._val = ctk.CTkLabel(self, text="—", font=(Glass.FONT_FAMILY, 18, "bold"),
                                 text_color=Glass.TEXT_PRIMARY)
        self._val.pack(anchor="w", padx=12, pady=(0, 8))

    def set(self, text, color=None):
        self._val.configure(text=str(text), text_color=color or Glass.TEXT_PRIMARY)


class Toast(ctk.CTkFrame):
    """Non-blocking in-app notification bar."""

    def __init__(self, master, message, variant="info", duration=3000):
        color_map = {
            "info": (Glass.INFO, Glass.INFO, Glass.BG_SOFT),
            "success": (Glass.SUCCESS, Glass.SUCCESS, Glass.SUCCESS_BG),
            "error": (Glass.ERROR, Glass.ERROR, Glass.ERROR_BG),
            "warning": (Glass.WARNING, Glass.WARNING, Glass.BG_SOFT),
        }
        accent, border, bg = color_map.get(variant, color_map["info"])

        super().__init__(master, fg_color=bg, border_width=1,
                         border_color=border, corner_radius=8, height=40)
        self.pack_propagate(False)

        ctk.CTkLabel(self, text=message, font=(Glass.FONT_FAMILY, 11),
                     text_color=Glass.TEXT_PRIMARY).pack(side="left", padx=16)

        # Auto-dismiss
        self.after(duration, self._fade_out)

    def _fade_out(self):
        try:
            self.destroy()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# DOWNLOAD ENGINE THREAD
# ═══════════════════════════════════════════════════════════

class DownloadPipeline(threading.Thread):
    """Non-blocking download runner — feeds events to queue."""

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
# MAIN APP
# ═══════════════════════════════════════════════════════════

class App(ctk.CTk):
    """Glassmorphism GitBook Downloader — no blocking dialogs."""

    def __init__(self):
        super().__init__()
        self.title("GitBook Downloader v5.0")
        self.geometry("1060x720")
        self.configure(fg_color=Glass.BG)
        self.minsize(860, 560)
        self._pipeline = None
        self._event_queue = queue.Queue()
        self._toast_y = 0

        self._build_ui()
        self._show_dashboard()
        self._start_poll()

    # ── LAYOUT ─────────────────────────────────────────────

    def _build_ui(self):
        # Header bar
        header = ctk.CTkFrame(self, fg_color=Glass.BG_SOFT, height=56,
                              corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo area
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", padx=24)

        ctk.CTkLabel(logo_frame, text="⬡", font=(Glass.FONT_FAMILY, 24),
                     text_color=Glass.ACCENT).pack(side="left")
        ctk.CTkLabel(logo_frame, text="GitBook Downloader",
                     font=(Glass.FONT_FAMILY, 16, "bold"),
                     text_color=Glass.TEXT_PRIMARY).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(logo_frame, text="v5.0",
                     font=(Glass.FONT_FAMILY, 10), text_color=Glass.TEXT_DIM
                     ).pack(side="left", padx=(6, 0))

        # Views container
        self._views = ctk.CTkFrame(self, fg_color="transparent")
        self._views.pack(fill="both", expand=True, padx=24, pady=(12, 12))

        # Toast container (overlays at bottom)
        self._toast_frame = ctk.CTkFrame(self._views, fg_color="transparent",
                                          height=0)
        self._toast_frame.pack(fill="x", side="bottom", pady=(0, 8))

        # Footer
        footer = ctk.CTkFrame(self, fg_color=Glass.BG_SOFT, height=28,
                              corner_radius=0)
        footer.pack(fill="x", side="bottom")
        ctk.CTkLabel(footer, text="⬡ Built for the docs community",
                     font=(Glass.FONT_FAMILY, 9), text_color=Glass.TEXT_DIM
                     ).pack(pady=4)

    def _toast(self, message, variant="info", duration=3000):
        """Show non-blocking notification — never freezes."""
        t = Toast(self._toast_frame, message, variant, duration)
        t.pack(fill="x", pady=(0, 4))

    # ── VIEWS ──────────────────────────────────────────────

    def _clear(self):
        for w in self._views.winfo_children():
            if w != self._toast_frame:
                w.destroy()

    def _show_dashboard(self):
        self._clear()
        c = ctk.CTkFrame(self._views, fg_color="transparent")
        c.pack(fill="both", expand=True)

        # ── New download ──
        card = GlassCard(c)
        card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card, text="New Download",
                     font=(Glass.FONT_FAMILY, 20, "bold"),
                     text_color=Glass.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(card, text="Paste a GitBook URL and press Enter or click Start",
                     font=(Glass.FONT_FAMILY, 11),
                     text_color=Glass.TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(0, 14))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))

        self._url_entry = ctk.CTkEntry(
            row, placeholder_text="https://docs.example.com/",
            font=(Glass.FONT_FAMILY, 13),
            fg_color=Glass.BG, text_color=Glass.TEXT_PRIMARY,
            border_color=Glass.GLASS_BORDER, corner_radius=Glass.RADIUS_INPUT,
            height=42)
        self._url_entry.pack(side="left", fill="x", expand=True)
        self._url_entry.bind("<Return>", lambda e: self._start_download())

        GlassButton(row, "primary", text="Start", width=120,
                    command=self._start_download).pack(side="right", padx=(12, 0))

        # ── History ──
        history = load_history()
        if history.get("downloads"):
            ctk.CTkLabel(c, text="Download History",
                         font=(Glass.FONT_FAMILY, 16, "bold"),
                         text_color=Glass.TEXT_PRIMARY
                         ).pack(anchor="w", pady=(0, 10))
            for entry in history["downloads"][:8]:
                self._build_history_card(c, entry)

    def _build_history_card(self, parent, entry):
        card = GlassCard(parent, hover_glow=True)
        card.pack(fill="x", pady=(0, 8))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        name = entry.get("url", "").rstrip("/").split("/")[-1] or "Home"
        ctk.CTkLabel(info, text=name, font=(Glass.FONT_FAMILY, 13, "bold"),
                     text_color=Glass.TEXT_PRIMARY).pack(anchor="w")
        detail = "{} pages | {:.1f} MB | {}".format(
            entry.get("pages", 0),
            entry.get("size_kb", 0) / 1024,
            entry.get("date", ""))
        ctk.CTkLabel(info, text=detail, font=(Glass.FONT_FAMILY, 10),
                     text_color=Glass.TEXT_MUTED).pack(anchor="w")

        acts = ctk.CTkFrame(row, fg_color="transparent")
        acts.pack(side="right")

        out = entry.get("output", "")
        GlassButton(acts, "ghost", text="Open", width=64, height=28,
                    font=(Glass.FONT_FAMILY, 10),
                    command=lambda p=out: self._open_file(p)
                    ).pack(side="left", padx=2)
        GlassButton(acts, "ghost", text="Split", width=64, height=28,
                    font=(Glass.FONT_FAMILY, 10),
                    command=lambda p=out: self._split_output(p)
                    ).pack(side="left", padx=2)
        GlassButton(acts, "ghost", text="Update", width=72, height=28,
                    font=(Glass.FONT_FAMILY, 10),
                    command=lambda e=entry: self._update_download(e)
                    ).pack(side="left", padx=2)

    # ── Download view ──

    def _show_download(self, url):
        self._clear()
        c = ctk.CTkFrame(self._views, fg_color="transparent")
        c.pack(fill="both", expand=True)

        card = GlassCard(c)
        card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card, text="Downloading",
                     font=(Glass.FONT_FAMILY, 20, "bold"),
                     text_color=Glass.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(card, text=url, font=(Glass.FONT_FAMILY, 11),
                     text_color=Glass.TEXT_SECONDARY, wraplength=600
                     ).pack(anchor="w", padx=20, pady=(0, 14))

        # Stats row
        sr = ctk.CTkFrame(card, fg_color="transparent")
        sr.pack(fill="x", padx=20, pady=(0, 14))

        self._s_discovered = StatTile(sr, "Discovered", "\u25c9")
        self._s_discovered.pack(side="left", padx=(0, 6))
        self._s_downloaded = StatTile(sr, "Downloaded", "\u2713")
        self._s_downloaded.pack(side="left", padx=6)
        self._s_errors = StatTile(sr, "Errors", "\u26a0")
        self._s_errors.pack(side="left", padx=6)
        self._s_size = StatTile(sr, "Size", "\u25a0")
        self._s_size.pack(side="left", padx=6)
        self._s_elapsed = StatTile(sr, "Elapsed", "\u25b6")
        self._s_elapsed.pack(side="left", padx=6)

        # Progress bar with label
        pf = ctk.CTkFrame(card, fg_color="transparent")
        pf.pack(fill="x", padx=20, pady=(0, 4))
        self._progress = ctk.CTkProgressBar(pf, fg_color=Glass.GLASS_BORDER,
                                             progress_color=Glass.ACCENT,
                                             corner_radius=4, height=4)
        self._progress.pack(fill="x")
        self._progress.set(0)

        self._status = ctk.CTkLabel(pf, text="Initializing...",
                                    font=(Glass.FONT_FAMILY, 10),
                                    text_color=Glass.TEXT_MUTED)
        self._status.pack(anchor="w", pady=(4, 0))

        # Log
        log_card = GlassCard(c)
        log_card.pack(fill="both", expand=True)

        ctk.CTkLabel(log_card, text="Activity Log",
                     font=(Glass.FONT_FAMILY, 13, "bold"),
                     text_color=Glass.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(10, 6))

        self._log_box = ctk.CTkTextbox(log_card, fg_color="transparent",
                                        border_width=0,
                                        text_color=Glass.TEXT_SECONDARY,
                                        font=(Glass.FONT_MONO, 10),
                                        corner_radius=0)
        self._log_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Action row
        ar = ctk.CTkFrame(c, fg_color="transparent")
        ar.pack(fill="x", pady=(10, 0))
        self._btn_cancel = GlassButton(ar, "ghost", text="Cancel", width=100,
                                       command=self._cancel_download)
        self._btn_cancel.pack(side="right")

        self._download_t0 = time.time()
        self._log("Download started")

    # ── ACTIONS ────────────────────────────────────────────

    def _start_download(self):
        url = self._url_entry.get().strip()
        if not url:
            self._toast("Enter a URL first", "warning")
            return
        self._url = url
        self._output = "downloaded_docs.md"
        self._show_download(url)
        self._pipeline = DownloadPipeline(
            url, self._output, max_pages=0, workers=5,
            update_existing=False, event_queue=self._event_queue)
        self._pipeline.start()

    def _update_download(self, entry):
        self._url = entry["url"]
        self._output = entry["output"]
        self._show_download(entry["url"] + " (update)")
        self._log("Updating existing download...")
        self._pipeline = DownloadPipeline(
            entry["url"], entry["output"], max_pages=0, workers=5,
            update_existing=True, event_queue=self._event_queue)
        self._pipeline.start()

    def _cancel_download(self):
        if self._pipeline:
            self._pipeline.stop()
            self._pipeline = None
        self._log("Cancelled")
        self._btn_cancel.configure(state="disabled")
        self._show_done_buttons()

    def _split_output(self, path):
        if not os.path.exists(path):
            self._toast("File not found: " + os.path.basename(path), "error")
            return
        try:
            base = path.replace(".md", "_chunks")
            chunks = split_markdown(path, base)
            self._toast("Split into {} chunks".format(len(chunks)), "success")
            self._log("Split into {} chunks in {}".format(len(chunks), base))
        except Exception as e:
            self._toast("Split failed: " + str(e), "error")

    def _open_file(self, path):
        if os.path.exists(path):
            # Use after() to avoid blocking
            self.after(10, lambda: os.startfile(path))
        else:
            self._toast("File was moved or deleted", "warning")

    def _show_done_buttons(self, dl_count=0):
        ar = ctk.CTkFrame(self._views.winfo_children()[0] if
                          self._views.winfo_children() else self,
                          fg_color="transparent")
        ar.pack(fill="x", pady=(8, 0))

        GlassButton(ar, "ghost", text="Dashboard", width=100,
                    command=self._show_dashboard).pack(side="left", padx=2)
        if self._output and os.path.exists(self._output):
            GlassButton(ar, "ghost", text="Split", width=80,
                        command=lambda: self._split_output(self._output)
                        ).pack(side="left", padx=2)
            GlassButton(ar, "ghost", text="Open", width=80,
                        command=lambda: self._open_file(self._output)
                        ).pack(side="left", padx=2)

    def _log(self, msg, color=None):
        try:
            tag = "default"
            if color:
                self._log_box.tag_config(tag, foreground=color)
            self._log_box.insert("end", msg + "\n", tag)
            self._log_box.see("end")
        except Exception:
            pass

    # ── NON-BLOCKING EVENT POLL ───────────────────────────

    def _start_poll(self):
        """Begin polling the event queue — runs every 80ms."""
        self._poll_running = True
        self._poll_tick()

    def _poll_tick(self):
        if not self._poll_running:
            return
        try:
            while True:
                data = self._event_queue.get_nowait()
                self._handle(data)
        except queue.Empty:
            pass
        self.after(80, self._poll_tick)

    def _handle(self, data):
        phase = data.get("phase", "")
        disc = data.get("discovered", 0)
        dl = data.get("downloaded", 0)
        err = data.get("errors", 0)
        size_kb = data.get("size_kb", 0)
        elapsed = data.get("elapsed", 0)

        # Update stats
        self._s_discovered.set(disc)
        self._s_downloaded.set(dl, Glass.SUCCESS if dl > 0 else Glass.TEXT_PRIMARY)
        self._s_errors.set(err, Glass.ERROR if err > 0 else Glass.TEXT_PRIMARY)
        if size_kb:
            s = "{:.1f} MB".format(size_kb / 1024) if size_kb > 1024 else "{:.0f} KB".format(size_kb)
            self._s_size.set(s)
        if elapsed:
            self._s_elapsed.set("{:.0f}s".format(elapsed))

        if phase == "progress":
            url = data.get("url", "")[:50]
            self._status.configure(text=url)
            if disc > 0:
                self._progress.set(dl / disc if disc else 0)

        elif phase == "downloaded":
            self._log("  {}  {:.1f} KB".format(
                data.get("url", "")[:60], data.get("size_kb", 0)))

        elif phase == "error":
            msg = data.get("message", "")
            self._log("ERROR: " + msg, Glass.ERROR)
            self._toast(msg[:60], "error")

        elif phase == "done":
            t = time.time() - self._download_t0
            self._status.configure(
                text="Done — {} pages | {} errors | {:.0f}s".format(dl, err, t),
                text_color=Glass.SUCCESS)
            self._progress.set(1.0)
            self._log("Done. {} pages, {} errors, {:.0f}s".format(dl, err, t), Glass.SUCCESS)
            self._pipeline = None
            self._btn_cancel.configure(state="disabled", text="Done")
            self._show_done_buttons(dl)

            # Non-blocking split prompt via toast with a callback button
            if dl > 0 and self._output and os.path.exists(self._output):
                self._toast("Download complete! {} pages, {:.1f} MB".format(
                    dl, size_kb / 1024 if size_kb else 0), "success", 5000)
                # Show inline Split button
                self.after(200, lambda: self._show_split_prompt())

    def _show_split_prompt(self):
        """Show a non-blocking split button after download completes."""
        for w in self._views.winfo_children():
            if isinstance(w, ctk.CTkFrame) and w != self._toast_frame:
                # Add split prompt below the action row
                prompt = GlassCard(w, fg_color=Glass.SUCCESS_BG,
                                   border_color=Glass.SUCCESS)
                prompt.pack(fill="x", pady=(8, 0))

                ctk.CTkLabel(prompt, text="Split into AI-ready chunks?",
                            font=(Glass.FONT_FAMILY, 12),
                            text_color=Glass.TEXT_PRIMARY
                            ).pack(side="left", padx=16, pady=10)

                GlassButton(prompt, "success", text="Split Now",
                           command=lambda p=self._output: self._split_output(p)
                           ).pack(side="right", padx=(4, 16), pady=8)

                GlassButton(prompt, "ghost", text="Dismiss",
                           command=lambda f=prompt: f.destroy()
                           ).pack(side="right", padx=4, pady=8)
                break


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

def ModernDashboard():
    """Factory function for PyInstaller entry."""
    return App()


if __name__ == "__main__":
    app = App()
    app.mainloop()
