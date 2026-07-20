"use client";

import { useState } from "react";
import Editor, { type OnMount } from "@monaco-editor/react";
import { LoaderCircle } from "lucide-react";

export type CodeLanguage = "python" | "cpp" | "markdown";

type CodeViewerProps = {
  code: string;
  language: CodeLanguage;
  isLoading: boolean;
};

export function CodeViewer({
  code,
  language,
  isLoading,
}: CodeViewerProps): React.JSX.Element {
  const [isEditorReady, setIsEditorReady] = useState(false);

  const handleEditorMount: OnMount = () => {
    setIsEditorReady(true);
  };

  return (
    <div className="relative h-full w-full bg-background">
      <Editor
        height="100%"
        language={language}
        value={code}
        theme="vs-dark"
        onMount={handleEditorMount}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "var(--font-mono)",
          scrollBeyondLastLine: false,
          lineNumbersMinChars: 3,
          padding: { top: 16, bottom: 16 },
          wordWrap: "on",
          renderLineHighlight: "none",
          overviewRulerLanes: 0,
        }}
        loading={null}
      />

      {(isLoading || !isEditorReady) && (
        <div className="absolute inset-0 flex items-center justify-center bg-background">
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
            Loading code viewer
          </div>
        </div>
      )}
    </div>
  );
}
