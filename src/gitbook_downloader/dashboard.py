"""
Dashboard GUI — Linear-inspired dark theme for GitBook Downloader.

Provides two tabs:
  📥 Download — BFS crawler with live progress
  ✂️ Split   — Markdown chunker with file picker
"""

import os
import queue
import threading
import time
from datetime import timedelta

import customtkinter as ctk
from tkinter import filedialog, messagebox

from .engine import download_docs
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


class DownloadThread(threading.Thread):
    """Runs download in background, feeds log entries to a queue."""

    def __init__(self, url, output, max_pages, log_queue):
        super().__init__(daemon=True)
        self.url = url
        self.output = output
        self.max_pages = max_pages
        self.log_queue = log_queue
        self._stop = threading.Event()
        self.result = None

    def run(self):
        visited = set()
        to_visit = [self.url]
        all_markdown = []
        base_domain = __import__("urllib.parse", fromlist=["urlparse"]).urlparse(self.url).netloc
        import requests
        from bs4 import BeautifulSoup
        from markdownify import markdownify as md
        from urllib.parse import urljoin, urlparse as uparse
        import re

        count = 0
        started = time.time()

        while to_visit and len(visited) < self.max_pages and not self._stop.is_set():
            url = to_visit.pop(0)
            if url in visited:
                continue
            count += 1

            self.log_queue.put({
                "level": "info", "msg": f"  [{count}] {url}",
                "downloaded": len(visited), "discovered": len(visited) + len(to_visit),
                "elapsed": int(time.time() - started), "phase": "download",
            })

            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code != 200:
                    self.log_queue.put({
                        "level": "error", "msg": f"  ⚠  HTTP {resp.status_code}: {url}",
                        "downloaded": len(visited), "discovered": len(visited) + len(to_visit),
                        "elapsed": int(time.time() - started), "phase": "download",
                    })
                    continue

                visited.add(url)
                soup = BeautifulSoup(resp.text, "html.parser")

                for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
                    tag.decompose()

                main = (
                    soup.find("main")
                    or soup.find("article")
                    or soup.find("div", class_="content")
                    or soup.body
                )
                html = str(main) if main else resp.text
                markdown = md(html, heading_style="ATX")
                markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)

                title = soup.find("h1")
                title_text = title.get_text().strip() if title else os.path.basename(url.rstrip("/")) or "Home"

                all_markdown.append(f"# {title_text}\n\nSource: {url}\n\n{markdown}\n\n---\n\n")

                self.log_queue.put({
                    "level": "success", "msg": f"  ✓ [{len(visited)}] {title_text}",
                    "downloaded": len(visited), "discovered": len(visited) + len(to_visit),
                    "elapsed": int(time.time() - started), "phase": "download",
                })

                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    full_url = urljoin(url, href)
                    parsed = uparse(full_url)
                    if parsed.netloc == base_domain and full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)

            except Exception as e:
                self.log_queue.put({
                    "level": "error", "msg": f"  ✕ {url}: {e}",
                    "downloaded": len(visited), "discovered": len(visited) + len(to_visit),
                    "elapsed": int(time.time() - started), "phase": "download",
                })

        # Write output
        try:
            with open(self.output, "w", encoding="utf-8") as f:
                f.write("\n".join(all_markdown))
        except Exception as e:
            self.log_queue.put({"level": "error", "msg": f"Write error: {e}", "downloaded": len(visited), "discovered": len(visited), "elapsed": int(time.time() - started), "phase": "done"})

        self.result = (len(visited), time.time() - started)
        self.log_queue.put({"level": "highlight", "msg": "", "downloaded": len(visited), "discovered": len(visited), "elapsed": int(time.time() - started), "phase": "done"})

    def stop(self):
        self._stop.set()


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._init_fonts()
        self.title("GitBook Downloader v3.1")
        self.geometry("1020x800")
        self.configure(fg_color=C["bg"])
        self.minsize(860, 660)

        self._thread = None
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

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=C["panel"], height=56, corner_radius=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⬡", font=ctk.CTkFont(size=24), text_color=C["accent"],
                     width=40).pack(side="left", padx=(16, 4), pady=10)
        ctk.CTkLabel(hdr, text="GitBook Downloader", font=FONT["h2"],
                     text_color=C["text"]).pack(side="left", pady=10)
        ctk.CTkLabel(hdr, text="v3.1 — simple BFS crawler + smart split",
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

        # URL input
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
            ("Max pages", "maxpg_in", "500", 80),
        ]):
            ctk.CTkLabel(opt, text=label, font=FONT["sm"], text_color=C["muted"]).grid(
                row=0, column=i, sticky="w", padx=14, pady=(10, 0))
            entry = ctk.CTkEntry(opt, font=FONT["body"], height=34, width=w,
                                 fg_color=C["surface"], border_color=C["border"],
                                 text_color=C["text"], corner_radius=6)
            entry.insert(0, default)
            entry.grid(row=1, column=i, sticky="w", padx=14, pady=(2, 10))
            setattr(self, var, entry)

        # Stats
        st = ctk.CTkFrame(t, fg_color=C["panel"], corner_radius=10)
        st.pack(fill="x", padx=8, pady=4)
        grid = ctk.CTkFrame(st, fg_color="transparent")
        grid.pack(fill="x", padx=8, pady=8)
        for k, col, color in [
            ("discovered", 0, C["amber"]),
            ("downloaded", 1, C["green"]),
            ("elapsed", 2, C["muted"]),
        ]:
            self._stat_labels[k] = self._make_stat(grid, k.title(), "0" if k != "elapsed" else "0s", col, color)

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
        ctk.CTkLabel(opt, text="Chunk size (MB)", font=FONT["sm"], text_color=C["muted"]).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(opt, text="Output folder", font=FONT["sm"], text_color=C["muted"]).grid(row=0, column=1, sticky="w", padx=14, pady=(10, 0))
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
            mp = 500

        out = os.path.join(os.getcwd(), fname)
        self._log_queue = queue.Queue()

        self.log.delete("1.0", "end")
        self.log.insert("end", f"╔══ DOWNLOAD ══╗\n║ URL:  {url}\n║ File: {fname}\n║ Max:  {mp} pages\n╚{'═'*14}╝\n\n", "highlight")

        self.prog.set(0)
        self.prog_lbl.configure(text="Downloading…")
        self.cur_lbl.configure(text="")

        for k in ("discovered", "downloaded"):
            self._stat_labels[k].configure(text="0")
        self._stat_labels["elapsed"].configure(text="0s")

        self.btn_go.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        for w in (self.url_in, self.fname_in, self.maxpg_in):
            w.configure(state="disabled")

        self._thread = DownloadThread(url, out, mp, self._log_queue)
        self._thread.start()
        self._dl_poll()

    def _dl_poll(self):
        if self._thread is None:
            return
        try:
            while True:
                e = self._log_queue.get_nowait()
                if e["msg"]:
                    self.log.insert("end", e["msg"] + "\n", e["level"])
                    self.log.see("end")

                dl = e.get("downloaded", 0)
                disc = e.get("discovered", 0)
                el = e.get("elapsed", 0)

                self._stat_labels["downloaded"].configure(text=str(dl))
                self._stat_labels["discovered"].configure(text=str(disc))
                self._stat_labels["elapsed"].configure(text=str(timedelta(seconds=int(el))) if el else "…")
                self.cur_lbl.configure(text=e.get("msg", ""))

                if disc > 0:
                    self.prog.set(min(dl / max(disc, 1), 1.0))
                    self.prog_lbl.configure(text=f"{dl} downloaded / {disc} discovered")

                if e.get("phase") == "done":
                    self._dl_done(dl, el)
                    return
        except queue.Empty:
            pass

        if not self._thread.is_alive():
            self._dl_done(
                self._thread.result[0] if self._thread.result else 0,
                int(self._thread.result[1]) if self._thread.result else 0,
            )
            return

        self._poll_job = self.after(100, self._dl_poll)

    def _dl_done(self, pages, elapsed):
        self.btn_go.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.prog.set(1.0)
        self.prog_lbl.configure(text="Complete ✓")
        self.cur_lbl.configure(text=f"✅ Downloaded {pages} pages in {timedelta(seconds=int(elapsed))}")
        for w in (self.url_in, self.fname_in, self.maxpg_in):
            w.configure(state="normal")
        self._thread = None
        self._poll_job = None

    def _dl_stop(self):
        if self._thread:
            self._thread.stop()
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
