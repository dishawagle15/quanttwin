export type WorkspaceTab = "graph" | "code" | "modernize" | "docs";

type WorkspaceTabsProps = {
  activeTab: WorkspaceTab;
  onTabChange: (tab: WorkspaceTab) => void;
};

const tabs: { id: WorkspaceTab; label: string }[] = [
  { id: "graph", label: "Dependency Graph" },
  { id: "code", label: "Code Viewer" },
  { id: "modernize", label: "Modernize" },
  { id: "docs", label: "Documentation" },
];

export function WorkspaceTabs({
  activeTab,
  onTabChange,
}: WorkspaceTabsProps): React.JSX.Element {
  return (
    <div className="flex h-10 shrink-0 items-end border-b border-border bg-background px-5">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={`h-full border-b-2 px-3 text-sm transition-colors ${
              isActive
                ? "border-accent text-text-primary"
                : "border-transparent text-text-secondary hover:text-text-primary"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
