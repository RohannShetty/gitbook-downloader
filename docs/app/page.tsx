import React from 'react';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { DocTypeSelector } from '@/components/DocTypeSelector';
import { AgentEcosystemShowcase } from '@/components/AgentEcosystemShowcase';
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
        {/* 2. Hero with interactive terminal demo (rendered inside ClientContainer) */}
        
        {/* 3. Supported AI Agent & IDE Ecosystem Directory */}
        <AgentEcosystemShowcase />

        {/* 4. Framework Intelligence & AST Heuristic Inspection */}
        <DocTypeSelector />

        {/* 5. Four-Part Output Contract */}
        <OutputContract />

        {/* 6. Export Studio Code Inspection */}
        <ExportStudioPreview />

        {/* 7. Capability Comparison Matrix vs Raw Scrapers & Cloud APIs */}
        <FeatureMatrix />

        {/* 8. FastMCP Agent Tooling Showcase */}
        <McpShowcase />

        {/* 9. Three Persona Workflows */}
        <PersonaShowcase />

        {/* 10. Live GitHub Release Feed & Telemetry */}
        <GithubReleaseFeed data={githubData} />

        {/* 11. Frequently Asked Questions */}
        <FaqSection />
      </main>

      {/* 12. Footer */}
      <Footer />
    </ClientContainer>
  );
}
