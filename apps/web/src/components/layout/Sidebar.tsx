import {
  BookOpen,
  Boxes,
  ChartNoAxesCombined,
  FolderGit2,
  LayoutDashboard,
  type LucideIcon,
} from "lucide-react";

type NavigationItem = {
  label: string;
  icon: LucideIcon;
  isActive?: boolean;
};

type NavigationSection = {
  label: string;
  items: NavigationItem[];
};

const navigationSections: NavigationSection[] = [
  {
    label: "Workspace",
    items: [
      { label: "Dashboard", icon: LayoutDashboard, isActive: true },
      { label: "Repository", icon: FolderGit2 },
      { label: "Dependency Graph", icon: Boxes },
    ],
  },
  {
    label: "Analysis",
    items: [
      { label: "Recognized Models", icon: ChartNoAxesCombined },
      { label: "Documentation", icon: BookOpen },
    ],
  },
];

export function Sidebar(): React.JSX.Element {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-border bg-background">
      <div className="flex h-14 items-center gap-2.5 border-b border-border px-5">
        <div className="flex size-6 items-center justify-center rounded bg-accent font-mono text-xs font-semibold text-background">
          Q
        </div>
        <span className="text-sm font-semibold tracking-tight text-text-primary">
          QuantTwin
        </span>
      </div>

      <nav className="flex-1 space-y-7 overflow-y-auto px-3 py-5" aria-label="Primary navigation">
        {navigationSections.map((section) => (
          <div key={section.label}>
            <p className="px-2 pb-2 text-[11px] font-medium uppercase tracking-[0.14em] text-text-secondary">
              {section.label}
            </p>
            <ul className="space-y-0.5">
              {section.items.map((item) => (
                <li key={item.label}>
                  <button
                    type="button"
                    className={`flex w-full items-center gap-2.5 rounded px-2 py-2 text-left text-sm transition-colors ${
                      item.isActive
                        ? "bg-card text-text-primary"
                        : "text-text-secondary hover:bg-card hover:text-text-primary"
                    }`}
                  >
                    <item.icon className="size-4" strokeWidth={1.75} aria-hidden="true" />
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
