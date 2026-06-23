"""
Stripe-themed Dashboard — GitBook Downloader v4.0

Design system based on Stripe's visual language:
- Clean white surface, deep navy headings (#061b31)
- Purple accent (#533afd), weight-300 typography
- Blue-tinted shadows, 4px border radius
- Dashboard: download history, one-click updates, auto-split
"""

import os
import sys
import json
import time
import queue
import threading
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    from .engine import stream_download, load_history, add_to_history
    from .splitter import split_markdown
except ImportError:
    from engine import stream_download, load_history, add_to_history
    from splitter import split_markdown

# ── Stripe Design Tokens ───────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

C = {
    "white":     "#ffffff",
    "navy":      "#061b31",
    "slate":     "#64748d",
    "dark_slate":"#273951",
    "purple":    "#533afd",
    "purple_h":  "#4434d4",
    "purple_lt": "#b9b9f9",
    "border":    "#e5edf5",
    "bg":        "#f8f9fb",
    "card_bg":   "#ffffff",
    "green":     "#15be53",
    "green_tx":  "#108c3d",
    "red":       "#df1b41",
    "amber":     "#9b6829",
    "shadow":    "rgba(50,50,93,0.25)",
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
class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self._init_fonts()
        self.title("GitBook Downloader")
        self.geometry("1060x720")
        self.configure(fg_color=C["bg"])
        self.minsize(860, 560)

        self._pipeline = None
        self._poll_job = None
        self._events = queue.Queue()
        self._history = load_history()

        self._build()

    def _init_fonts(self):
        base = ctk.CTkFont
        FONT.update({
            "hero":   base(family="Segoe UI", size=26, weight="bold"),
            "h1":     base(family="Segoe UI", size=18, weight="bold"),
            "h2":     base(family="Segoe UI", size=14, weight="bold"),
            "body":   base(family="Segoe UI", size=13),
            "sm":     base(family="Segoe UI", size=11),
            "xs":     base(family="Segoe UI", size=10),
            "mono":   base(family="Consolas", size=11),
            "stat":   base(family="Segoe UI", size=28, weight="bold"),
            "btn":    base(family="Segoe UI", size=13, weight="bold"),
            "navy_h1":base(family="Segoe UI", size=14, weight="bold"),
        })

    # ── Layout ────────────────────────────────────────────
    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=C["white"], height=52,
                              corner_radius=0, border_width=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="⬡", font=ctk.CTkFont(size=22),
                     text_color=C["purple"], width=36).pack(side="left", padx=(20, 4), pady=10)
        ctk.CTkLabel(header, text="GitBook Downloader",
                     font=FONT["h2"], text_color=C["navy"]).pack(side="left", pady=10)
        ctk.CTkLabel(header, text="v4.0",
                     font=FONT["xs"], text_color=C["slate"],
                     fg_color=C["border"], corner_radius=3,
                     width=32, height=18).pack(side="left", padx=10, pady=14)

        self.header_actions = ctk.CTkFrame(header, fg_color="transparent")
        self.header_actions.pack(side="right", padx=16, pady=10)

        self.btn_new_dl = ctk.CTkButton(self.header_actions, text="+ New Download",
            command=self._show_new_download, font=FONT["btn"], height=32,
            fg_color=C["purple"], hover_color=C["purple_h"],
            corner_radius=4, text_color=C["white"])
        self.btn_new_dl.pack(side="right", padx=(8, 0))

        # Main content
        self.content = ctk.CTkFrame(self, fg_color=C["bg"])
        self.content.pack(fill="both", expand=True)

        # Status bar
        status = ctk.CTkFrame(self, fg_color=C["white"], height=26,
                              corner_radius=0, border_width=1,
                              border_color=C["border"])
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        self.status_lbl = ctk.CTkLabel(status, text="Ready",
            font=FONT["xs"], text_color=C["slate"])
        self.status_lbl.pack(side="left", padx=16, pady=3)

        # Show dashboard
        self._show_dashboard()

    # ═══════════════════════════════════════════════════════
    # DASHBOARD (History View)
    # ═══════════════════════════════════════════════════════
    def _show_dashboard(self):
        self._clear_content()
        self._active_view = "dashboard"
        self.btn_new_dl.pack(side="right", padx=(8, 0))

        v = ctk.CTkFrame(self.content, fg_color="transparent")
        v.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(v, text="Downloads", font=FONT["hero"],
                     text_color=C["navy"]).pack(anchor="w")
        ctk.CTkLabel(v, text="Your documentation downloads and their status",
                     font=FONT["body"], text_color=C["slate"]).pack(anchor="w", pady=(2, 20))

        downloads = self._history.get("downloads", [])

        if not downloads:
            # Empty state
            empty = ctk.CTkFrame(v, fg_color=C["white"], corner_radius=8,
                                border_width=1, border_color=C["border"])
            empty.pack(fill="x", pady=20)
            ctk.CTkLabel(empty, text="No downloads yet",
                         font=FONT["h1"], text_color=C["navy"]).pack(pady=(32, 4))
            ctk.CTkLabel(empty, text="Click '+ New Download' to get started",
                         font=FONT["body"], text_color=C["slate"]).pack(pady=(0, 24))
            return

        # Scrollable list
        scroll = ctk.CTkScrollableFrame(v, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for i, dl in enumerate(downloads):
            self._build_history_card(scroll, dl, i)

    def _build_history_card(self, parent, dl, index):
        """A card showing one past download."""
        card = ctk.CTkFrame(parent, fg_color=C["card_bg"], corner_radius=6,
                           border_width=1, border_color=C["border"])
        card.pack(fill="x", pady=3)

        # Row 1: URL + date
        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=(12, 4))

        # Domain pill
        from urllib.parse import urlparse
        domain = urlparse(dl["url"]).netloc
        pill = ctk.CTkFrame(r1, fg_color=C["border"], corner_radius=4)
        pill.pack(side="left")
        ctk.CTkLabel(pill, text=domain, font=FONT["xs"],
                     text_color=C["navy"]).pack(padx=8, pady=2)

        ctk.CTkLabel(r1, text=dl["date"], font=FONT["xs"],
                     text_color=C["slate"]).pack(side="right")

        # Row 2: File path
        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=(0, 6))
        fname = os.path.basename(dl["output"])
        ctk.CTkLabel(r2, text=f"📄 {fname}", font=FONT["body"],
                     text_color=C["slate"]).pack(side="left")

        # Row 3: Stats + actions
        r3 = ctk.CTkFrame(card, fg_color="transparent")
        r3.pack(fill="x", padx=16, pady=(0, 12))

        stats_frame = ctk.CTkFrame(r3, fg_color="transparent")
        stats_frame.pack(side="left")

        for lbl, val, color in [
            ("Pages", str(dl["pages"]), C["navy"]),
            ("Size", f"{dl['size_kb']/1024:.1f} MB" if dl["size_kb"] > 1024 else f"{dl['size_kb']:.0f} KB", C["slate"]),
        ]:
            sg = ctk.CTkFrame(stats_frame, fg_color="transparent")
            sg.pack(side="left", padx=(0, 16))
            ctk.CTkLabel(sg, text=val, font=FONT["stat"],
                         text_color=color).pack(side="left")
            ctk.CTkLabel(sg, text=f" {lbl}", font=FONT["xs"],
                         text_color=C["slate"]).pack(side="left")

        if dl.get("new_pages", 0) > 0:
            nb = ctk.CTkFrame(stats_frame, fg_color=C["green"], corner_radius=4)
            nb.pack(side="left")
            ctk.CTkLabel(nb, text=f"+{dl['new_pages']} new",
                         font=FONT["xs"], text_color=C["white"]).pack(padx=6, pady=1)

        # Actions
        acts = ctk.CTkFrame(r3, fg_color="transparent")
        acts.pack(side="right")

        ctk.CTkButton(acts, text="Update", width=64, height=28,
            font=FONT["xs"], fg_color=C["white"], text_color=C["purple"],
            hover_color=C["border"], corner_radius=4,
            border_width=1, border_color=C["purple_lt"],
            command=lambda d=dl: self._start_update(d)).pack(side="left", padx=3)

        ctk.CTkButton(acts, text="Split", width=52, height=28,
            font=FONT["xs"], fg_color=C["white"], text_color=C["slate"],
            hover_color=C["border"], corner_radius=4,
            border_width=1, border_color=C["border"],
            command=lambda d=dl: self._split_existing(d)).pack(side="left", padx=3)

        ctk.CTkButton(acts, text="Open", width=52, height=28,
            font=FONT["xs"], fg_color=C["white"], text_color=C["slate"],
            hover_color=C["border"], corner_radius=4,
            border_width=1, border_color=C["border"],
            command=lambda d=dl: os.startfile(d["output"])).pack(side="left", padx=3)

    # ═══════════════════════════════════════════════════════
    # NEW DOWNLOAD / UPDATE VIEW
    # ═══════════════════════════════════════════════════════
    def _show_new_download(self):
        self._clear_content()
        self._active_view = "download"
        self.btn_new_dl.pack_forget()

        v = ctk.CTkFrame(self.content, fg_color="transparent")
        v.pack(fill="both", expand=True, padx=24, pady=24)

        # Back + title
        top = ctk.CTkFrame(v, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkButton(top, text="← Back", command=self._show_dashboard,
            font=FONT["body"], fg_color="transparent", text_color=C["slate"],
            hover_color=C["border"], corner_radius=4, width=60, height=28).pack(side="left")

        ctk.CTkLabel(top, text="New Download", font=FONT["hero"],
                     text_color=C["navy"]).pack(side="left", padx=12)

        # URL card
        card = ctk.CTkFrame(v, fg_color=C["white"], corner_radius=8,
                           border_width=1, border_color=C["border"])
        card.pack(fill="x", pady=(20, 12))

        ctk.CTkLabel(card, text="GitBook URL", font=FONT["h2"],
                     text_color=C["navy"]).pack(anchor="w", padx=20, pady=(16, 6))

        url_row = ctk.CTkFrame(card, fg_color="transparent")
        url_row.pack(fill="x", padx=20, pady=(0, 16))

        self.url_entry = ctk.CTkEntry(url_row,
            placeholder_text="https://docs.example.com/",
            font=FONT["body"], height=42,
            fg_color=C["white"], border_color=C["border"],
            text_color=C["navy"], corner_radius=4)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_go = ctk.CTkButton(url_row, text="Download",
            command=self._start_fresh_download,
            font=FONT["btn"], height=42, width=120,
            fg_color=C["purple"], hover_color=C["purple_h"],
            corner_radius=4, text_color=C["white"])
        self.btn_go.pack(side="right")

        self.btn_stop = ctk.CTkButton(url_row, text="Cancel",
            command=self._stop_pipeline,
            font=FONT["body"], height=42, width=80,
            fg_color=C["white"], hover_color="#fef2f2",
            corner_radius=4, text_color=C["red"],
            border_width=1, border_color=C["border"], state="disabled")
        self.btn_stop.pack(side="right", padx=(0, 6))

        # Options
        opt_row = ctk.CTkFrame(v, fg_color="transparent")
        opt_row.pack(fill="x", pady=(0, 12))

        for lbl, attr, default, w in [
            ("Output file", "out_name", "downloaded_docs.md", 200),
            ("Max pages (0=all)", "max_pg", "0", 100),
            ("Workers", "workers", "5", 60),
        ]:
            g = ctk.CTkFrame(opt_row, fg_color=C["white"], corner_radius=6,
                            border_width=1, border_color=C["border"])
            g.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(g, text=lbl, font=FONT["xs"],
                         text_color=C["slate"]).pack(anchor="w", padx=12, pady=(8, 0))
            e = ctk.CTkEntry(g, font=FONT["body"], height=32, width=w,
                            fg_color=C["white"], border_color=C["border"],
                            text_color=C["navy"], corner_radius=4)
            e.insert(0, default)
            e.pack(padx=12, pady=(2, 8))
            setattr(self, f"opt_{attr}", e)

        # Progress area (hidden until download starts)
        self.prog_frame = ctk.CTkFrame(v, fg_color="transparent")

        self.phase_lbl = ctk.CTkLabel(v, text="", font=FONT["body"])
        self.progress = ctk.CTkProgressBar(v, fg_color=C["border"],
            progress_color=C["purple"], height=4, corner_radius=2)
        self.progress.set(0)
        self.detail_lbl = ctk.CTkLabel(v, text="", font=FONT["xs"])

        # Log
        log_card = ctk.CTkFrame(v, fg_color=C["white"], corner_radius=8,
                               border_width=1, border_color=C["border"])
        log_card.pack(fill="both", expand=True)
        ctk.CTkLabel(log_card, text="Activity", font=FONT["h2"],
                     text_color=C["navy"]).pack(anchor="w", padx=16, pady=(12, 4))

        self.log = ctk.CTkTextbox(log_card, font=FONT["mono"],
            fg_color="#fafbfc", border_width=0,
            text_color=C["dark_slate"], corner_radius=4, wrap="word")
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for tag, color in [
            ("success", C["green"]), ("error", C["red"]),
            ("highlight", C["purple"]), ("info", C["slate"]),
        ]:
            self.log.tag_config(tag, foreground=color)

    def _start_fresh_download(self):
        self._start_stream(update_existing=False)

    def _start_update(self, dl):
        """Update an existing download — only fetch new/changed pages."""
        self._show_new_download()
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, dl["url"])
        self.opt_out_name.delete(0, "end")
        self.opt_out_name.insert(0, dl["output"])
        self.btn_go.configure(text="Update", command=lambda: self._start_stream(update_existing=True))
        self.phase_lbl.configure(text=f"Will update: {os.path.basename(dl['output'])}")
        self.phase_lbl.pack(anchor="w", pady=(0, 8))

    def _start_stream(self, update_existing=False):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        out_name = self.opt_out_name.get().strip() or "downloaded_docs.md"
        try:
            mp = int(self.opt_max_pg.get())
        except ValueError:
            mp = 0
        try:
            w = int(self.opt_workers.get())
            w = max(1, min(w, 10))
        except ValueError:
            w = 5

        output = os.path.join(os.getcwd(), out_name)

        # Show progress area
        self.prog_frame.pack(fill="x", pady=(0, 8))
        self.phase_lbl.pack(anchor="w", pady=(0, 4))
        self.progress.pack(fill="x", pady=(0, 2))
        self.detail_lbl.pack(anchor="w")

        self.phase_lbl.configure(text="⏳ Starting streaming pipeline…", text_color=C["navy"])
        self.detail_lbl.configure(text="", text_color=C["slate"])
        self.progress.set(0)
        self.log.delete("1.0", "end")

        self._set_running(True)
        self.status_lbl.configure(text="Downloading…", text_color=C["purple"])

        self._events = queue.Queue()
        self._pipeline = DownloadPipeline(url, output, mp, w, update_existing,
                                           self._events)
        self._pipeline.start()
        self._poll()

    def _poll(self):
        try:
            while True:
                d = self._events.get_nowait()
                phase = d.get("phase", "")

                if phase == "discovery":
                    disc = d.get("discovered", 0)
                    self.phase_lbl.configure(
                        text=f"🔍 Found {disc} pages — streaming downloads…")

                elif phase == "downloaded":
                    dl = d.get("downloaded", 0)
                    disc = d.get("discovered", 0)
                    title = d.get("title", "")
                    kb = d.get("size_kb", 0)
                    self.phase_lbl.configure(
                        text=f"📥 {dl} downloaded / {disc} discovered")
                    if disc > 0:
                        self.progress.set(min(dl / max(disc, 1), 1.0))
                    self.detail_lbl.configure(text=f"Last: {title} ({kb} KB)")
                    self.log.insert("end", f"  ✓ {title} ({kb} KB)\n", "success")
                    self.log.see("end")

                elif phase == "progress":
                    url = d.get("url", "")
                    self.detail_lbl.configure(text=f"Downloading: {url}")

                elif phase == "done":
                    new_pages = d.get("new_pages", d.get("downloaded", 0))
                    errors = d.get("errors", 0)
                    size = d.get("size_kb", 0)
                    elapsed = d.get("elapsed", 0)
                    output = d.get("output", "")

                    self.phase_lbl.configure(
                        text=f"✅ Complete — {new_pages} pages ({size/1024:.1f} MB)")
                    self.progress.set(1.0)
                    self.detail_lbl.configure(
                        text=f"Saved: {os.path.basename(output)}  |  {errors} errors  |  {elapsed}s")
                    self.status_lbl.configure(text="Done", text_color=C["green"])
                    self._set_running(False)

                    self.log.insert("end",
                        f"\n{'─'*40}\n"
                        f"✅ {new_pages} pages downloaded\n"
                        f"📄 {os.path.basename(output)}\n"
                        f"📏 {size/1024:.1f} MB\n"
                        f"{'─'*40}\n", "highlight")

                    # Auto-split prompt
                    self._offer_split(output)

                    self._pipeline = None
                    self._poll_job = None
                    return

                elif phase == "error":
                    self.phase_lbl.configure(text=f"❌ {d.get('message', 'Error')}",
                                             text_color=C["red"])
                    self.status_lbl.configure(text="Error", text_color=C["red"])
                    self._set_running(False)
                    self._pipeline = None
                    self._poll_job = None
                    return

        except queue.Empty:
            pass

        if self._pipeline and self._pipeline.is_alive():
            self._poll_job = self.after(150, self._poll)

    def _stop_pipeline(self):
        if self._pipeline:
            self._pipeline.stop()
            self.phase_lbl.configure(text="⏹ Cancelled", text_color=C["red"])
            self.status_lbl.configure(text="Cancelled", text_color=C["red"])
            self._set_running(False)
            self._pipeline = None

    def _set_running(self, running):
        s_run = "disabled" if running else "normal"
        s_idle = "normal" if running else "disabled"
        self.btn_go.configure(state=s_run)
        self.btn_stop.configure(state=s_idle)
        self.url_entry.configure(state=s_run)
        for attr in ("opt_out_name", "opt_max_pg", "opt_workers"):
            try:
                getattr(self, attr).configure(state=s_run)
            except Exception:
                pass

    # ── Split ──────────────────────────────────────────────
    def _offer_split(self, output):
        """Show a subtle split button after download completes."""
        if not os.path.exists(output):
            return
        f = ctk.CTkFrame(self.prog_frame, fg_color="transparent")
        f.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(f, text="Want AI-ready chunks?",
                     font=FONT["body"], text_color=C["slate"]).pack(side="left")
        ctk.CTkButton(f, text="Split into chunks", command=lambda: self._split_existing(
            {"output": output}),
            font=FONT["btn"], height=28, fg_color=C["purple"],
            hover_color=C["purple_h"], corner_radius=4,
            text_color=C["white"]).pack(side="left", padx=10)

    def _split_existing(self, dl):
        """Split an existing downloaded file."""
        fpath = dl["output"]
        if not os.path.exists(fpath):
            messagebox.showerror("Error", f"File not found: {fpath}")
            return

        out_dir = os.path.join(os.path.dirname(fpath) or ".", "chunks")

        try:
            chunks = split_markdown(fpath, out_dir, 1.0)
        except Exception as e:
            messagebox.showerror("Split Error", str(e))
            return

        total_kb = sum(sz for _, sz in chunks) / 1024
        msg = f"Created {len(chunks)} chunks ({total_kb:.0f} KB) in:\n{out_dir}"
        self.status_lbl.configure(text=f"Split: {len(chunks)} chunks", text_color=C["green"])
        messagebox.showinfo("Split Complete", msg)

    # ── Helpers ────────────────────────────────────────────
    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
