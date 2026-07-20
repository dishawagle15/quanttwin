const analysisApiUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1/analysis";

export interface ExplanationResponse {
  summary: string;
  inputs: string;
  outputs: string;
  computational_complexity: string;
  mathematical_intuition: string;
  limitations: string;
}

export interface PatternResponse {
  pattern_name: string;
  confidence_score: number;
  latex_equation: string | null;
  evidence_list: string[];
  reasoning: string;
  limitations: string[];
}

export interface ModernizeResponse {
  modernized_code: string;
  improvements: string[];
}

export interface DocsResponse {
  markdown_docs: string;
}

async function postAnalysis<TResponse>(
  endpoint: string,
  body: Record<string, unknown>,
): Promise<TResponse> {
  const response = await fetch(`${analysisApiUrl}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorBody = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(errorBody?.detail ?? "Unable to complete AI analysis.");
  }

  return (await response.json()) as TResponse;
}

export async function explainFunction(
  functionName: string,
  code: string,
): Promise<ExplanationResponse> {
  return postAnalysis<ExplanationResponse>("/explain", {
    function_name: functionName,
    function_code: code,
  });
}

export async function recognizePattern(code: string): Promise<PatternResponse> {
  return postAnalysis<PatternResponse>("/recognize-pattern", {
    function_code: code,
  });
}

export async function modernizeCode(code: string): Promise<ModernizeResponse> {
  return postAnalysis<ModernizeResponse>("/modernize", { code });
}

export async function generateDocs(
  code: string,
  mathContext: Record<string, unknown>,
): Promise<DocsResponse> {
  return postAnalysis<DocsResponse>("/document", {
    code,
    math_context: mathContext,
  });
}
