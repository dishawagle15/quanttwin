import { ChevronRight, Upload } from "lucide-react";

export function TopBar(): React.JSX.Element {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-background px-5">
      <div className="flex min-w-0 items-center gap-2 text-sm">
        <span className="truncate text-text-secondary">Workspace</span>
        <ChevronRight className="size-3.5 shrink-0 text-text-secondary" aria-hidden="true" />
        <span className="truncate font-medium text-text-primary">Dashboard</span>
      </div>

      <button
        type="button"
        className="inline-flex shrink-0 items-center gap-2 rounded border border-border bg-card px-3 py-1.5 text-sm font-medium text-text-primary transition-colors hover:border-text-secondary"
      >
        <Upload className="size-3.5" aria-hidden="true" />
        Upload Repository
      </button>
    </header>
  );
}
