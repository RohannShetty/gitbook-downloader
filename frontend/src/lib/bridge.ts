/**
 * Python PyWebView API client with fallbacks for standalone dev.
 */

declare global {
  interface Window {
    pywebview?: {
      api: {
        detect: (url: string) => Promise<any>
        start_capture: (url: string, options: any) => Promise<any>
        cancel_capture: () => Promise<any>
        list_library: () => Promise<any[]>
        get_library_doc: (domain: string) => Promise<any>
        delete_domain: (domain: string) => Promise<any>
        open_folder: (path: string) => Promise<any>
        search_docs: (query: string, domain?: string) => Promise<any[]>
        diff_snapshots: (domain: string, v1: string, v2: string) => Promise<any>
        get_diagnostics: () => Promise<any>
        get_system_info: () => Promise<any>
        export_doc: (domain: string, format: string, customPath?: string) => Promise<any>
      }
    }
    onCaptureProgress?: (data: any) => void
    onCaptureDone?: (data: any) => void
  }
}

export const pyApi = {
  detect: async (url: string) => {
    if (window.pywebview?.api?.detect) return await window.pywebview.api.detect(url)
    return { detected: true, provider: 'gitbook', site_versions: ['v1'] }
  },
  startCapture: async (url: string, options: any) => {
    if (window.pywebview?.api?.start_capture) return await window.pywebview.api.start_capture(url, options)
    return { success: true, message: 'Simulated capture start' }
  },
  cancelCapture: async () => {
    if (window.pywebview?.api?.cancel_capture) return await window.pywebview.api.cancel_capture()
    return { success: true }
  },
  listLibrary: async () => {
    if (window.pywebview?.api?.list_library) return await window.pywebview.api.list_library()
    return [
      {
        domain: 'docs.openalgo.in',
        provider: 'gitbook',
        pages_count: 364,
        size_bytes: 4892011,
        snapshots: ['v1.0.7', 'v1.0.8'],
        last_crawled: '2026-08-23 15:00',
        folder: 'C:\\Users\\rohan\\.gitbook-downloader\\docs\\docs.openalgo.in',
        file_path: 'C:\\Users\\rohan\\.gitbook-downloader\\docs\\docs.openalgo.in\\docs.md'
      }
    ]
  },
  getLibraryDoc: async (domain: string) => {
    if (window.pywebview?.api?.get_library_doc) return await window.pywebview.api.get_library_doc(domain)
    return {
      success: true,
      domain,
      title: 'OpenAlgo Documentation',
      content: '# OpenAlgo Documentation\n\nWelcome to OpenAlgo documentation.\n\n## Quickstart\n\nInstall using python.',
      pages: [
        { path: 'index.md', title: 'Introduction', size: 1024 },
        { path: 'quickstart.md', title: 'Quickstart', size: 2048 },
      ]
    }
  },
  deleteDomain: async (domain: string) => {
    if (window.pywebview?.api?.delete_domain) return await window.pywebview.api.delete_domain(domain)
    return { success: true }
  },
  openFolder: async (path: string) => {
    if (window.pywebview?.api?.open_folder) return await window.pywebview.api.open_folder(path)
    return { success: true }
  },
  searchDocs: async (query: string, domain?: string) => {
    if (window.pywebview?.api?.search_docs) return await window.pywebview.api.search_docs(query, domain)
    return [
      { domain: 'docs.openalgo.in', title: 'Quickstart Guide', snippet: 'Fast start with OpenAlgo Python API', score: 10 }
    ]
  },
  diffSnapshots: async (domain: string, v1: string, v2: string) => {
    if (window.pywebview?.api?.diff_snapshots) return await window.pywebview.api.diff_snapshots(domain, v1, v2)
    return { success: true, changes: [{ file: 'docs.md', lines_added: 12, lines_removed: 4, diff_text: '@@ -1,4 +1,12 @@\n+ Added feature' }] }
  },
  getDiagnostics: async () => {
    if (window.pywebview?.api?.get_diagnostics) return await window.pywebview.api.get_diagnostics()
    return {}
  },
  getSystemInfo: async () => {
    if (window.pywebview?.api?.get_system_info) return await window.pywebview.api.get_system_info()
    return { version: '9.0.0-beta.1', python: '3.11.15', platform: 'win32', library_dir: 'C:\\Users\\rohan\\.gitbook-downloader\\docs' }
  },
  exportDoc: async (domain: string, format: string, customPath?: string) => {
    if (window.pywebview?.api?.export_doc) return await window.pywebview.api.export_doc(domain, format, customPath)
    return { success: true, path: `exports/${domain}-docs.${format}`, format }
  }
}
