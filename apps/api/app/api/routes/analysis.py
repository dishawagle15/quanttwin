"""HTTP endpoints for OpenAI-powered code analysis."""

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from fastapi import APIRouter, HTTPException, status
from openai import APIConnectionError, APIError, RateLimitError
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.repository import SDEPattern
from app.services.codex import CodexAnalyzer

router = APIRouter()
AnalysisResponse = TypeVar("AnalysisResponse")


class FunctionExplanationRequest(BaseModel):
    """Payload for general function analysis."""

    model_config = ConfigDict(extra="forbid")

    function_name: str = Field(min_length=1)
    function_code: str = Field(min_length=1)


class PatternRecognitionRequest(BaseModel):
    """Payload for stochastic-pattern recognition."""

    model_config = ConfigDict(extra="forbid")

    function_code: str = Field(min_length=1)


class ModernizationRequest(BaseModel):
    """Payload for legacy-code modernization."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)


class DocumentationRequest(BaseModel):
    """Payload for Markdown documentation generation."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    math_context: dict[str, Any]


@router.post("/explain")
async def explain_function(
    request: FunctionExplanationRequest,
) -> dict[str, Any]:
    """Explain a function's behavior and quantitative intuition."""

    analyzer = _get_analyzer()
    return await _run_openai_request(
        lambda: analyzer.analyze_function(
            function_name=request.function_name,
            function_code=request.function_code,
        )
    )


@router.post("/recognize-pattern", response_model=SDEPattern)
async def recognize_pattern(request: PatternRecognitionRequest) -> SDEPattern:
    """Recognize a supported stochastic process from function source code."""

    analyzer = _get_analyzer()
    return await _run_openai_request(
        lambda: analyzer.recognize_pattern(request.function_code),
    )


@router.post("/modernize")
async def modernize_code(request: ModernizationRequest) -> dict[str, Any]:
    """Translate legacy quantitative code into vectorized Python."""

    analyzer = _get_analyzer()
    return await _run_openai_request(lambda: analyzer.modernize_code(request.code))


@router.post("/document")
async def generate_documentation(
    request: DocumentationRequest,
) -> dict[str, str]:
    """Generate Markdown API documentation for selected source code."""

    analyzer = _get_analyzer()
    return await _run_openai_request(
        lambda: analyzer.generate_documentation(
            code=request.code,
            math_context=request.math_context,
        )
    )


async def _run_openai_request(
    operation: Callable[[], Awaitable[AnalysisResponse]],
) -> AnalysisResponse:
    """Translate OpenAI transport and response failures into HTTP errors."""

    try:
        return await operation()
    except RateLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI rate limit reached. Please retry shortly.",
        ) from error
    except APIConnectionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to the OpenAI service.",
        ) from error
    except APIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI could not complete the analysis request.",
        ) from error
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI returned an invalid response.",
        ) from error


def _get_analyzer() -> CodexAnalyzer:
    """Create an analyzer or provide a clear configuration error."""

    try:
        return CodexAnalyzer()
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI analysis is not configured for this environment.",
        ) from error
