"""
Modern Dashboard — Polished GUI for GitBook Downloader.

Sidebar navigation, animated stats, download + split in one flow.
Designed to feel like a premium desktop app, not a script wrapper.
"""

import os
import sys
import queue
import threading
import time
from datetime import timedelta

import customtkinter as ctk
from tkinter import filedialog, messagebox

from .engine import download_docs
from .splitter import split_markdown

# ── Design System ─────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Refined color palette
C = {
    "bg":        "#0a0a0b",
    "sidebar":   "#0d0d0f",
    "surface":   "#111113",
    "card":      "#161618",
    "border":    "#1f1f22",
    "hover":     "#222226",
    "text":      "#fafafa",
    "text2":     "#c4c4cc",
    "muted":     "#6b6b76",
    "accent":    "#6366f1",   # Indigo
    "accent_h":  "#818cf8",
    "green":     "#22c55e",
    "red":       "#ef4444",
    "amber":     "#f59e0b",
}

FONT = {}

# ═══════════════════════════════════════════════════════════
class DownloadWorker(threading.Thread):
    """Runs the download engine in background, feeds progress to a queue."""

    def __init__(self, url, output, max_pages, workers, log_queue):
        super().__init__(daemon=True)
        self.url = url
        self.output = output
        self.max_pages = max_pages
        self.workers = workers
        self.log_queue = log_queue
        self._stop = threading.Event()

    def run(self):
        def cb(phase, current, total, message):
            if self._stop.is_set():
                raise SystemExit()
            self.log_queue.put({
                "phase": phase, "current": current, "total": total,
                "message": message,
            })

        try:
            pages, errors = download_docs(
                self.url, self.output,
                max_pages=self.max_pages,
                workers=self.workers,
                progress_callback=cb,
                quiet=True,
            )
            self.log_queue.put({
                "phase": "done", "pages": pages, "errors": len(errors),
                "output": self.output,
            })
        except SystemExit:
            self.log_queue.put({"phase": "cancelled"})
        except Exception as e:
            self.log_queue.put({"phase": "error", "message": str(e)})

    def stop(self):
        self._stop.set()


# ═══════════════════════════════════════════════════════════
class ModernDashboard(ctk.CTk):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()

        self._init_fonts()
        self.title("GitBook Downloader")
        self.geometry("1100x750")
        self.configure(fg_color=C["bg"])
        self.minsize(900, 600)

        # State
        self._worker = None
        self._poll_job = None
        self._log_queue = queue.Queue()
        self._active_view = "download"
        self._split_file = None

        self._build()
        self._show_download()

    # ── Fonts ─────────────────────────────────────────────
    def _init_fonts(self):
        FONT.update({
            "hero":    ctk.CTkFont(family="Inter", size=28, weight="bold"),
            "h1":      ctk.CTkFont(family="Inter", size=20, weight="bold"),
            "h2":      ctk.CTkFont(family="Inter", size=14, weight="bold"),
            "body":    ctk.CTkFont(family="Inter", size=13),
            "sm":      ctk.CTkFont(family="Inter", size=11),
            "xs":      ctk.CTkFont(family="Inter", size=10),
            "mono":    ctk.CTkFont(family="Cascadia Code", size=11),
            "stat_val": ctk.CTkFont(family="Inter", size=24, weight="bold"),
            "stat_lbl": ctk.CTkFont(family="Inter", size=10),
            "btn":     ctk.CTkFont(family="Inter", size=13, weight="bold"),
        })

    # ── Layout ────────────────────────────────────────────
    def _build(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=C["sidebar"], width=200,
                                     corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(24, 32))
        ctk.CTkLabel(logo_frame, text="⬡", font=ctk.CTkFont(size=28),
                     text_color=C["accent"]).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(logo_frame, text="GitBook\nDownloader",
                     font=FONT["sm"], text_color=C["text2"],
                     justify="left").pack(side="left")

        # Nav buttons
        self.nav_btns = {}
        for icon, label, key in [
            ("📥", "Download", "download"),
            ("✂️", "Splitter", "split"),
            ("⚙️", "Settings", "settings"),
        ]:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {label}",
                font=FONT["body"], anchor="w", height=40,
                fg_color="transparent", text_color=C["text2"],
                hover_color=C["hover"], corner_radius=8,
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_btns[key] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent",
                     height=20).pack(fill="x", expand=True)

        # Version
        ctk.CTkLabel(self.sidebar, text="v3.2.0", font=FONT["xs"],
                     text_color=C["muted"]).pack(side="bottom", pady=16)

        # Main content area
        self.main = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)

        # Build all views (hidden/shown via navigate)
        self._build_download_view()
        self._build_split_view()
        self._build_settings_view()

    # ── Navigation ────────────────────────────────────────
    def _navigate(self, key):
        self._active_view = key
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.configure(fg_color=C["accent"], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=C["text2"])

        for k, frame in self._views.items():
            frame.pack_forget()

        self._views[key].pack(fill="both", expand=True, padx=24, pady=24)

    # ═══════════════════════════════════════════════════════
    # DOWNLOAD VIEW
    # ═══════════════════════════════════════════════════════
    def _build_download_view(self):
        v = ctk.CTkFrame(self.main, fg_color="transparent")

        # Header
        ctk.CTkLabel(v, text="Download Documentation",
                     font=FONT["h1"], text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(v, text="Enter a GitBook URL to download the complete site",
                     font=FONT["body"], text_color=C["muted"]).pack(anchor="w", pady=(2, 20))

        # URL Card
        card = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card, text="Target URL", font=FONT["h2"],
                     text_color=C["text"]).pack(anchor="w", padx=20, pady=(16, 6))

        url_row = ctk.CTkFrame(card, fg_color="transparent")
        url_row.pack(fill="x", padx=20, pady=(0, 16))

        self.url_entry = ctk.CTkEntry(url_row,
            placeholder_text="https://docs.example.com/",
            font=FONT["body"], height=44,
            fg_color=C["surface"], border_color=C["border"],
            text_color=C["text"], corner_radius=8)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.url_entry.insert(0, "https://docs.openalgo.in/")

        self.btn_start = ctk.CTkButton(url_row, text="▶  Start",
            command=self._start_download,
            font=FONT["btn"], height=44, width=120,
            fg_color=C["accent"], hover_color=C["accent_h"],
            corner_radius=8, text_color="#ffffff")
        self.btn_start.pack(side="right")

        self.btn_cancel = ctk.CTkButton(url_row, text="■  Cancel",
            command=self._cancel_download,
            font=FONT["body"], height=44, width=100,
            fg_color=C["surface"], hover_color="#3a1818",
            corner_radius=8, text_color=C["text2"],
            border_width=1, border_color=C["border"],
            state="disabled")
        self.btn_cancel.pack(side="right", padx=(0, 8))

        # Options row
        opt_row = ctk.CTkFrame(v, fg_color="transparent")
        opt_row.pack(fill="x", pady=(0, 16))

        for label, key, default, width in [
            ("Output file", "output_name", "downloaded_docs.md", 200),
            ("Max pages", "max_pages", "500", 80),
            ("Workers", "workers", "5", 60),
        ]:
            grp = ctk.CTkFrame(opt_row, fg_color=C["card"], corner_radius=8,
                               border_width=1, border_color=C["border"])
            grp.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(grp, text=label, font=FONT["xs"],
                         text_color=C["muted"]).pack(anchor="w", padx=14, pady=(10, 0))
            entry = ctk.CTkEntry(grp, font=FONT["body"], height=34, width=width,
                                 fg_color=C["surface"], border_color=C["border"],
                                 text_color=C["text"], corner_radius=6)
            entry.insert(0, default)
            entry.pack(padx=14, pady=(2, 10))
            setattr(self, f"opt_{key}", entry)

        # Stats bar (hidden until download starts)
        self.stats_bar = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                                       border_width=1, border_color=C["border"])

        # Phase indicator
        self.phase_lbl = ctk.CTkLabel(v, text="", font=FONT["sm"],
                                       text_color=C["muted"])

        # Progress bar
        self.progress = ctk.CTkProgressBar(v, fg_color=C["surface"],
                                            progress_color=C["accent"],
                                            height=6, corner_radius=3)
        self.progress.set(0)
        self.progress_lbl = ctk.CTkLabel(v, text="", font=FONT["xs"],
                                          text_color=C["muted"])

        # Log
        log_card = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                                border_width=1, border_color=C["border"])
        log_card.pack(fill="both", expand=True)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(log_header, text="Activity", font=FONT["h2"],
                     text_color=C["text"]).pack(side="left")
        ctk.CTkButton(log_header, text="Clear", width=50, height=24,
                      font=FONT["xs"], fg_color=C["surface"],
                      hover_color=C["hover"], corner_radius=4,
                      text_color=C["muted"], border_width=1,
                      border_color=C["border"],
                      command=lambda: self.log_box.delete("1.0", "end")
                      ).pack(side="right")

        self.log_box = ctk.CTkTextbox(log_card, font=FONT["mono"],
                                       fg_color=C["surface"],
                                       border_width=0,
                                       text_color=C["text2"],
                                       corner_radius=6, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for tag, color in [
            ("success", C["green"]), ("error", C["red"]),
            ("info", C["muted"]), ("highlight", C["accent"]),
            ("phase", C["amber"]),
        ]:
            self.log_box.tag_config(tag, foreground=color)

        # Status bar
        status = ctk.CTkFrame(self, fg_color=C["sidebar"], height=28,
                              corner_radius=0)
        status.pack(side="bottom", fill="x")
        status.pack_propagate(False)
        self.status_lbl = ctk.CTkLabel(status, text="Ready",
                                        font=FONT["xs"], text_color=C["muted"])
        self.status_lbl.pack(side="left", padx=16, pady=4)

        self._views = {"download": v}

    # ── Download Logic ────────────────────────────────────
    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        out_name = self.opt_output_name.get().strip() or "downloaded_docs.md"
        try:
            max_pages = int(self.opt_max_pages.get())
        except ValueError:
            max_pages = 500
        try:
            workers = int(self.opt_workers.get())
            workers = max(1, min(workers, 10))
        except ValueError:
            workers = 5

        output = os.path.join(os.getcwd(), out_name)

        # Reset UI
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", f"Target: {url}\nOutput: {out_name}\nMax: {max_pages}  |  Workers: {workers}\n\n", "info")

        self._show_stats_bar()
        self._set_running(True)
        self.status_lbl.configure(text="Downloading…", text_color=C["amber"])
        self.progress.set(0)

        self._log_queue = queue.Queue()
        self._worker = DownloadWorker(url, output, max_pages, workers,
                                       self._log_queue)
        self._worker.start()
        self._poll()

    def _poll(self):
        """Poll the log queue and update UI."""
        try:
            while True:
                msg = self._log_queue.get_nowait()
                phase = msg.get("phase", "")

                if phase == "discovery":
                    self.phase_lbl.configure(
                        text=f"🔍 Discovering pages… ({msg['current']} found)")
                    self.progress.set(min(msg["current"] / max(msg["total"], 1), 0.3))

                elif phase == "discovery_done":
                    self.phase_lbl.configure(
                        text=f"✓ Found {msg['current']} pages — downloading…")
                    self._update_stats(discovered=msg['current'])

                elif phase == "download":
                    self.phase_lbl.configure(
                        text=f"📥 Downloading… ({msg['current']}/{msg['total']})")
                    pct = 0.3 + 0.7 * (msg["current"] / max(msg["total"], 1))
                    self.progress.set(min(pct, 1.0))
                    self._update_stats(downloaded=msg['current'])
                    self.log_box.insert("end", f"  ✓ {msg['message']}\n", "success")
                    self.log_box.see("end")

                elif phase == "done":
                    self.phase_lbl.configure(text="✅ Download complete!")
                    self.progress.set(1.0)
                    self._update_stats(downloaded=msg['pages'],
                                       discovered=msg['pages'])
                    self.status_lbl.configure(text="Done", text_color=C["green"])
                    self.log_box.insert("end",
                        f"\n{'─' * 40}\n✅ {msg['pages']} pages downloaded\n"
                        f"📄 Saved: {os.path.basename(msg['output'])}\n"
                        f"{'─' * 40}\n", "highlight")
                    self.log_box.see("end")
                    self._set_running(False)
                    self._worker = None
                    self._poll_job = None
                    return

                elif phase == "cancelled":
                    self.phase_lbl.configure(text="⏹ Cancelled")
                    self.status_lbl.configure(text="Cancelled", text_color=C["red"])
                    self._set_running(False)
                    self._worker = None
                    self._poll_job = None
                    return

                elif phase == "error":
                    self.log_box.insert("end", f"\n❌ {msg['message']}\n", "error")
                    self.phase_lbl.configure(text="❌ Error")
                    self.status_lbl.configure(text="Error", text_color=C["red"])
                    self._set_running(False)
                    self._worker = None
                    self._poll_job = None
                    return

        except queue.Empty:
            pass

        if self._worker and self._worker.is_alive():
            self._poll_job = self.after(150, self._poll)

    def _cancel_download(self):
        if self._worker:
            self._worker.stop()
            self.log_box.insert("end", "\n⏹ Cancelling…\n", "error")
            self.btn_cancel.configure(state="disabled")

    def _set_running(self, running):
        state_running = "disabled" if running else "normal"
        state_idle = "normal" if running else "disabled"
        self.btn_start.configure(state=state_running)
        self.btn_cancel.configure(state=state_idle)
        self.url_entry.configure(state=state_running)
        for attr in ("opt_output_name", "opt_max_pages", "opt_workers"):
            getattr(self, attr).configure(state=state_running)

    def _show_stats_bar(self):
        self.stats_bar.pack(fill="x", pady=(0, 12))
        self.phase_lbl.pack(anchor="w", pady=(0, 4))
        self.progress.pack(fill="x", pady=(0, 2))
        self.progress_lbl.pack(anchor="w", pady=(0, 4))

        # Stat cards inside the bar
        for w in self.stats_bar.winfo_children():
            w.destroy()

        grid = ctk.CTkFrame(self.stats_bar, fg_color="transparent")
        grid.pack(fill="x", padx=12, pady=10)

        self._stat_widgets = {}
        for i, (label, color) in enumerate([
            ("Discovered", C["amber"]),
            ("Downloaded", C["green"]),
            ("Errors", C["red"]),
            ("Elapsed", C["muted"]),
        ]):
            cell = ctk.CTkFrame(grid, fg_color=C["surface"], corner_radius=6)
            cell.pack(side="left", padx=3, expand=True, fill="x")
            ctk.CTkLabel(cell, text=label, font=FONT["stat_lbl"],
                         text_color=C["muted"]).pack(pady=(8, 0))
            val = ctk.CTkLabel(cell, text="—", font=FONT["stat_val"],
                               text_color=color)
            val.pack(pady=(0, 8))
            self._stat_widgets[label.lower()] = val

    def _update_stats(self, discovered=None, downloaded=None,
                      errors=None, elapsed=None):
        if not hasattr(self, '_stat_widgets'):
            return
        if discovered is not None:
            self._stat_widgets["discovered"].configure(text=str(discovered))
        if downloaded is not None:
            self._stat_widgets["downloaded"].configure(text=str(downloaded))
        if errors is not None:
            self._stat_widgets["errors"].configure(text=str(errors))
        if elapsed is not None:
            self._stat_widgets["elapsed"].configure(text=str(elapsed))

    # ═══════════════════════════════════════════════════════
    # SPLIT VIEW
    # ═══════════════════════════════════════════════════════
    def _build_split_view(self):
        v = ctk.CTkFrame(self.main, fg_color="transparent")

        ctk.CTkLabel(v, text="Split Markdown",
                     font=FONT["h1"], text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(v, text="Break a downloaded .md file into AI-friendly chunks",
                     font=FONT["body"], text_color=C["muted"]).pack(anchor="w", pady=(2, 20))

        # File selection
        file_card = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                                 border_width=1, border_color=C["border"])
        file_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(file_card, text="Markdown File", font=FONT["h2"],
                     text_color=C["text"]).pack(anchor="w", padx=20, pady=(16, 6))

        file_row = ctk.CTkFrame(file_card, fg_color="transparent")
        file_row.pack(fill="x", padx=20, pady=(0, 16))

        self.split_file_lbl = ctk.CTkLabel(file_row, text="No file selected",
            font=FONT["body"], text_color=C["muted"],
            fg_color=C["surface"], corner_radius=6,
            height=38, anchor="w")
        self.split_file_lbl.pack(side="left", fill="x", expand=True,
                                  padx=(0, 8), ipadx=12)

        ctk.CTkButton(file_row, text="Browse", command=self._split_browse,
                      font=FONT["body"], height=38, width=80,
                      fg_color=C["surface"], hover_color=C["hover"],
                      corner_radius=6, text_color=C["text2"],
                      border_width=1, border_color=C["border"]).pack(side="right")

        # Options
        opt_card = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                                border_width=1, border_color=C["border"])
        opt_card.pack(fill="x", pady=(0, 12))

        opt_inner = ctk.CTkFrame(opt_card, fg_color="transparent")
        opt_inner.pack(fill="x", padx=20, pady=16)

        for i, (label, attr, default, w) in enumerate([
            ("Chunk size (MB)", "split_size", "1.0", 80),
            ("Output folder", "split_out", "(auto)", 200),
        ]):
            ctk.CTkLabel(opt_inner, text=label, font=FONT["xs"],
                         text_color=C["muted"]).grid(row=0, column=i, sticky="w", padx=(0, 16))
            if attr == "split_out":
                out_row = ctk.CTkFrame(opt_inner, fg_color="transparent")
                out_row.grid(row=1, column=i, sticky="ew", pady=(2, 0))
                self.split_out_lbl = ctk.CTkLabel(out_row, text=default,
                    font=FONT["body"], text_color=C["muted"],
                    fg_color=C["surface"], corner_radius=6,
                    height=34, anchor="w")
                self.split_out_lbl.pack(side="left", fill="x", expand=True, ipadx=10)
                ctk.CTkButton(out_row, text="…", width=34, height=34,
                              command=self._split_outdir,
                              font=FONT["body"], fg_color=C["surface"],
                              hover_color=C["hover"], corner_radius=6,
                              text_color=C["text2"], border_width=1,
                              border_color=C["border"]).pack(side="right", padx=(4, 0))
            else:
                entry = ctk.CTkEntry(opt_inner, font=FONT["body"],
                                     height=34, width=w,
                                     fg_color=C["surface"],
                                     border_color=C["border"],
                                     text_color=C["text"], corner_radius=6)
                entry.insert(0, default)
                entry.grid(row=1, column=i, sticky="w", pady=(2, 0))
                setattr(self, f"opt_{attr}", entry)

        opt_inner.grid_columnconfigure(1, weight=1)

        # Split button
        ctk.CTkButton(v, text="✂  Split File", command=self._split_run,
                      font=FONT["btn"], height=40, width=160,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      corner_radius=8, text_color="#ffffff").pack(anchor="e", pady=(0, 12))

        # Results
        res_card = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                                border_width=1, border_color=C["border"])
        res_card.pack(fill="both", expand=True)

        ctk.CTkLabel(res_card, text="Results", font=FONT["h2"],
                     text_color=C["text"]).pack(anchor="w", padx=16, pady=(12, 4))

        self.split_result = ctk.CTkTextbox(res_card, font=FONT["mono"],
                                            fg_color=C["surface"],
                                            border_width=0,
                                            text_color=C["text2"],
                                            corner_radius=6, wrap="word")
        self.split_result.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for tag, c in [("success", C["green"]), ("error", C["red"]),
                        ("info", C["muted"])]:
            self.split_result.tag_config(tag, foreground=c)

        self._views["split"] = v

    def _split_browse(self):
        p = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")])
        if p:
            self._split_file = p
            self.split_file_lbl.configure(text=p, text_color=C["text"])

    def _split_outdir(self):
        p = filedialog.askdirectory(title="Select Output Folder")
        if p:
            self.split_out_lbl.configure(text=p, text_color=C["text"])

    def _split_run(self):
        if not self._split_file or not os.path.exists(self._split_file):
            messagebox.showerror("Error", "Select a valid .md file first")
            return
        try:
            size = float(self.opt_split_size.get())
        except ValueError:
            size = 1.0

        out_dir = self.split_out_lbl.cget("text")
        if out_dir == "(auto)":
            out_dir = os.path.join(os.path.dirname(self._split_file) or ".", "chunks")

        self.split_result.delete("1.0", "end")
        self.split_result.insert("end",
            f"Input:  {self._split_file}\nOutput: {out_dir}\nChunk:  {size} MB\n\n", "info")

        try:
            chunks = split_markdown(self._split_file, out_dir, size)
        except Exception as e:
            self.split_result.insert("end", f"✕ Error: {e}\n", "error")
            return

        total = 0
        for fn, sz in chunks:
            total += sz
            kb = sz / 1024
            s = f"{kb / 1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"
            self.split_result.insert("end",
                f"  ✓ {os.path.basename(fn):32s} {s:>10s}\n", "success")

        total_kb = total / 1024
        self.split_result.insert("end",
            f"\n{'─' * 40}\n{len(chunks)} chunks ({total_kb:.0f} KB total)\n{'─' * 40}\n",
            "success")
        self.status_lbl.configure(text=f"Split: {len(chunks)} chunks", text_color=C["green"])

    # ═══════════════════════════════════════════════════════
    # SETTINGS VIEW
    # ═══════════════════════════════════════════════════════
    def _build_settings_view(self):
        v = ctk.CTkFrame(self.main, fg_color="transparent")

        ctk.CTkLabel(v, text="Settings",
                     font=FONT["h1"], text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(v, text="Configure default options",
                     font=FONT["body"], text_color=C["muted"]).pack(anchor="w", pady=(2, 20))

        # About card
        card = ctk.CTkFrame(v, fg_color=C["card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(card, text="About", font=FONT["h2"],
                     text_color=C["text"]).pack(anchor="w", padx=20, pady=(16, 4))

        info = (
            "GitBook Downloader v3.2.0\n"
            "Download complete GitBook documentation sites as markdown.\n"
            "Split into AI-friendly chunks for LLM context windows.\n\n"
            "Built by Rohan Shetty • MIT License\n"
            "github.com/RohannShetty/gitbook-downloader"
        )
        ctk.CTkLabel(card, text=info, font=FONT["body"],
                     text_color=C["text2"], justify="left",
                     wraplength=600).pack(anchor="w", padx=20, pady=(0, 16))

        self._views["settings"] = v

    # ── Show initial view ─────────────────────────────────
    def _show_download(self):
        self._navigate("download")


def main():
    ModernDashboard().mainloop()


if __name__ == "__main__":
    main()
