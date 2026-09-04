import type { MetadataRoute } from "next";

export const dynamic = "force-static";

const SITE = "https://rohannshetty.github.io/gitbook-downloader/";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${SITE}sitemap.xml`,
  };
}
