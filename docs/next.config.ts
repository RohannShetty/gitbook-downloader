import type { NextConfig } from "next";

const isGithubActions = process.env.GITHUB_ACTIONS === 'true';

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || (isGithubActions ? '/gitbook-downloader' : ''),
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
