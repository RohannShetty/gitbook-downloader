"""HTTP retry with exponential backoff and timeout handling.

Provides a requests.Session pre-configured with retry strategy, timeout
adapter, and a helper for GET requests with structured error handling.
"""

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Default timeout (seconds) applied to every request when not overridden.
DEFAULT_TIMEOUT = 20


class TimeoutHTTPAdapter(HTTPAdapter):
    """Requests adapter that injects a per-request timeout.

    The timeout is applied as a default; callers can still override it per
    request via ``kwargs["timeout"]``.
    """

    def __init__(self, timeout: int | None = None, *args, **kwargs):
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return super().send(request, **kwargs)


def create_session(
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
    backoff_factor: float = 0.5,
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
) -> requests.Session:
    """Create a ``requests.Session`` with retry strategy and timeout.

    Args:
        timeout: Per-request timeout in seconds.
        retries: Max retry attempts on 429/5xx/connection errors.
        backoff_factor: Sleep = ``backoff_factor * (2 ** (retry - 1))``.
        user_agent: User-Agent header value.

    Returns:
        ``requests.Session`` with retry adapter mounted for http/https.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        respect_retry_after_header=True,
    )
    adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def retry_get(session: requests.Session, url: str, **kwargs):
    """Perform a GET request with retry and structured error handling.

    Args:
        session: A ``requests.Session`` (ideally from :func:`create_session`).
        url: The URL to fetch.
        **kwargs: Extra keyword arguments forwarded to ``session.get``.

    Returns:
        A ``(response, error)`` tuple.
        On success ``error`` is ``None`` and ``response`` is the
        ``requests.Response``.  On failure ``response`` is ``None`` and
        ``error`` is a short human-readable string (<= 80 chars).
    """
    try:
        resp = session.get(url, **kwargs)
        return resp, None
    except requests.Timeout:
        return None, "Timeout"
    except requests.ConnectionError:
        return None, "Connection failed"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)[:80]
