'use client';

import React, { useState } from 'react';
import { Header } from './Header';
import { Hero } from './Hero';
import { InstallModal } from './InstallModal';
import { DocHarvestGithubData } from '../lib/github';

interface ClientContainerProps {
  githubData: DocHarvestGithubData;
  children: React.ReactNode;
}

export function ClientContainer({ githubData, children }: ClientContainerProps) {
  const [installModalOpen, setInstallModalOpen] = useState(false);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Sticky Header */}
      <Header
        stars={githubData.stats.stars}
        onOpenInstallModal={() => setInstallModalOpen(true)}
      />

      {/* Hero Section */}
      <Hero onOpenInstallModal={() => setInstallModalOpen(true)} />

      {/* Child Server Sections */}
      {children}

      {/* Multi-OS Install Modal */}
      <InstallModal
        isOpen={installModalOpen}
        onClose={() => setInstallModalOpen(false)}
      />
    </div>
  );
}
