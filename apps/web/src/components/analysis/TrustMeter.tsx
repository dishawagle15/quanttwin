import { Check } from "lucide-react";

type TrustMeterProps = {
  score: number;
  evidence: string[];
  reasoning: string;
  limitations: string;
};

export function TrustMeter({
  score,
  evidence,
  reasoning,
  limitations,
}: TrustMeterProps): React.JSX.Element {
  const normalizedScore = Math.max(0, Math.min(100, score));
  const isHighConfidence = normalizedScore >= 80;
  const meterColor = isHighConfidence ? "bg-emerald-500" : "bg-amber-400";
  const scoreColor = isHighConfidence ? "text-emerald-500" : "text-amber-400";

  return (
    <section className="border-t border-border pt-4">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="text-sm font-medium text-text-primary">Trust Meter</h3>
        <span className={`font-mono text-sm ${scoreColor}`}>
          {normalizedScore.toFixed(0)}%
        </span>
      </div>

      <div className="mt-3 h-1 overflow-hidden rounded-full bg-border">
        <div
          className={`h-full rounded-full transition-[width] ${meterColor}`}
          style={{ width: `${normalizedScore}%` }}
        />
      </div>

      <div className="mt-4 space-y-4">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-text-secondary">
            Evidence
          </p>
          <ul className="mt-2 space-y-1.5">
            {evidence.map((item) => (
              <li key={item} className="flex gap-2 text-xs leading-5 text-text-secondary">
                <Check className="mt-0.5 size-3.5 shrink-0 text-text-primary" aria-hidden="true" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-text-secondary">
            Reasoning
          </p>
          <p className="mt-1.5 text-xs leading-5 text-text-secondary">{reasoning}</p>
        </div>

        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-text-secondary">
            Limitations
          </p>
          <p className="mt-1.5 text-xs leading-5 text-text-secondary">{limitations}</p>
        </div>
      </div>
    </section>
  );
}
