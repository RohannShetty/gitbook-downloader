// Centralized version and download URLs for DocHarvest.
// Single source of truth — components import from here instead of hardcoding.

export const VERSION = '11.0.5';

const RELEASE_BASE =
  `https://github.com/RohannShetty/gitbook-downloader/releases/download/v${VERSION}`;

export const DOWNLOAD_URLS = {
  windows: `${RELEASE_BASE}/docharvest-windows-latest.exe`,
  linux: `${RELEASE_BASE}/docharvest-ubuntu-latest`,
  macos: `${RELEASE_BASE}/docharvest-macos-latest`,
};
