import { Braces, FileCode } from "lucide-react";
import { Handle, Position, type NodeProps } from "@xyflow/react";

import type { GraphNodeData } from "@/types/graph";

export function CustomNode({ data }: NodeProps): React.JSX.Element {
  const nodeData = data as GraphNodeData;
  const isFile = nodeData.node_type === "file";
  const Icon = isFile ? FileCode : Braces;

  return (
    <div className="min-w-44 rounded border border-border bg-card px-3 py-2.5 text-text-primary">
      <Handle
        type="target"
        position={Position.Left}
        className="!size-1.5 !border-0 !bg-text-secondary"
      />
      <div className="flex items-center gap-2">
        <Icon className="size-3.5 shrink-0 text-text-secondary" strokeWidth={1.75} />
        <div className="min-w-0">
          <p className="truncate text-sm font-medium">{nodeData.label}</p>
          <p className="mt-0.5 truncate font-mono text-[10px] text-text-secondary">
            {isFile ? nodeData.file_path : "function"}
          </p>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!size-1.5 !border-0 !bg-text-secondary"
      />
    </div>
  );
}
