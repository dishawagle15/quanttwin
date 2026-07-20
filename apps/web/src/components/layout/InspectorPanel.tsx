import { BlockMath } from "react-katex";
import { LoaderCircle } from "lucide-react";

import "katex/dist/katex.min.css";

import { TrustMeter } from "@/components/analysis/TrustMeter";
import type { ExplanationResponse, PatternResponse } from "@/lib/api";

type InspectorPanelProps = {
  isLoading: boolean;
  isModernizing: boolean;
  isGeneratingDocs: boolean;
  explanation: ExplanationResponse | null;
  pattern: PatternResponse | null;
  onModernizeClick: () => void;
  onDocsClick: () => void;
};

function InspectorSkeleton(): React.JSX.Element {
  return (
    <div className="space-y-4 p-4" aria-label="Loading AI analysis">
      {["understanding", "pattern", "trust"].map((section) => (
        <div key={section} className="animate-pulse border border-border bg-card p-4">
          <div className="h-3 w-24 rounded bg-border" />
          <div className="mt-4 h-3 w-full rounded bg-border" />
          <div className="mt-2 h-3 w-4/5 rounded bg-border" />
        </div>
      ))}
    </div>
  );
}

export function InspectorPanel({
  isLoading,
  isModernizing,
  isGeneratingDocs,
  explanation,
  pattern,
  onModernizeClick,
  onDocsClick,
}: InspectorPanelProps): React.JSX.Element {
  const limitations = pattern?.limitations.join(" ") || explanation?.limitations || "—";

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-border bg-background">
      <div className="flex h-14 items-center border-b border-border px-5">
        <h2 className="text-sm font-medium text-text-primary">Inspector</h2>
      </div>

      {isLoading ? (
        <InspectorSkeleton />
      ) : (
        <div className="space-y-5 overflow-y-auto p-5">
          <section>
            <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-text-secondary">
              Code Understanding
            </p>
            {explanation ? (
              <>
                <p className="mt-2 text-sm leading-6 text-text-primary">
                  {explanation.summary}
                </p>
                <p className="mt-3 text-xs leading-5 text-text-secondary">
                  {explanation.mathematical_intuition}
                </p>
              </>
            ) : (
              <p className="mt-2 text-xs leading-5 text-text-secondary">
                Select a graph node to generate an explanation.
              </p>
            )}
          </section>

          {pattern && (
            <section className="border-t border-border pt-5">
              <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-text-secondary">
                Mathematical Pattern
              </p>
              <h3 className="mt-2 text-sm font-medium text-text-primary">
                {pattern.pattern_name}
              </h3>
              {pattern.latex_equation && (
                <div className="mt-3 overflow-x-auto border border-border bg-card px-3 py-4 text-text-primary">
                  <BlockMath math={pattern.latex_equation} />
                </div>
              )}
            </section>
          )}

          {pattern && (
            <TrustMeter
              score={pattern.confidence_score}
              evidence={pattern.evidence_list}
              reasoning={pattern.reasoning}
              limitations={limitations}
            />
          )}
        </div>
      )}

      <div className="mt-auto space-y-2 border-t border-border p-4">
        <button
          type="button"
          onClick={onModernizeClick}
          disabled={isModernizing || isGeneratingDocs}
          className="flex w-full items-center justify-center gap-2 border border-border bg-card px-3 py-2 text-sm text-text-primary transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isModernizing && (
            <LoaderCircle className="size-3.5 animate-spin" aria-hidden="true" />
          )}
          Modernize Code
        </button>
        <button
          type="button"
          onClick={onDocsClick}
          disabled={isModernizing || isGeneratingDocs}
          className="flex w-full items-center justify-center gap-2 border border-border bg-card px-3 py-2 text-sm text-text-primary transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isGeneratingDocs && (
            <LoaderCircle className="size-3.5 animate-spin" aria-hidden="true" />
          )}
          Generate Docs
        </button>
      </div>
    </aside>
  );
}
