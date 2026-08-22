# Download Flow Audit Findings — 2026-08-22

Scope: download-correctness audit of src/gitbook_downloader (engine, providers, discovery, retry, versioning/storage, mcp/server). Research only — nothing modified.

## Verdict
**Not trustworthy for download correctness — 4 blocking defects plus several high-severity content-corruption paths.**

- BLOCKER: MCP `download_docs` can never succeed — it calls `stream_download(..., output_file=...)` (mcp/server.py:138) but `stream_download` has no `output_file` parameter (engine.py:104-111) → `TypeError` on every invocation, caught and returned as `{"error": ...}` (server.py:182-184).
- BLOCKER: GitBook boilerplate stripper `_LLM_REF_LINE` is over-escaped and can never match (gitbook.py:31-34) → the "For the complete documentation index, see [llms.txt]" trailer leaks into every GitBook page downloaded via `.md` export.
- BLOCKER: `utils/discovery._fetch_sitemap_xml` requests `/sitemap` and `/sitemap.gz`, never `/sitemap.xml` (discovery.py:126-127) → the generic sitemap discovery path, including the brand-new walk-up code, finds essentially nothing.
- BLOCKER (latent): the new `_bfs_crawl` uses `urljoin`, which is never imported (engine.py:82; imports at engine.py:6-19 and :46-48) → `NameError` swallowed at engine.py:92-93 → BFS returns only the start page whenever the no-`extract_links` fallback branch runs.

Additionally: sitemap-derived URL sets get no host validation (foreign content can merge into a domain's book), soft-200 HTML responses can be stored as "markdown", charset handling is left entirely to `requests` defaults, and the combined book's page order is nondeterministic. The uncommitted changes are directionally right but ship one latent crash and build on the broken sitemap fetcher. No examined file exceeds 1000 lines.

## Critical bugs — wrong/incorrect downloaded content

1. **GitBook llms.txt trailer leaks into every page** — gitbook.py:31-34: `_LLM_REF_LINE = re.compile(r"^(>?\\s*For the complete documentation index, see \\[llms\\.txt\\].*)$", re.MULTILINE)`. In a raw string `\\s` / `\\[` / `\\.` mean *literal backslash*, so the pattern can never match real text; `strip_agent_boilerplate` (gitbook.py:41) therefore never removes the trailer from `.md` exports. Related: the boilerplate regexes' lookahead keeps the trailing `\n---\n` (gitbook.py:24, 28), leaving stray horizontal rules at page ends.
2. **HTML stored as markdown on soft-200** — gitbook.py:150-155 accepts any 200 on `<url>.md` as markdown unless text starts with `<!` or contains `data-dpl-id` in the first 500 chars; HTML starting `<html …>` (no doctype) or other SPA shells pass. Weaker still: mintlify.py:127-130 and docusaurus.py:114-119 check only `startswith("<!")`.
3. **Cross-domain pages merged into a domain's book** — sitemap parsers add every `<loc>` with no netloc check: generic.py:50-56, mintlify.py:70-80, docusaurus.py:59-65, readthedocs.py:62-68 (their llms.txt paths DO filter by netloc — inconsistent). engine.py:220-222 consumes the set as-is; the only downstream filter, `_is_english_url` (engine.py:199-209), tests path prefixes only and never host.
4. **Sitemap-index entries downloaded as pages** — utils/discovery.py:225-237 parses index `<loc>` sub-sitemaps but keeps them in the `all_raw` union → `.xml` files are returned as page URLs and fetched as content (they clear the 60-char minimum, engine.py:242). Providers repeat the mistake via `.//sm:loc` on `<sitemapindex>` documents: generic.py:52, mintlify.py:76, docusaurus.py:61, readthedocs.py:64.
5. **RTD extractor deletes content** — readthedocs.py:141-142 decomposes ANY `div` whose class contains `"header"` (e.g. `page-header`, in-article header blocks) → silent heading/content loss on Sphinx pages.
6. **Nav/sidebar leakage on selector-miss fallback** — every provider ultimately converts the whole `<body>` when its selectors miss: generic.py:140-142, gitbook.py:183-185, mintlify.py:158-160, docusaurus.py:149-151, readthedocs.py:164-166. Only tag-level `nav/footer/aside/script/style` are removed first; class-based sidebars/toolbars (e.g. MkDocs-Material-style `md-sidebar`, or Mintlify's `"content" in class` wrapper match, mintlify.py:157) survive into the markdown as navigation noise.
7. **No link rewriting anywhere** — markdownify emits hrefs verbatim (generic.py:143, gitbook.py:186, mintlify.py:161, docusaurus.py:152, readthedocs.py:167); relative links, `#anchors`, and `.md`-suffixed links are never absolutized/localized during assembly (engine.py:285-290) → broken/dangling links throughout the downloaded book.
8. **Charset handling left to requests defaults** — every content fetch stores `resp.text` with no `resp.encoding` correction and nothing ever applies `apparent_encoding`: generic.py:119,131; gitbook.py:152,164; mintlify.py:128,139; docusaurus.py:117,128; readthedocs.py:123; engine.py:67. Servers omitting/mislabeling charset yield mojibake in output files.
9. **Nondeterministic book + wrong stored title** — `combined` is built from `url_content.items()` in thread-completion order (engine.py:283-290) → page order changes between runs, invalidating snapshot diffs; the stored title is the first `# ` heading of the entire concatenation (engine.py:326 via base.py:105-110) = whichever page happened to finish first.
10. **Query-string collapse loses pages** — providers/base.py:16-22 `normalize_url` strips the entire query, so `?page=2`/`?id=X` variants dedupe into one URL (used by the BFS visited-set, engine.py:96), while utils/discovery.py:21-42 `normalize_url` KEEPS queries — two conflicting dedup keys for the same resource across one pipeline.

## Discovery bugs

1. **`/sitemap.xml` is never requested** — utils/discovery.py:124-136 `_fetch_sitemap_xml` loops `for suffix in ("", ".gz")` building `f"{base_url}/sitemap{suffix}"` → tries `/sitemap`, `/sitemap.gz`; the docstring claims `/sitemap.xml`. `discover_from_sitemap` and the new `_walk_up_sitemaps` (:163-193) therefore nearly always return empty → avoidable BFS fallback.
2. **BFS ignores `exclude_paths`** — `_bfs_crawl` (engine.py:24-101) has no exclude parameter and calls `provider.extract_links(current, html, path_scope=path_scope)` (engine.py:74) without excludes; exclusion patterns are silently unenforced whenever discovery fails.
3. **Engine exposes no path_scope/exclude_paths at all** — `stream_download`'s signature (engine.py:104-111) lacks both; scoping is inferred from the input URL's own path (engine.py:184-217), so configured exclusions cannot reach the engine through this entry point.
4. **English-language filter holes** (engine.py:187-217):
   - bare `zh` and `pt` missing from `_LANG_CODES` (only `zh-cn/zh-tw/zh-hans/zh-hant`, `pt-br`) → `/docs/zh/…`, `/docs/pt/…` pages downloaded into English crawls;
   - `if filtered:` (engine.py:212) — when EVERY URL is filtered out, the full unfiltered set is kept (filter silently disabled);
   - the filter applies only to discovered sets, never to BFS results;
   - `p.startswith(input_path)` without a segment boundary admits sibling paths (`/docs` matches `/docsx`);
   - legit English sections whose first segment looks like a language code (`/docs/id/`, `/docs/no/`) are dropped.
5. **Silent 500-page cap when unlimited requested** — engine.py:227 `max_pages=max_pages or 500` caps BFS at 500 even when the caller passed `max_pages=0`.
6. **llms.txt parsing gaps** — markdown-link regex requires absolute http(s) targets, so relative links are skipped entirely: gitbook.py:90, mintlify.py:60; utils/discovery.py:102-106 adds bare-URL capture but `(?:^|\s)(https?://\S+)` swallows trailing punctuation (`).` `,`) producing malformed URLs; `_same_domain` (discovery.py:58-62) demands equal scheme+netloc, so www/non-www mirrors listed in llms.txt are dropped wholesale.
7. **Namespace-rigid sitemap parsing** — all parsers require the standard sitemap xmlns: discovery.py:149-158, generic.py:51-52, mintlify.py:75-76, docusaurus.py:60-61, readthedocs.py:63-64; sitemaps without the namespace parse to zero URLs.
8. **Duplicate elimination split-brain** — BFS dedupes via base.normalize_url (query-stripped, engine.py:96-99) while discovered sets use discovery.normalize_url (query-kept, discovery.py:42); engine concatenates both worlds without re-normalizing (engine.py:220-231) → the same page can be crawled twice in different forms and appear twice in the book.
9. **Arbitrary truncation** — `crawl_urls[:max_pages]` (engine.py:230-231) slices in discovery order, not by relevance/priority.
10. **Anchor-only links enqueue the page again** — fragment links resolve to the full page path and pass the filters (generic.py:96-97 and equivalents in every provider); the visited-set saves correctness but wastes fetches and drops anchor context.
11. **Cross-ref**: host-unfiltered sitemap `<loc>`s and index-file-as-page issues are catalogued under Critical #3/#4 — they are equally discovery-correctness failures (missed filtering, garbage URLs admitted).

## Provider detection risks

1. **Selection mechanism** — `ProviderRegistry.detect` (base.py:129-148) fetches the ROOT URL once and returns the first `detect()==True` in priority order (gitbook 100 > mintlify 90 > docusaurus 80 > readthedocs 70 > generic 0; sort at base.py:125). Non-200 or a network exception ⇒ immediate Generic (base.py:136-140) *without trying other providers* — one transient blip downgrades extraction quality for the whole run.
2. **Mintlify signal is effectively "page mentions mintlify"** — mintlify.py:40: `"mintlify" in lower_html and "generator" in lower_html`. A generator meta tag is near-universal; any site whose prose mentions Mintlify (comparison posts, migration guides) is misrouted to MintlifyProvider at priority 90 — ahead of Docusaurus and RTD — producing wrong `.md` probing and `"content" in class` substring extraction (mintlify.py:157).
3. **ReadTheDocs signals over-match** — readthedocs.py:41 any occurrence of `"readthedocs"` (credit links, `readthedocs.io` URLs); :46 `'role="main"'` is a generic accessibility attribute on most modern sites; combined with footer text "read the docs" (:48), non-Sphinx sites get classified as RTD → the `div.header` purge (readthedocs.py:141) eats their content and `div.document` selects the wrong container.
4. **Detection samples only the landing page** — root marketing pages frequently lack provider markers even when `/docs` is GitBook/Docusaurus → Generic fallback → body-conversion nav leakage (Critical #6). Nothing re-checks the provider on deeper pages.
5. **Double detection / disagreement** — MCP detects a provider (server.py:109) then `stream_download` detects again internally (engine.py:137-138) via a second root fetch; the two can disagree if the site changes between fetches, and the outer instance is used only for its title (server.py:146).
6. **Misclassification blast radius** — wrong provider ⇒ different selector chain ⇒ either body-fallback nav leakage or the 60-char discard rule (engine.py:242) deleting legitimately short pages that were extracted poorly.

## Versioning & concurrency

1. **Snapshot sequencing race** — engine.py:308-320 snapshots the PREVIOUS docs.md after downloading; two concurrent runs on one domain both see `domain_exists`, both snapshot the same old content (duplicate identical versions), then both `save_doc`. Metadata read-modify-write in versioning.py:89-117 and manager.py:124-172 has no lock; last writer wins and intermediate `versions[]` entries are lost.
2. **Corrupt-metadata history reset** — `get_metadata` returns None on JSONDecodeError (manager.py:216-219); `save_doc` then takes the fresh-install branch (manager.py:127-155), resetting `latest_version` to 1.0.0 with a single-entry history → the next snapshot recomputes v1.0.1 and OVERWRITES the existing v1.0.1.md (versioning.py:91-97) — old snapshot content destroyed.
3. **Orphaned version files** — versioning.py:114-117 writes the version file but updates metadata only `if meta:`; with meta missing/corrupt the file exists with no registry entry (invisible to `get_versions`, subject to #2's overwrite).
4. **Non-atomic writes everywhere** — docs.md (manager.py:121), metadata.json (manager.py:230), version files (versioning.py:97) are plain `write_text`; a crash mid-write corrupts the latest book or the metadata (feeding #2/#3).
5. **MCP double-snapshot / double-save (dormant)** — server.py:113-115 snapshots, then the engine snapshots again (engine.py:309-312); the server saves (server.py:148-157) what the engine already saved (engine.py:322-331). Currently unreachable due to the `output_file` TypeError, but it is a two-versions-per-run design waiting behind that fix.
6. **Streaming-pipeline threading** — discovery is fully synchronous before the ThreadPoolExecutor starts (engine.py:150-231), so there is no discovery/download race in-process. Worker threads mutate counters under one lock (engine.py:245-248, 264-265); `progress_callback` fires from worker threads (engine.py:252-259) so any UI callback must be thread-safe. No deadlocks found: a single lock, no nesting.
7. **Retry double-writes** — HTTP retries are GET/HEAD-only in the urllib3 adapter (retry.py:59-68), so transport-level retries cannot duplicate writes; the genuine double-write hazard is architectural (#5). The engine relies solely on adapter-level retries; providers' explicit `timeout=20` overrides coexist fine with `TimeoutHTTPAdapter.setdefault` (retry.py:31-33).
8. **Versions trail reality** — snapshot-before-save ordering means `latest_version` metadata points at the PREVIOUS content while docs.md holds newer content that has no version entry (engine.py:308-331); diffs/changelog describe the previous transition, not the just-downloaded state.
9. **Rollback inflates versions** — every rollback pre-snapshots (versioning.py:219-222), bumping patch numbers even when nothing changed.

## Uncommitted-changes assessment

One `git diff` over engine.py, providers/generic.py, utils/discovery.py (+184/−19, all uncommitted):

- **providers/generic.py (+22/−17) — SOUND.** `discover_urls` now walks the path hierarchy building correct `…/sitemap.xml` candidates deepest-first (generic.py:41-58), replacing the single fixed `/sitemap.xml` attempt; llms.txt fallback retained. Pre-existing gaps remain (no netloc filter on `<loc>`, sitemap-index locs treated as pages).
- **utils/discovery.py (+40/−0) — BROKEN IN EFFECT.** The new `_walk_up_sitemaps` (:163-193) is reasonable in isolation but delegates to `_fetch_sitemap_xml`, which requests `/sitemap` and `/sitemap.gz` and never `/sitemap.xml` (:126-127, pre-existing bug the new code should have exposed) — the new feature cannot find real sitemaps; docstrings promise `.xml(.gz)` behavior the code doesn't implement.
- **engine.py (+122/−2) — MIXED, not shippable as-is.** Replacing `crawl_urls = [url]` with a real BFS is the right move, but (a) `_bfs_crawl`'s fallback branch uses never-imported `urljoin` (engine.py:82) → swallowed NameError → single-page crawls if that branch executes; (b) the new language filter keeps the UNFILTERED set when everything is filtered out (`if filtered:`, :212), misses bare `zh`/`pt`, never applies to BFS output, and matches path prefixes without segment boundaries.

Verdict: generic.py is commit-worthy after adding host filtering; discovery.py needs the `.xml` fix before its walk-up means anything; engine.py needs the import fix plus filter hardening.

## Rule violations

None. Line counts of the examined files (threshold: >1000 lines):

| File | Lines |
|---|---|
| mcp/server.py | 430 |
| engine.py | 406 |
| storage/manager.py | 311 |
| storage/versioning.py | 287 |
| utils/discovery.py | 248 |
| providers/gitbook.py | 188 |
| providers/readthedocs.py | 173 |
| providers/mintlify.py | 168 |
| providers/base.py | 161 |
| providers/docusaurus.py | 160 |
| providers/generic.py | 149 |
| utils/retry.py | 95 |

All within budget.
