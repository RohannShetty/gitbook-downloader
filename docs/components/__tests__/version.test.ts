import { describe, it, expect } from 'vitest';
import { VERSION, DOWNLOAD_URLS } from '../../lib/version';

describe('version constants', () => {
  it('should export VERSION as 11.0.2', () => {
    expect(VERSION).toBe('11.0.2');
  });

  it('should export DOWNLOAD_URLS with correct Windows URL', () => {
    expect(DOWNLOAD_URLS.windows).toBe(
      'https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.2/docharvest-windows-latest.exe'
    );
  });

  it('should export DOWNLOAD_URLS with correct Linux URL', () => {
    expect(DOWNLOAD_URLS.linux).toBe(
      'https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.2/docharvest-ubuntu-latest'
    );
  });

  it('should export DOWNLOAD_URLS with correct macOS URL', () => {
    expect(DOWNLOAD_URLS.macos).toBe(
      'https://github.com/RohannShetty/gitbook-downloader/releases/download/v11.0.2/docharvest-macos-latest'
    );
  });

  it('should have DOWNLOAD_URLS that include the VERSION in their paths', () => {
    const allUrls = Object.values(DOWNLOAD_URLS);
    allUrls.forEach((url) => {
      expect(url).toContain(`v${VERSION}`);
    });
  });
});
