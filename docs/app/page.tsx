import React from 'react';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { DocTypeSelector } from '@/components/DocTypeSelector';
import { OutputContract } from '@/components/OutputContract';
import { ExportStudioPreview } from '@/components/ExportStudioPreview';
import { FeatureMatrix } from '@/components/FeatureMatrix';
import { McpShowcase } from '@/components/McpShowcase';
import { PersonaShowcase } from '@/components/PersonaShowcase';
import { GithubReleaseFeed } from '@/components/GithubReleaseFeed';
import { FaqSection } from '@/components/FaqSection';
import { Footer } from '@/components/Footer';
import { ClientContainer } from '@/components/ClientContainer';
import { getDocHarvestGithubData } from '@/lib/github';

export const revalidate = 3600;

export default async function Page() {
  const githubData = await getDocHarvestGithubData();

  return (
    <ClientContainer githubData={githubData}>
      {/* 1. Header is rendered in ClientContainer to manage install modal state */}
      <main>
        {/* 2. Hero with interactive terminal demo */}
        {/* 3. DocTypeSelector */}
        <DocTypeSelector />

        {/* 4. Four-Part Output Contract */}
        <OutputContract />

        {/* 5. Export Studio Code Inspection */}
        <ExportStudioPreview />

        {/* 6. Capability Comparison Matrix */}
        <FeatureMatrix />

        {/* 7. FastMCP Agent Tooling Showcase */}
        <McpShowcase />

        {/* 8. Three Persona Workflows */}
        <PersonaShowcase />

        {/* 9. Live GitHub Release Feed & Telemetry */}
        <GithubReleaseFeed data={githubData} />

        {/* 10. Frequently Asked Questions */}
        <FaqSection />
      </main>

      {/* 11. Footer */}
      <Footer />
    </ClientContainer>
  );
}
