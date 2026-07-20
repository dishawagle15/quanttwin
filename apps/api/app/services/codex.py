"""OpenAI-powered analysis services for quantitative source code."""

import json
from typing import Any

import openai

from app.config import get_settings
from app.schemas.repository import SDEPattern

_FUNCTION_ANALYSIS_PROMPT = """You are an expert quantitative engineer. Analyze this
function. Return a JSON object with: summary, inputs, outputs,
computational_complexity, mathematical_intuition, and limitations."""

_PATTERN_RECOGNITION_PROMPT = """You are a strict pattern recognition engine for
quantitative finance.

Supported models: Geometric Brownian Motion, Black-Scholes,
Ornstein-Uhlenbeck, CIR, Euler-Maruyama, Monte Carlo.

If the code perfectly matches a supported model, provide the pattern_name and
exact LaTeX equation. If confidence is below 80% or it uses proprietary logic,
you MUST set pattern_name to 'Custom stochastic process', latex_equation to
null, and confidence_score appropriately. Always provide evidence_list,
reasoning, and limitations for the Trust Meter."""

_MODERNIZATION_PROMPT = """You are an expert quantitative software architect.
Translate the provided legacy discrete quantitative loop (e.g., C++ or Fortran)
into modern, highly optimized, vectorized Python using NumPy and SciPy. Ensure
type hints and docstrings are included. Return a JSON object with keys
modernized_code (string) and improvements (list of strings)."""

_DOCUMENTATION_PROMPT = """Generate professional Markdown API documentation for
the provided quantitative function. Include its mathematical theory, inputs,
outputs, and an example usage. Return a JSON object with key markdown_docs
(string)."""


class CodexAnalyzer:
    """Run structured OpenAI analysis over quantitative functions."""

    def __init__(self) -> None:
        """Initialize an asynchronous OpenAI client with the configured API key."""

        settings = get_settings()
        if settings.openai_api_key is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        self._model = settings.openai_model
        self._client = openai.AsyncClient(
            api_key=settings.openai_api_key.get_secret_value(),
        )

    async def analyze_function(
        self,
        function_name: str,
        function_code: str,
    ) -> dict[str, Any]:
        """Return a JSON-mode explanation of a function and its mathematics."""

        completion = await self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _FUNCTION_ANALYSIS_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Function name: {function_name}\n\n"
                        f"Function code:\n```\n{function_code}\n```"
                    ),
                },
            ],
        )
        content = completion.choices[0].message.content
        if content is None:
            raise ValueError("The model returned an empty analysis response.")

        analysis = json.loads(content)
        if not isinstance(analysis, dict):
            raise ValueError("The model analysis response was not a JSON object.")
        return analysis

    async def recognize_pattern(self, function_code: str) -> SDEPattern:
        """Recognize known stochastic models with Pydantic structured outputs."""

        completion = await self._client.beta.chat.completions.parse(
            model=self._model,
            response_format=SDEPattern,
            messages=[
                {"role": "system", "content": _PATTERN_RECOGNITION_PROMPT},
                {
                    "role": "user",
                    "content": f"Analyze this function:\n```\n{function_code}\n```",
                },
            ],
        )
        pattern = completion.choices[0].message.parsed
        if pattern is None:
            raise ValueError("The model did not return a structured SDE pattern.")
        return pattern

    async def modernize_code(self, code: str) -> dict[str, Any]:
        """Translate legacy quantitative code into vectorized Python."""

        result = await self._json_completion(_MODERNIZATION_PROMPT, code)
        modernized_code = result.get("modernized_code")
        improvements = result.get("improvements")
        if not isinstance(modernized_code, str):
            raise ValueError("The modernization response did not include code.")
        if not isinstance(improvements, list) or not all(
            isinstance(item, str) for item in improvements
        ):
            raise ValueError("The modernization response had invalid improvements.")

        return {
            "modernized_code": modernized_code,
            "improvements": improvements,
        }

    async def generate_documentation(
        self,
        code: str,
        math_context: dict[str, Any],
    ) -> dict[str, str]:
        """Generate Markdown API documentation for quantitative source code."""

        context = json.dumps(math_context, ensure_ascii=False)
        result = await self._json_completion(
            _DOCUMENTATION_PROMPT,
            f"Mathematical context:\n{context}\n\nFunction code:\n{code}",
        )
        markdown_docs = result.get("markdown_docs")
        if not isinstance(markdown_docs, str):
            raise ValueError("The documentation response did not include Markdown.")
        return {"markdown_docs": markdown_docs}

    async def _json_completion(
        self,
        system_prompt: str,
        user_content: str,
    ) -> dict[str, Any]:
        """Call Chat Completions JSON mode and validate an object response."""

        completion = await self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        content = completion.choices[0].message.content
        if content is None:
            raise ValueError("The model returned an empty response.")

        result = json.loads(content)
        if not isinstance(result, dict):
            raise ValueError("The model response was not a JSON object.")
        return result
