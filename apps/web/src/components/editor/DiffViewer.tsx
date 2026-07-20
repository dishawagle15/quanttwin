import { CodeViewer } from "@/components/editor/CodeViewer";

type DiffViewerProps = {
  originalCode: string;
  modernizedCode: string;
};

export function DiffViewer({
  originalCode,
  modernizedCode,
}: DiffViewerProps): React.JSX.Element {
  return (
    <div className="flex h-full min-w-0 bg-background">
      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-10 shrink-0 items-center border-b border-border px-4">
          <h2 className="text-xs font-medium text-text-secondary">Original Legacy Code</h2>
        </header>
        <div className="min-h-0 flex-1">
          <CodeViewer code={originalCode} language="cpp" isLoading={false} />
        </div>
      </section>

      <section className="flex min-w-0 flex-1 flex-col border-l border-border">
        <header className="flex h-10 shrink-0 items-center border-b border-border px-4">
          <h2 className="text-xs font-medium text-text-secondary">Vectorized Python</h2>
        </header>
        <div className="min-h-0 flex-1">
          <CodeViewer code={modernizedCode} language="python" isLoading={false} />
        </div>
      </section>
    </div>
  );
}
