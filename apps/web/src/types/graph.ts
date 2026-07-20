export interface GraphNodeData {
  label: string;
  node_type: "file" | "function";
  file_path: string;
}

export interface GraphNode {
  id: string;
  type: string;
  position: {
    x: number;
    y: number;
  };
  data: GraphNodeData;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  animated: boolean;
}
