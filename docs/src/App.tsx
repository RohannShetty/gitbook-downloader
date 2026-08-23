import React, { useState } from "react"
import { Header } from "./components/Header"
import { Hero } from "./components/Hero"
import { DocTypeSelector } from "./components/DocTypeSelector"
import { OutputContract } from "./components/OutputContract"
import { ExportStudioPreview } from "./components/ExportStudioPreview"
import { FeatureMatrix } from "./components/FeatureMatrix"
import { PersonaShowcase } from "./components/PersonaShowcase"
import { McpShowcase } from "./components/McpShowcase"
import { InstallSection } from "./components/InstallSection"
import { FaqSection } from "./components/FaqSection"
import { Footer } from "./components/Footer"
import { InstallModal } from "./components/InstallModal"

export function App() {
  const [installModalOpen, setInstallModalOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 selection:bg-cyan-500/20 selection:text-cyan-300 font-sans antialiased overflow-x-hidden">
      {/* Top Fixed Header */}
      <Header onOpenInstallModal={() => setInstallModalOpen(true)} />

      {/* Main Content Sections */}
      <main>
        {/* 1. Hero with Animated Terminal Demo */}
        <Hero onOpenInstallModal={() => setInstallModalOpen(true)} />

        {/* 2. Interactive Documentation Type Selector */}
        <DocTypeSelector />

        {/* 3. The Four-Part Output Contract Visualizer */}
        <OutputContract />

        {/* 4. Multi-Target Export Studio Preview */}
        <ExportStudioPreview />

        {/* 5. Honest Capability Feature Matrix */}
        <FeatureMatrix />

        {/* 6. Persona Pathways (AI, Offline, DevOps) */}
        <PersonaShowcase />

        {/* 7. FastMCP AI Agent Server */}
        <McpShowcase />

        {/* 8. Installation & Quickstart Options */}
        <InstallSection />

        {/* 9. Frequently Asked Questions */}
        <FaqSection />
      </main>

      {/* Footer */}
      <Footer />

      {/* Quick Install Popup Modal */}
      <InstallModal
        isOpen={installModalOpen}
        onClose={() => setInstallModalOpen(false)}
      />
    </div>
  )
}

export default App
