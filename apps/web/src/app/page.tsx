"use client";

import { useRef, useState } from "react";

import { DependencyGraph } from "@/components/graph/DependencyGraph";
import { CodeViewer, type CodeLanguage } from "@/components/editor/CodeViewer";
import { DiffViewer } from "@/components/editor/DiffViewer";
import { InspectorPanel } from "@/components/layout/InspectorPanel";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import {
  WorkspaceTabs,
  type WorkspaceTab,
} from "@/components/layout/WorkspaceTabs";
import type { GraphEdge, GraphNode } from "@/types/graph";
import {
  explainFunction,
  generateDocs,
  modernizeCode,
  recognizePattern,
  type ExplanationResponse,
  type PatternResponse,
} from "@/lib/api";

const mockNodes: GraphNode[] = [
  {
    id: "file::pricing_engine.py",
    type: "default",
    position: { x: 0, y: 120 },
    data: {
      label: "pricing_engine.py",
      node_type: "file",
      file_path: "pricing_engine.py",
    },
  },
  {
    id: "pricing_engine.py::monte_carlo_price",
    type: "default",
    position: { x: 300, y: 0 },
    data: {
      label: "monte_carlo_price",
      node_type: "function",
      file_path: "pricing_engine.py",
    },
  },
  {
    id: "pricing_engine.py::discount_cashflows",
    type: "default",
    position: { x: 300, y: 220 },
    data: {
      label: "discount_cashflows",
      node_type: "function",
      file_path: "pricing_engine.py",
    },
  },
];

const mockEdges: GraphEdge[] = [
  {
    id: "file::pricing_engine.py-pricing_engine.py::monte_carlo_price",
    source: "file::pricing_engine.py",
    target: "pricing_engine.py::monte_carlo_price",
    animated: true,
  },
  {
    id: "file::pricing_engine.py-pricing_engine.py::discount_cashflows",
    source: "file::pricing_engine.py",
    target: "pricing_engine.py::discount_cashflows",
    animated: true,
  },
  {
    id: "pricing_engine.py::monte_carlo_price-pricing_engine.py::discount_cashflows",
    source: "pricing_engine.py::monte_carlo_price",
    target: "pricing_engine.py::discount_cashflows",
    animated: true,
  },
];

const mockEulerMaruyamaCode = `#include <cmath>
#include <random>
#include <vector>

std::vector<double> simulate_gbm(
    double spot,
    double drift,
    double volatility,
    double dt,
    int steps
) {
    std::mt19937 generator(42);
    std::normal_distribution<double> normal(0.0, 1.0);
    std::vector<double> path{spot};

    for (int step = 0; step < steps; ++step) {
        const double shock = normal(generator) * std::sqrt(dt);
        const double increment = drift * dt + volatility * shock;
        path.push_back(path.back() * (1.0 + increment));
    }

    return path;
}`;

export default function HomePage(): React.JSX.Element {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("graph");
  const [selectedCode, setSelectedCode] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState<CodeLanguage>("cpp");
  const [explanationData, setExplanationData] = useState<ExplanationResponse | null>(null);
  const [patternData, setPatternData] = useState<PatternResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [modernizedCode, setModernizedCode] = useState("");
  const [markdownDocs, setMarkdownDocs] = useState("");
  const [isModernizing, setIsModernizing] = useState(false);
  const [isGeneratingDocs, setIsGeneratingDocs] = useState(false);
  const analysisRequestId = useRef(0);

  const handleNodeClick = async (node: GraphNode): Promise<void> => {
    setSelectedNode(node);
    setIsAnalyzing(true);
    setExplanationData(null);
    setPatternData(null);

    const requestId = analysisRequestId.current + 1;
    analysisRequestId.current = requestId;

    if (node.data.node_type === "function") {
      setSelectedCode(mockEulerMaruyamaCode);
      setSelectedLanguage("cpp");
      setActiveTab("code");
    }

    try {
      const [explanation, pattern] = await Promise.all([
        explainFunction(node.data.label, mockEulerMaruyamaCode),
        recognizePattern(mockEulerMaruyamaCode),
      ]);
      if (analysisRequestId.current === requestId) {
        setExplanationData(explanation);
        setPatternData(pattern);
      }
    } catch {
      if (analysisRequestId.current === requestId) {
        setExplanationData(null);
        setPatternData(null);
      }
    } finally {
      if (analysisRequestId.current === requestId) {
        setIsAnalyzing(false);
      }
    }
  };

  const handleModernize = async (): Promise<void> => {
    if (!selectedCode) {
      return;
    }

    setIsModernizing(true);
    try {
      const response = await modernizeCode(selectedCode);
      setModernizedCode(response.modernized_code);
      setActiveTab("modernize");
    } catch {
      setModernizedCode("# Unable to modernize the selected code.");
      setActiveTab("modernize");
    } finally {
      setIsModernizing(false);
    }
  };

  const handleDocs = async (): Promise<void> => {
    if (!selectedCode) {
      return;
    }

    setIsGeneratingDocs(true);
    try {
      const response = await generateDocs(selectedCode, {
        pattern_name: patternData?.pattern_name ?? null,
        latex_equation: patternData?.latex_equation ?? null,
        mathematical_intuition: explanationData?.mathematical_intuition ?? null,
      });
      setMarkdownDocs(response.markdown_docs);
      setActiveTab("docs");
    } catch {
      setMarkdownDocs("# Documentation unavailable\n\nPlease retry the request.");
      setActiveTab("docs");
    } finally {
      setIsGeneratingDocs(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <TopBar />
        <WorkspaceTabs activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="min-h-0 flex-1 overflow-hidden">
          {activeTab === "graph" ? (
            <DependencyGraph
              nodes={mockNodes}
              edges={mockEdges}
              onNodeClick={handleNodeClick}
            />
          ) : activeTab === "code" ? (
            <CodeViewer
              code={selectedCode || "// Select a function node to view its source code."}
              language={selectedLanguage}
              isLoading={false}
            />
          ) : activeTab === "modernize" ? (
            <DiffViewer
              originalCode={selectedCode || mockEulerMaruyamaCode}
              modernizedCode={modernizedCode || "# Modernized code will appear here."}
            />
          ) : (
            <CodeViewer
              code={markdownDocs || "# Documentation\n\nGenerate documentation for a selected function."}
              language="markdown"
              isLoading={false}
            />
          )}
        </main>
      </div>

      <InspectorPanel
        isLoading={isAnalyzing}
        isModernizing={isModernizing}
        isGeneratingDocs={isGeneratingDocs}
        explanation={explanationData}
        pattern={patternData}
        onModernizeClick={handleModernize}
        onDocsClick={handleDocs}
      />
    </div>
  );
}
