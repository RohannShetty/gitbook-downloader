"""
GitBook Downloader v5.0 — Editorial Dashboard
Warm amber + charcoal palette. Anti-default: no purple gradients.
Dark/light theme toggle. File rename support. Clean editorial density.
"""

import os, sys, json, time, queue, threading
from datetime import datetime
from tkinter import filedialog, messagebox

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
# DESIGN TOKENS — Editorial Amber
# ═══════════════════════════════════════════════════════════

class _T:
    _mode = "dark"

    @classmethod
    def set_mode(cls, mode):
        cls._mode = mode

    @classmethod
    def bg(cls):    return "#16141a" if cls._mode == "dark" else "#faf7f4"
    @classmethod
    def surface(cls): return "#1f1c24" if cls._mode == "dark" else "#ffffff"
    @classmethod
    def border(cls): return "#2e2936" if cls._mode == "dark" else "#e6e0d8"
    @classmethod
    def accent(cls): return "#e8983e"   # warm amber — constant accent
    @classmethod
    def accent_hover(cls): return "#f0a84c"
    @classmethod
    def text_primary(cls): return "#e8e4dd" if cls._mode == "dark" else "#2d2520"
    @classmethod
    def text_secondary(cls): return "#9d9490" if cls._mode == "dark" else "#6b635c"
    @classmethod
    def text_muted(cls): return "#5c5554" if cls._mode == "dark" else "#a09890"
    @classmethod
    def success(cls): return "#4ec9a0"
    @classmethod
    def error(cls): return "#e0556a"
    @classmethod
    def radius(cls): return 8
    @classmethod
    def font(cls): return "Segoe UI"


T = _T

DARK = {
    "bg": "#16141a", "surface": "#1f1c24", "border": "#2e2936",
    "text_primary": "#e8e4dd", "text_secondary": "#9d9490", "text_muted": "#5c5554",
}
LIGHT = {
    "bg": "#faf7f4", "surface": "#ffffff", "border": "#e6e0d8",
    "text_primary": "#2d2520", "text_secondary": "#6b635c", "text_muted": "#a09890",
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".gitbook-downloader")


# ═══════════════════════════════════════════════════════════
# PIPELINE THREAD
# ═══════════════════════════════════════════════════════════

class DownloadPipeline(threading.Thread):
    def __init__(self, url, output, max_pages, workers, update_existing, event_queue):
        super().__init__(daemon=True)
        self.url = url; self.output = output
        self.max_pages = max_pages; self.workers = workers
        self.update_existing = update_existing
        self.event_queue = event_queue; self._stop = threading.Event()

    def run(self):
        def cb(data):
            if self._stop.is_set(): raise SystemExit()
            self.event_queue.put(data)
        try:
            stream_download(self.url, self.output, max_pages=self.max_pages,
                          workers=self.workers, update_existing=self.update_existing,
                          progress_callback=cb)
        except SystemExit: pass
        except Exception as e:
            self.event_queue.put({"phase": "error", "message": str(e)})

    def stop(self): self._stop.set()


# ═══════════════════════════════════════════════════════════
# WIDGETS
# ═══════════════════════════════════════════════════════════

class C(ctk.CTkFrame):
    """Surface card — picks up theme from T."""
    def __init__(self, m, **kw):
        kw.setdefault("fg_color", T.surface())
        kw.setdefault("border_width", 1)
        kw.setdefault("border_color", T.border())
        kw.setdefault("corner_radius", T.radius())
        super().__init__(m, **kw)

class B(ctk.CTkButton):
    """Accent button."""
    def __init__(self, m, variant="primary", **kw):
        if variant == "primary":
            kw.setdefault("fg_color", T.accent())
            kw.setdefault("hover_color", T.accent_hover())
            kw.setdefault("text_color", "#ffffff")
        else:
            kw.setdefault("fg_color", "transparent")
            kw.setdefault("hover_color", T.border())
            kw.setdefault("text_color", T.text_secondary())
            kw.setdefault("border_width", 1)
            kw.setdefault("border_color", T.border())
        kw.setdefault("corner_radius", 6)
        kw.setdefault("font", (T.font(), 11, "bold"))
        kw.setdefault("height", 34)
        super().__init__(m, **kw)

class StatTile(C):
    def __init__(self, m, label, w=130, h=72):
        super().__init__(m, width=w, height=h)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text=label, font=(T.font(), 9),
                     text_color=T.text_muted()).pack(anchor="w", padx=12, pady=(8,0))
        self._v = ctk.CTkLabel(self, text="—", font=(T.font(), 16, "bold"),
                                text_color=T.text_primary())
        self._v.pack(anchor="w", padx=12, pady=(0,8))
    def set(self, t, c=None):
        self._v.configure(text=str(t), text_color=c or T.text_primary())

class Toast(ctk.CTkFrame):
    def __init__(self, m, msg, variant="info", dur=3000):
        bg_map = {"info": T.border(), "success": "#254d3c", "error": "#4d1c24"}
        border_map = {"info": T.border(), "success": T.success(), "error": T.error()}
        super().__init__(m, fg_color=bg_map.get(variant, bg_map["info"]),
                         border_width=1, border_color=border_map.get(variant, border_map["info"]),
                         corner_radius=6, height=36)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text=msg, font=(T.font(), 10),
                     text_color=T.text_primary()).pack(side="left", padx=14)
        self.after(dur, self.destroy)


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitBook Downloader v5.0")
        self.geometry("1060x700")
        self.configure(fg_color=T.bg())
        self.minsize(860, 560)
        self._pipeline = None; self._event_queue = queue.Queue()
        self._current_theme = "dark"
        self._build_ui()
        self._show_dashboard()
        self._start_poll()

    def _apply_theme(self, mode):
        self._current_theme = mode
        ctk.set_appearance_mode(mode)
        T.set_mode(mode)
        self.configure(fg_color=T.bg())
        # Rebuild to refresh all colors
        self._build_ui(); self._show_dashboard()

    def _build_ui(self):
        # Header
        h = ctk.CTkFrame(self, fg_color=T.surface(), height=52, corner_radius=0)
        h.pack(fill="x"); h.pack_propagate(False)

        lf = ctk.CTkFrame(h, fg_color="transparent"); lf.pack(side="left", padx=20)
        ctk.CTkLabel(lf, text="⬡ ", font=(T.font(), 22),
                     text_color=T.accent()).pack(side="left")
        ctk.CTkLabel(lf, text="GitBook Downloader", font=(T.font(), 15, "bold"),
                     text_color=T.text_primary()).pack(side="left", padx=(6,0))
        ctk.CTkLabel(lf, text="v5.0", font=(T.font(), 10),
                     text_color=T.text_muted()).pack(side="left", padx=(4,0))

        # Theme toggle
        rf = ctk.CTkFrame(h, fg_color="transparent"); rf.pack(side="right", padx=16)
        t = "☀️" if self._current_theme == "dark" else "🌙"
        self._theme_btn = B(rf, "ghost", text=t, width=36, height=36,
                            font=(T.font(), 14),
                            command=self._toggle_theme)
        self._theme_btn.pack(side="right", padx=(0,4))

        # Views
        self._views = ctk.CTkFrame(self, fg_color="transparent")
        self._views.pack(fill="both", expand=True, padx=20, pady=(8,4))

        self._toast_frame = ctk.CTkFrame(self._views, fg_color="transparent", height=0)
        self._toast_frame.pack(fill="x", side="bottom")

        # Footer
        f = ctk.CTkFrame(self, fg_color=T.surface(), height=24, corner_radius=0)
        f.pack(fill="x", side="bottom")
        ctk.CTkLabel(f, text="docs → markdown → AI", font=(T.font(), 9),
                     text_color=T.text_muted()).pack(pady=3)

    def _toggle_theme(self):
        self._apply_theme("light" if self._current_theme == "dark" else "dark")

    def _toast(self, msg, v="info", d=3000):
        Toast(self._toast_frame, msg, v, d).pack(fill="x", pady=(0,4))

    def _clear(self):
        for w in self._views.winfo_children():
            if w != self._toast_frame: w.destroy()

    # ── Dashboard ──

    def _show_dashboard(self):
        self._clear()
        c = ctk.CTkFrame(self._views, fg_color="transparent"); c.pack(fill="both", expand=True)

        # New download card
        card = C(c); card.pack(fill="x", pady=(0,14))

        ctk.CTkLabel(card, text="New Download", font=(T.font(), 18, "bold"),
                     text_color=T.text_primary()).pack(anchor="w", padx=18, pady=(14,2))
        ctk.CTkLabel(card, text="Paste a GitBook or MkDocs URL",
                     font=(T.font(), 11), text_color=T.text_secondary()
                     ).pack(anchor="w", padx=18, pady=(0,12))

        row = ctk.CTkFrame(card, fg_color="transparent"); row.pack(fill="x", padx=18, pady=(0,14))

        self._url_entry = ctk.CTkEntry(row, placeholder_text="https://docs.example.com/",
            font=(T.font(), 12), fg_color=T.bg(),
            text_color=T.text_primary(), border_color=T.border(),
            corner_radius=6, height=40)
        self._url_entry.pack(side="left", fill="x", expand=True)
        self._url_entry.bind("<Return>", lambda e: self._start_download())

        B(row, "primary", text="Start", width=110,
          command=self._start_download).pack(side="right", padx=(10,0))

        # History
        hist = load_history()
        if hist.get("downloads"):
            ctk.CTkLabel(c, text="History", font=(T.font(), 14, "bold"),
                         text_color=T.text_primary()).pack(anchor="w", pady=(0,8))
            for e in hist["downloads"][:8]:
                self._hist_card(c, e)

    def _hist_card(self, p, e):
        card = C(p); card.pack(fill="x", pady=(0,6))
        row = ctk.CTkFrame(card, fg_color="transparent"); row.pack(fill="x", padx=14, pady=10)

        info = ctk.CTkFrame(row, fg_color="transparent"); info.pack(side="left", fill="x", expand=True)
        name = e.get("url","").rstrip("/").split("/")[-1] or "Home"
        ctk.CTkLabel(info, text=name, font=(T.font(), 12, "bold"),
                     text_color=T.text_primary()).pack(anchor="w")
        ctk.CTkLabel(info, text=f"{e.get('pages',0)} pages · {e.get('size_kb',0)/1024:.1f}MB · {e.get('date','')}",
                     font=(T.font(), 10), text_color=T.text_muted()).pack(anchor="w")

        acts = ctk.CTkFrame(row, fg_color="transparent"); acts.pack(side="right")
        out = e.get("output","")

        B(acts, "ghost", text="Rename", width=70, height=28, font=(T.font(), 10),
          command=lambda p=out: self._rename_file(p)).pack(side="left", padx=2)
        B(acts, "ghost", text="Open", width=58, height=28, font=(T.font(), 10),
          command=lambda p=out: self._open_file(p)).pack(side="left", padx=2)
        B(acts, "ghost", text="Split", width=58, height=28, font=(T.font(), 10),
          command=lambda p=out: self._split_output(p)).pack(side="left", padx=2)
        B(acts, "ghost", text="Update", width=64, height=28, font=(T.font(), 10),
          command=lambda e=e: self._update_download(e)).pack(side="left", padx=2)

    # ── Download ──

    def _show_download(self, url):
        self._clear()
        c = ctk.CTkFrame(self._views, fg_color="transparent"); c.pack(fill="both", expand=True)

        card = C(c); card.pack(fill="x", pady=(0,12))
        ctk.CTkLabel(card, text="Downloading", font=(T.font(), 18, "bold"),
                     text_color=T.text_primary()).pack(anchor="w", padx=18, pady=(14,2))
        ctk.CTkLabel(card, text=url, font=(T.font(), 11),
                     text_color=T.text_secondary(), wraplength=600
                     ).pack(anchor="w", padx=18, pady=(0,12))

        sr = ctk.CTkFrame(card, fg_color="transparent"); sr.pack(fill="x", padx=18, pady=(0,12))
        self._s_disc = StatTile(sr, "Discovered"); self._s_disc.pack(side="left", padx=(0,4))
        self._s_dl = StatTile(sr, "Downloaded"); self._s_dl.pack(side="left", padx=4)
        self._s_err = StatTile(sr, "Errors"); self._s_err.pack(side="left", padx=4)
        self._s_size = StatTile(sr, "Size"); self._s_size.pack(side="left", padx=4)
        self._s_elap = StatTile(sr, "Elapsed"); self._s_elap.pack(side="left", padx=4)

        pf = ctk.CTkFrame(card, fg_color="transparent"); pf.pack(fill="x", padx=18, pady=(0,4))
        self._prog = ctk.CTkProgressBar(pf, fg_color=T.border(),
                                        progress_color=T.accent(), corner_radius=3, height=3)
        self._prog.pack(fill="x"); self._prog.set(0)
        self._status = ctk.CTkLabel(pf, text="Starting...", font=(T.font(), 10),
                                    text_color=T.text_muted())
        self._status.pack(anchor="w", pady=(3,0))

        log = C(c); log.pack(fill="both", expand=True)
        ctk.CTkLabel(log, text="Activity", font=(T.font(), 12, "bold"),
                     text_color=T.text_primary()).pack(anchor="w", padx=14, pady=(8,4))
        self._logb = ctk.CTkTextbox(log, fg_color="transparent", border_width=0,
                                     text_color=T.text_secondary(), font=("Consolas", 10), corner_radius=0)
        self._logb.pack(fill="both", expand=True, padx=14, pady=(0,10))

        ar = ctk.CTkFrame(c, fg_color="transparent"); ar.pack(fill="x", pady=(8,0))
        self._cancel_btn = B(ar, "ghost", text="Cancel", width=90, command=self._cancel_download)
        self._cancel_btn.pack(side="right")
        self._download_t0 = time.time()

    # ── Actions ──

    def _start_download(self):
        url = self._url_entry.get().strip()
        if not url: return self._toast("Enter a URL", "error")
        self._url = url; self._output = "downloaded_docs.md"
        self._show_download(url)
        self._pipeline = DownloadPipeline(url, self._output, 0, 5, False, self._event_queue)
        self._pipeline.start()

    def _update_download(self, e):
        self._url = e["url"]; self._output = e["output"]
        self._show_download(e["url"] + " (update)")
        self._pipeline = DownloadPipeline(e["url"], e["output"], 0, 5, True, self._event_queue)
        self._pipeline.start()

    def _cancel_download(self):
        if self._pipeline: self._pipeline.stop(); self._pipeline = None
        self._cancel_btn.configure(state="disabled")
        self._show_done_buttons()

    def _rename_file(self, path):
        if not os.path.exists(path):
            return self._toast("File not found", "error")
        # Non-blocking: use filedialog
        new = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(path) or ".",
            initialfile=os.path.basename(path),
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")])
        if new and new != path:
            try:
                os.rename(path, new)
                # Update history entry
                h = load_history()
                for entry in h.get("downloads", []):
                    if entry.get("output") and os.path.abspath(entry["output"]) == os.path.abspath(path):
                        entry["output"] = os.path.abspath(new)
                        save_history(h)
                        break
                self._toast(f"Renamed to {os.path.basename(new)}", "success")
                self._show_dashboard()
            except OSError as ex:
                self._toast(f"Rename failed: {ex}", "error")

    def _split_output(self, path):
        if not os.path.exists(path): return self._toast("File not found", "error")
        try:
            base = path.replace(".md","_chunks")
            chunks = split_markdown(path, base)
            self._toast(f"Split into {len(chunks)} chunks", "success")
        except Exception as e:
            self._toast(f"Split failed: {e}", "error")

    def _open_file(self, path):
        if os.path.exists(path): self.after(10, lambda: os.startfile(path))
        else: self._toast("File moved or deleted", "warning")

    def _show_done_buttons(self, dl=0):
        ar = ctk.CTkFrame(self._views.winfo_children()[0] if self._views.winfo_children() else self,
                          fg_color="transparent"); ar.pack(fill="x", pady=(6,0))
        B(ar, "ghost", text="Dashboard", width=90, command=self._show_dashboard).pack(side="left", padx=2)
        if self._output and os.path.exists(self._output):
            B(ar, "ghost", text="Rename", width=80,
              command=lambda: self._rename_file(self._output)).pack(side="left", padx=2)
            B(ar, "ghost", text="Split", width=70,
              command=lambda: self._split_output(self._output)).pack(side="left", padx=2)
            B(ar, "ghost", text="Open", width=70,
              command=lambda: self._open_file(self._output)).pack(side="left", padx=2)

    def _log(self, msg, c=None):
        try:
            tag = "d"
            if c: self._logb.tag_config(tag, foreground=c)
            self._logb.insert("end", msg + "\n", tag); self._logb.see("end")
        except Exception: pass

    # ── Poll ──

    def _start_poll(self):
        self._poll_running = True; self._poll_tick()

    def _poll_tick(self):
        if not self._poll_running: return
        try:
            while True: self._handle(self._event_queue.get_nowait())
        except queue.Empty: pass
        self.after(80, self._poll_tick)

    def _handle(self, d):
        p = d.get("phase",""); disc = d.get("discovered",0); dl = d.get("downloaded",0)
        err = d.get("errors",0); skb = d.get("size_kb",0); ela = d.get("elapsed",0)

        self._s_disc.set(disc); self._s_dl.set(dl, T.success() if dl>0 else T.text_primary())
        self._s_err.set(err, T.error() if err>0 else T.text_primary())
        if skb: self._s_size.set(f"{skb/1024:.1f}MB" if skb>1024 else f"{skb:.0f}KB")
        if ela: self._s_elap.set(f"{ela:.0f}s")

        if p == "progress":
            self._status.configure(text=d.get("url","")[:50])
            if disc: self._prog.set(dl/disc)
        elif p == "downloaded":
            self._log(f"  {d.get('url','')[:60]}  {d.get('size_kb',0):.1f}KB")
        elif p == "error":
            self._log("ERROR: " + d.get("message",""), T.error())
        elif p == "done":
            t = time.time()-self._download_t0
            self._status.configure(text=f"Done · {dl} pages · {err} errors · {t:.0f}s",
                                   text_color=T.success())
            self._prog.set(1.0)
            self._log(f"Done. {dl} pages, {err} errors, {t:.0f}s", T.success())
            self._pipeline = None; self._cancel_btn.configure(state="disabled", text="Done")
            self._show_done_buttons(dl)
            if dl > 0:
                self._toast(f"Downloaded {dl} pages · {skb/1024:.1f}MB" if skb else f"Downloaded {dl} pages", "success", 5000)


def ModernDashboard(): return App()

if __name__ == "__main__":
    App().mainloop()
