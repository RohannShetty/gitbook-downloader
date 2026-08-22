"""Regression tests for unified URL identity (audit Critical #10).

One canonical normalize_url must exist: query strings are part of page
identity (so ?page=2 never collapses into ?page=1), while fragments,
trailing slashes, slash-runs and .md suffixes are not. Content probes
(<url>.md) must never carry a query string.
"""

from gitbook_downloader.providers import base as provider_base
from gitbook_downloader.utils import discovery


def test_single_source_of_truth():
    """Both historical import paths expose the SAME function object."""
    assert discovery.normalize_url is provider_base.normalize_url


def test_query_string_is_part_of_identity():
    n = provider_base.normalize_url
    assert n("https://docs.example.com/guide?page=1") != n(
        "https://docs.example.com/guide?page=2"
    )


def test_fragments_trailing_slash_md_suffix_stripped():
    n = provider_base.normalize_url
    assert n("https://x.com/docs/intro/#section") == "https://x.com/docs/intro"
    assert n("https://x.com/docs/intro/") == "https://x.com/docs/intro"
    assert n("https://x.com/docs/intro.md") == "https://x.com/docs/intro"


def test_slash_runs_collapsed():
    assert (
        provider_base.normalize_url("https://x.com//docs//intro")
        == "https://x.com/docs/intro"
    )


def test_content_probe_strips_query():
    probe = provider_base.content_probe_url("https://x.com/docs/api?page=2&lang=en")
    assert probe == "https://x.com/docs/api"


def test_probe_helpers_exported_from_discovery():
    assert discovery.content_probe_url is provider_base.content_probe_url
