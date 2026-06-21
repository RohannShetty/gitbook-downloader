"""
Dashboard GUI — Linear-inspired dark theme for GitBook Downloader.

Provides two tabs:
  📥 Download — Two-phase engine with live stats, progress, and activity log
  ✂️ Split   — Markdown chunker with file picker and results viewer
"""

import os
import sys
import json
import queue
import threading
from datetime import timedelta

import customtkinter as ctk
from tkinter import filedialog, messagebox

from .engine import SmartEngine
from .splitter import split_markdown

# ── Appearance ──────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

C = {
    "bg": "#08090a",
    "panel": "#0f1011",
    "surface": "#191a1b",
    "card": "#1a1b1c",
    "border": "#23252a",
    "text": "#f7f8f8",
    "text2": "#d0d6e0",
    "muted": "#8a8f98",
    "accent": "#5e6ad2",
    "accent_h": "#828fff",
    "green": "#27a644",
    "red": "#e5484d",
    "amber": "#d97706",
}
FONT = {}


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._init_fonts()
        self.title("GitBook Downloader v3.1")
        self.geometry("1020x800")
        self.configure(fg_color=C["bg"])
        self.minsize(860, 660)

        self.engine = None
        self._poll_job = None
        self._stat_labels = {}
        self._build()

    def _init_fonts(self):
        FONT.update({
            "h1":   ctk.CTkFont(family="Inter", size=22, weight="bold"),
            "h2":   ctk.CTkFont(family="Inter", size=15, weight="bold"),
            "h3":   ctk.CTkFont(family="Inter", size=12, weight="bold"),
            "body": ctk.CTkFont(family="Inter", size=13),
            "sm":   ctk.CTkFont(family="Inter", size=11),
            "xs":   ctk.CTkFont(family="Inter", size=10),
            "mono": ctk.CTkFont(family="Consolas", size=11),
            "stat": ctk.CTkFont(family="Inter", size=22, weight="bold"),
        })

    def _make_stat(self, parent, title, value, col, color):
        card = ctk.CTkFrame(parent, fg_color=C["card"], corner_radius=8)
        card.grid(row=0, column=col, padx=4, pady=6, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=title, font=FONT["xs"], text_color=C["muted"]).pack(pady=(8, 0))
        lbl = ctk.CTkLabel(card, text=value, font=FONT["stat"], text_color=color)
        lbl.pack(pady=(0, 8))
        return lbl

    # ── Build ────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=C["panel"], height=56, corner_radius=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⬡", font=ctk.CTkFont(size=24), text_color=C["accent"],
                     width=40).pack(side="left", padx=(16, 4), pady=10)
        ctk.CTkLabel(hdr, text="GitBook Downloader", font=FONT["h2"],
                     text_color=C["text"]).pack(side="left", pady=10)
        ctk.CTkLabel(hdr, text="v3.1 — sitemaps + retries + token-aware split",
                     font=FONT["sm"], text_color=C["muted"]).pack(side="left", padx=12, pady=10)
        ver = ctk.CTkLabel(hdr, text="v3.1", font=FONT["xs"], text_color=C["muted"],
                           fg_color=C["card"], corner_radius=4, width=36, height=22)
        ver.pack(side="right", padx=16, pady=15)

        # Tabs
        self.tabs = ctk.CTkTabview(self, fg_color=C["bg"],
                                   segmented_button_fg_color=C["panel"],
                                   segmented_button_selected_color=C["accent"],
                                   segmented_button_unselected_color=C["panel"],
                                   segmented_button_selected_hover_color=C["accent_h"],
                                   text_color=C["text"])
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(12, 16))
        self.tab_dl = self.tabs.add("  📥 Download  ")
        self.tab_sp = self.tabs.add("  ✂️  Split    ")
        self.tab_dl.configure(fg_color=C["bg"])
        self.tab_sp.configure(fg_color=C["bg"])
        self._build_download()
        self._build_split()

    def _build_download(self):
        t = self.tab_dl

        # URL
        uf = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        uf.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(uf, text="Target URL", font=FONT["h3"], text_color=C["text2"]).pack(anchor="w", padx=14, pady=(10, 0))
        row = ctk.CTkFrame(uf, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(4, 12))

        self.url_in = ctk.CTkEntry(row, placeholder_text="https://docs.example.com/",
                                   font=FONT["body"], height=42, fg_color=C["surface"],
                                   border_color=C["border"], text_color=C["text"],
                                   placeholder_text_color=C["muted"], corner_radius=8)
        self.url_in.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_go = ctk.CTkButton(row, text="▶  Start", command=self._dl_start,
                                    font=ctk.CTkFont(size=13, weight="bold"),
                                    height=42, width=130, fg_color=C["accent"],
                                    hover_color=C["accent_h"], corner_radius=8, text_color="#ffffff")
        self.btn_go.pack(side="right")
        self.btn_stop = ctk.CTkButton(row, text="■  Stop", command=self._dl_stop,
                                      font=FONT["body"], height=42, width=80, fg_color=C["surface"],
                                      hover_color="#3a2020", corner_radius=8, text_color=C["text2"],
                                      border_width=1, border_color=C["border"], state="disabled")
        self.btn_stop.pack(side="right", padx=(0, 8))

        # Options
        opt = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        opt.pack(fill="x", padx=8, pady=4)
        for i, (label, var, default, w) in enumerate([
            ("Output file", "fname_in", "downloaded_docs.md", 220),
            ("Max pages", "maxpg_in", "5000", 80),
            ("Parallel", "concurrency_in", "5", 60),
        ]):
            ctk.CTkLabel(opt, text=label, font=FONT["sm"], text_color=C["muted"]).grid(
                row=0, column=i, sticky="w", padx=14, pady=(10, 0))
            entry = ctk.CTkEntry(opt, font=FONT["body"], height=34, width=w,
                                 fg_color=C["surface"], border_color=C["border"],
                                 text_color=C["text"], corner_radius=6)
            entry.insert(0, default)
            entry.grid(row=1, column=i, sticky="w", padx=14, pady=(2, 10))
            setattr(self, var, entry)
        opt.grid_columnconfigure(2, weight=1)

        # Stats
        st = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        st.pack(fill="x", padx=8, pady=4)
        grid = ctk.CTkFrame(st, fg_color="transparent")
        grid.pack(fill="x", padx=8, pady=8)
        for k, col, color in [
            ("discovered", 0, C["amber"]),
            ("downloaded", 1, C["green"]),
            ("failed", 2, C["red"]),
            ("retries", 3, C["amber"]),
            ("elapsed", 4, C["muted"]),
        ]:
            self._stat_labels[k] = self._make_stat(grid, k.title(), "0" if k != "elapsed" else "0s", col, color)

        # Phase
        self.phase_lbl = ctk.CTkLabel(t, text="Ready", font=FONT["sm"], text_color=C["muted"],
                                      fg_color=C["surface"], corner_radius=4, width=240, height=24)
        self.phase_lbl.pack(pady=(4, 2))

        # Progress
        self.prog = ctk.CTkProgressBar(t, fg_color=C["surface"], progress_color=C["accent"], height=8, corner_radius=4)
        self.prog.pack(fill="x", padx=18, pady=(6, 2))
        self.prog.set(0)
        self.prog_lbl = ctk.CTkLabel(t, text="", font=FONT["xs"], text_color=C["muted"])
        self.prog_lbl.pack(pady=(0, 2))
        self.cur_lbl = ctk.CTkLabel(t, text="", font=FONT["xs"], text_color=C["muted"])
        self.cur_lbl.pack(anchor="w", padx=18)

        # Log
        lf = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        lf.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        hr = ctk.CTkFrame(lf, fg_color="transparent")
        hr.pack(fill="x", padx=14, pady=(8, 2))
        ctk.CTkLabel(hr, text="Activity Log", font=FONT["h3"], text_color=C["text2"]).pack(side="left")
        ctk.CTkButton(hr, text="Clear", command=lambda: self.log.delete("1.0", "end"),
                      font=FONT["xs"], height=22, width=50, fg_color=C["surface"],
                      hover_color="#28282c", corner_radius=4, text_color=C["muted"],
                      border_width=1, border_color=C["border"]).pack(side="right")

        self.log = ctk.CTkTextbox(lf, font=FONT["mono"], fg_color=C["bg"],
                                  border_color=C["border"], border_width=1,
                                  text_color=C["text2"], corner_radius=6, wrap="word")
        self.log.pack(fill="both", expand=True, padx=10, pady=(2, 10))
        for tag, color in [
            ("info", C["muted"]),
            ("success", C["green"]),
            ("error", C["red"]),
            ("highlight", C["accent_h"]),
            ("phase", C["amber"]),
        ]:
            self.log.tag_config(tag, foreground=color)

    def _build_split(self):
        t = self.tab_sp

        # File picker
        fr = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        fr.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(fr, text="Markdown File", font=FONT["h3"], text_color=C["text2"]).pack(anchor="w", padx=14, pady=(10, 0))
        row = ctk.CTkFrame(fr, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(4, 12))
        self.sp_file_lbl = ctk.CTkLabel(row, text="No file selected", font=FONT["body"],
                                        text_color=C["muted"], fg_color=C["surface"],
                                        corner_radius=6, height=38, anchor="w")
        self.sp_file_lbl.pack(side="left", fill="x", expand=True, padx=(0, 8), ipadx=10)
        ctk.CTkButton(row, text="Browse", command=self._sp_browse, font=FONT["body"],
                      height=38, width=90, fg_color=C["surface"], hover_color="#28282c",
                      corner_radius=6, text_color=C["text2"], border_width=1, border_color=C["border"]).pack(side="right")

        # Options
        opt = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        opt.pack(fill="x", padx=8, pady=4)
        ctk.CTkLabel(opt, text="Chunk size (MB)", font=FONT["sm"], text_color=C["muted"]).grid(
            row=0, column=0, sticky="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(opt, text="Output folder", font=FONT["sm"], text_color=C["muted"]).grid(
            row=0, column=1, sticky="w", padx=14, pady=(10, 0))
        self.sp_size = ctk.CTkEntry(opt, font=FONT["body"], height=34, width=80,
                                    fg_color=C["surface"], border_color=C["border"],
                                    text_color=C["text"], corner_radius=6)
        self.sp_size.insert(0, "1.0")
        self.sp_size.grid(row=1, column=0, sticky="w", padx=14, pady=(2, 10))
        outr = ctk.CTkFrame(opt, fg_color="transparent")
        outr.grid(row=1, column=1, sticky="ew", padx=14, pady=(2, 10))
        opt.grid_columnconfigure(1, weight=1)
        self.sp_out_lbl = ctk.CTkLabel(outr, text="(auto: chunks/)", font=FONT["sm"],
                                       text_color=C["muted"], fg_color=C["surface"],
                                       corner_radius=6, height=34, anchor="w")
        self.sp_out_lbl.pack(side="left", fill="x", expand=True, ipadx=10)
        ctk.CTkButton(outr, text="Choose", command=self._sp_outdir, font=FONT["sm"],
                      height=34, width=70, fg_color=C["surface"], hover_color="#28282c",
                      corner_radius=6, text_color=C["text2"], border_width=1, border_color=C["border"]).pack(side="right")

        ctk.CTkButton(t, text="✂  Split File", command=self._sp_run,
                      font=ctk.CTkFont(size=13, weight="bold"), height=40, width=160,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      corner_radius=8, text_color="#ffffff").pack(anchor="e", padx=8, pady=4)

        self.sp_prog = ctk.CTkProgressBar(t, fg_color=C["surface"], progress_color=C["accent"], height=8, corner_radius=4)
        self.sp_prog.pack(fill="x", padx=18, pady=(8, 2))
        self.sp_prog.set(0)
        self.sp_prog_lbl = ctk.CTkLabel(t, text="", font=FONT["xs"], text_color=C["muted"])
        self.sp_prog_lbl.pack(pady=(0, 2))

        rf = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        rf.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        ctk.CTkLabel(rf, text="Results", font=FONT["h3"], text_color=C["text2"]).pack(anchor="w", padx=14, pady=(8, 2))
        self.sp_result = ctk.CTkTextbox(rf, font=FONT["mono"], fg_color=C["bg"],
                                        border_color=C["border"], border_width=1,
                                        text_color=C["text2"], corner_radius=6, wrap="word")
        self.sp_result.pack(fill="both", expand=True, padx=10, pady=(2, 10))
        for tag, c in [("success", C["green"]), ("error", C["red"]), ("info", C["muted"])]:
            self.sp_result.tag_config(tag, foreground=c)

    # ═══════════════════════════════════════════════════════════
    # DOWNLOAD LOGIC
    # ═══════════════════════════════════════════════════════════
    def _dl_start(self):
        url = self.url_in.get().strip()
        if not url:
            messagebox.showerror("Error", "Enter a URL")
            return
        fname = self.fname_in.get().strip() or "downloaded_docs.md"
        try:
            mp = int(self.maxpg_in.get())
        except ValueError:
            mp = 5000
        try:
            cc = int(self.concurrency_in.get())
            SmartEngine.CONCURRENCY = max(1, min(cc, 10))
        except ValueError:
            SmartEngine.CONCURRENCY = 5

        out = os.path.join(os.getcwd(), fname)

        self.log.delete("1.0", "end")
        self.log.insert("end", (
            f"╔══ DOWNLOAD ══╗\n"
            f"║ URL:  {url}\n"
            f"║ File: {fname}\n"
            f"║ Max:  {mp} pages\n"
            f"║ Workers: {SmartEngine.CONCURRENCY}\n"
            f"╚{'═'*14}╝\n\n"
        ), "highlight")

        self.prog.set(0)
        self.prog_lbl.configure(text="Phase 1: Discovery…")
        self.phase_lbl.configure(text="🔍 Discovery Phase", text_color=C["amber"])
        self.cur_lbl.configure(text="")

        for k in ("discovered", "downloaded", "failed", "retries"):
            self._stat_labels[k].configure(text="0")
        self._stat_labels["elapsed"].configure(text="0s")

        self.btn_go.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        for w in (self.url_in, self.fname_in, self.maxpg_in, self.concurrency_in):
            w.configure(state="disabled")

        self.engine = SmartEngine(url, out, mp)
        threading.Thread(target=self.engine.run, daemon=True).start()
        self._dl_poll()

    def _dl_poll(self):
        if self.engine is None:
            return
        try:
            while True:
                e = self.engine.log.get_nowait()
                self.log.insert("end", e["msg"] + "\n", e["level"])
                self.log.see("end")
                s = e["stats"]
                self._stat_labels["discovered"].configure(text=str(s["discovered"]))
                self._stat_labels["downloaded"].configure(text=str(s["downloaded"]))
                self._stat_labels["failed"].configure(text=str(s["failed"]))
                self._stat_labels["retries"].configure(text=str(s.get("retries", 0)))
                el = s.get("elapsed", 0)
                self._stat_labels["elapsed"].configure(text=str(timedelta(seconds=int(el))) if el else "…")

                ph = s.get("phase", "discovery")
                if ph == "discovery":
                    self.phase_lbl.configure(text="🔍 Discovery Phase — finding all pages…", text_color=C["amber"])
                    if s["discovered"] > 0:
                        self.prog.set(min(s["discovered"] / max(s["discovered"] + 50, 1), 0.3))
                else:
                    self.phase_lbl.configure(text="📥 Download Phase", text_color=C["green"])
                    if s["discovered"] > 0:
                        self.prog.set(0.3 + 0.7 * min(s["downloaded"] / max(s["discovered"], 1), 1.0))

                total_done = s["downloaded"] + s["failed"]
                if ph == "discovery":
                    self.prog_lbl.configure(text=f"Discovery: {s['discovered']} URLs found…")
                elif total_done > 0:
                    self.prog_lbl.configure(text=f"{s['downloaded']} ok / {s['failed']} fail / {s['discovered']} total")

                if e["level"] in ("success", "error") and ("✓ [" in e.get("msg", "") or "✕ [" in e.get("msg", "")):
                    self.cur_lbl.configure(text=e["msg"])
        except queue.Empty:
            pass

        if self.engine.done.is_set():
            self._dl_done()
        else:
            self._poll_job = self.after(100, self._dl_poll)

    def _dl_done(self):
        self.btn_go.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.prog.set(1.0)
        self.prog_lbl.configure(text="Complete ✓")
        self.phase_lbl.configure(text="✅ Done", text_color=C["green"])
        self.cur_lbl.configure(text="")
        for w in (self.url_in, self.fname_in, self.maxpg_in, self.concurrency_in):
            w.configure(state="normal")
        self.engine = None
        self._poll_job = None

    def _dl_stop(self):
        if self.engine:
            self.engine.stop()
        self.btn_stop.configure(state="disabled")
        self.log.insert("end", "\n⏹  Stopping…\n", "error")

    # ═══════════════════════════════════════════════════════════
    # SPLIT LOGIC
    # ═══════════════════════════════════════════════════════════
    def _sp_browse(self):
        p = filedialog.askopenfilename(title="Select Markdown File", filetypes=[("Markdown", "*.md"), ("All", "*.*")])
        if p:
            self.sp_file_lbl.configure(text=p, text_color=C["text"])

    def _sp_outdir(self):
        p = filedialog.askdirectory(title="Select Output Folder")
        if p:
            self.sp_out_lbl.configure(text=p, text_color=C["text"])

    def _sp_run(self):
        inp = self.sp_file_lbl.cget("text")
        if inp == "No file selected" or not os.path.exists(inp):
            messagebox.showerror("Error", "Select a valid .md file")
            return
        try:
            size = float(self.sp_size.get())
        except ValueError:
            size = 1.0
        out_dir = self.sp_out_lbl.cget("text")
        if out_dir.startswith("(auto"):
            out_dir = os.path.join(os.path.dirname(inp) or ".", "chunks")

        self.sp_result.delete("1.0", "end")
        self.sp_result.insert("end", f"Input:  {inp}\nOutput: {out_dir}\nChunk:  {size} MB\n\n", "info")
        self.sp_prog.set(0)
        self.sp_prog_lbl.configure(text="Splitting…")
        try:
            chunks = split_markdown(inp, out_dir, size)
        except Exception as e:
            self.sp_result.insert("end", f"✕ {e}\n", "error")
            self.sp_prog_lbl.configure(text="Failed")
            return
        for fn, sz in chunks:
            kb = sz / 1024
            s = f"{kb / 1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"
            self.sp_result.insert("end", f"  ✓ {os.path.basename(fn):28s} {s:>8s}\n", "success")
        total_kb = sum(sz for _, sz in chunks) / 1024
        self.sp_result.insert("end", f"\n━━━ {len(chunks)} chunks ({total_kb:.0f} KB total) ━━━\n", "success")
        self.sp_prog.set(1.0)
        self.sp_prog_lbl.configure(text=f"{len(chunks)} chunks ✓")


def main():
    Dashboard().mainloop()


if __name__ == "__main__":
    main()
