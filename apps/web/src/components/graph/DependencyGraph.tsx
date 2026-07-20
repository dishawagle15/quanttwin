"use client";

import { useEffect, useMemo } from "react";
import {
  Background,
  Controls,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { CustomNode } from "@/components/graph/CustomNode";
import type { GraphEdge, GraphNode, GraphNodeData } from "@/types/graph";

type DependencyGraphProps = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick: (node: GraphNode) => void;
};

type FlowNode = Node<GraphNodeData, "custom">;

const nodeTypes = {
  custom: CustomNode,
};

function toFlowNodes(nodes: GraphNode[]): FlowNode[] {
  return nodes.map((node) => ({
    ...node,
    type: "custom",
  }));
}

function toFlowEdges(edges: GraphEdge[]): Edge[] {
  return edges.map((edge) => ({
    ...edge,
    style: { stroke: "var(--border)", strokeWidth: 1 },
  }));
}

export function DependencyGraph({
  nodes,
  edges,
  onNodeClick,
}: DependencyGraphProps): React.JSX.Element {
  const initialNodes = useMemo(() => toFlowNodes(nodes), [nodes]);
  const initialEdges = useMemo(() => toFlowEdges(edges), [edges]);
  const [flowNodes, setNodes, onNodesChange] = useNodesState<FlowNode>(initialNodes);
  const [flowEdges, setEdges, onEdgesChange] = useEdgesState<Edge>(initialEdges);

  useEffect(() => {
    setNodes(toFlowNodes(nodes));
  }, [nodes, setNodes]);

  useEffect(() => {
    setEdges(toFlowEdges(edges));
  }, [edges, setEdges]);

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(_, node) => {
          const selectedNode = nodes.find((graphNode) => graphNode.id === node.id);
          if (selectedNode) {
            onNodeClick(selectedNode);
          }
        }}
        fitView
        minZoom={0.35}
        maxZoom={1.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="var(--border)" gap={20} size={1} />
        <Controls
          showInteractive={false}
          className="!rounded !border !border-border !bg-card !shadow-none"
        />
      </ReactFlow>
    </div>
  );
}
