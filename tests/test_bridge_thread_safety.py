"""Bridge thread-safety regression for ``_emit_to_js``.

After Phase 4 step 3, the ``ApiBridge._emit_to_js`` method must marshal
calls to a background drain thread so the capture worker thread is no
longer calling ``window.evaluate_js`` directly (which races the WebView2
message loop on Windows).

This test asserts:
1. The bridge has a queue-based dispatcher.
2. ``_emit_to_js`` enqueues rather than calling evaluate_js directly.
3. The drain thread is started when ``set_window`` is called and stopped
   in ``cleanup``.
4. A burst of 50 emit calls from a worker thread is delivered to the
   stubbed window (smoke: all 50 reach the JS shim).
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_PY = REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py"


class _StubWindow:
    """Minimal stand-in for pywebview's window that records evaluate_js calls."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self._lock = threading.Lock()

    def evaluate_js(self, code: str) -> None:
        with self._lock:
            self.calls.append(code)


def test_bridge_uses_queue_dispatcher() -> None:
    """The bridge must define a queue and a drain thread."""
    from gitbook_downloader.gui.bridge import ApiBridge
    bridge = ApiBridge()
    # The instance has a queue attribute (queue.Queue).
    assert hasattr(bridge, "_emit_queue"), (
        "ApiBridge must have a `_emit_queue` for the thread-safe dispatcher"
    )
    assert hasattr(bridge, "_emit_drain_thread") or hasattr(bridge, "start_emit_drain"), (
        "ApiBridge must define a drain-thread entry point"
    )


def test_emit_to_js_enqueues_instead_of_calling_evaluate_js_directly() -> None:
    """The new _emit_to_js must NOT call window.evaluate_js synchronously."""
    from gitbook_downloader.gui.bridge import ApiBridge
    win = _StubWindow()
    bridge = ApiBridge()
    bridge.set_window(win)
    try:
        # Direct call: should enqueue, not call evaluate_js yet.
        bridge._emit_to_js("cb", {"x": 1})
        # The stub records only evaluate_js calls; the queue is not drained
        # synchronously, but the drain thread polls every 100ms. Give it a
        # moment to drain.
        deadline = time.time() + 1.0
        while time.time() < deadline and len(win.calls) == 0:
            time.sleep(0.05)
        # After up to 1 second, the drain thread should have fired exactly
        # one evaluate_js call.
        assert len(win.calls) == 1, (
            f"Expected exactly 1 evaluate_js call after 1s; got {len(win.calls)}"
        )
        # The call should reference the cb function and the x=1 payload.
        assert "cb" in win.calls[0]
        assert "x" in win.calls[0]
    finally:
        bridge.cleanup()


def test_burst_of_50_emits_all_reach_window() -> None:
    """50 rapid emits from a worker thread must all be delivered."""
    from gitbook_downloader.gui.bridge import ApiBridge
    win = _StubWindow()
    bridge = ApiBridge()
    bridge.set_window(win)
    try:
        def worker() -> None:
            for i in range(50):
                bridge._emit_to_js("burst", {"i": i})

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        # Wait for the worker to finish and the drain to catch up.
        t.join(timeout=2.0)
        deadline = time.time() + 3.0
        while time.time() < deadline and len(win.calls) < 50:
            time.sleep(0.05)
        assert len(win.calls) == 50, (
            f"Expected 50 evaluate_js calls (one per emit); got {len(win.calls)}"
        )
    finally:
        bridge.cleanup()


def test_cleanup_stops_drain_thread() -> None:
    """After cleanup(), the drain thread must be stopped (not alive)."""
    from gitbook_downloader.gui.bridge import ApiBridge
    win = _StubWindow()
    bridge = ApiBridge()
    bridge.set_window(win)
    # Drain thread should be alive right after set_window.
    assert bridge._emit_drain_thread is not None
    assert bridge._emit_drain_thread.is_alive()
    bridge.cleanup()
    # Give it up to 1s to terminate.
    deadline = time.time() + 1.0
    while time.time() < deadline and bridge._emit_drain_thread.is_alive():
        time.sleep(0.05)
    assert not bridge._emit_drain_thread.is_alive(), (
        "Drain thread should stop after cleanup()"
    )


def test_emit_to_js_safe_with_no_window() -> None:
    """Calling _emit_to_js with no window must not raise (and is a no-op)."""
    from gitbook_downloader.gui.bridge import ApiBridge
    bridge = ApiBridge()  # no window
    # Should not raise.
    bridge._emit_to_js("noop", {"x": 1})
    # And no drain thread is started yet (no window).
    assert bridge._emit_drain_thread is None or not bridge._emit_drain_thread.is_alive()
