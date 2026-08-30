'use client';

import React from 'react';
import { Check, X, Sparkles } from 'lucide-react';
import { MATRIX_ROWS } from '@/data/showcaseData';
import { VERSION } from '../lib/version';

export function FeatureMatrix() {
  return (
    <section id="matrix" className="border-b border-border bg-background py-16 scroll-mt-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="space-y-3 mb-12">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-primary font-bold tracking-widest uppercase">
              Capability Comparison
            </span>
            <div className="h-px flex-1 bg-border/60" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Why DocHarvest Outperforms Raw Scrapers &amp; Cloud APIs
          </h2>
          <p className="text-sm text-muted-foreground font-mono max-w-2xl">
            Compare DocHarvest against raw scrapers and proprietary cloud services.
          </p>
        </div>

        {/* Feature Comparison Table */}
        <div className="border border-border rounded-xl bg-card overflow-x-auto shadow-xl">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/80">
                <th className="p-4 sm:p-5 text-foreground font-bold w-1/2">
                  Engine Capability
                </th>
                <th className="p-4 sm:p-5 text-cyan font-bold bg-cyan/10 text-center">
                  DocHarvest v{VERSION}
                </th>
                <th className="p-4 sm:p-5 text-muted-foreground font-semibold text-center hidden sm:table-cell">
                  Raw Scrapers (curl/Scrapy)
                </th>
                <th className="p-4 sm:p-5 text-muted-foreground font-semibold text-center">
                  Cloud Reader APIs
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-border/60">
              {MATRIX_ROWS.map((row, index) => (
                <tr key={index} className="hover:bg-secondary/30 transition-colors">
                  <td className="p-4 sm:p-5">
                    <div className="font-bold text-foreground">{row.feature}</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5 font-normal">
                      {row.detail}
                    </div>
                  </td>
                  
                  {/* DocHarvest Column */}
                  <td className="p-4 sm:p-5 text-center bg-card/50">
                    {row.docharvest ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-card/50 text-emerald">
                        <Check className="h-4 w-4" />
                      </div>
                    ) : (
                      <X className="h-4 w-4 text-cyan/50 mx-auto" />
                    )}
                  </td>

                  {/* Raw Scrapers Column */}
                  <td className="p-4 sm:p-5 text-center hidden sm:table-cell">
                    {row.rawScrapers === true ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-card/50 text-emerald">
                        <Check className="h-4 w-4" />
                      </div>
                    ) : (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-card/50 text-cyan/50">
                        <X className="h-4 w-4" />
                      </div>
                    )}
                  </td>

                  {/* Cloud APIs Column */}
                  <td className="p-4 sm:p-5 text-center">
                    {row.cloudApis === true ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-card/50 text-emerald">
                        <Check className="h-4 w-4" />
                      </div>
                    ) : row.cloudApis === false ? (
                      <div className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-card/50 text-cyan/50">
                        <X className="h-4 w-4" />
                      </div>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-card/50 text-accent border border-border/50 font-bold">
                        {row.cloudApis}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </section>
  );
}
