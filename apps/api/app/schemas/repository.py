"""Schemas describing a parsed source repository and AI-derived patterns."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepositorySchema(BaseModel):
    """Base schema that rejects undeclared fields at the API boundary."""

    model_config = ConfigDict(extra="forbid")


class VariableNode(RepositorySchema):
    """A variable declaration extracted from a source file."""

    name: Annotated[str, Field(min_length=1)]
    type: str | None = None
    line_number: Annotated[int, Field(ge=1)]
    mathematical_role: str | None = None


class FunctionNode(RepositorySchema):
    """A function or method declaration extracted from a source file."""

    name: Annotated[str, Field(min_length=1)]
    parameters: list[str] = Field(default_factory=list)
    return_type: str | None = None
    start_line: Annotated[int, Field(ge=1)]
    end_line: Annotated[int, Field(ge=1)]
    body_snippet: str = ""
    calls: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_line_range(self) -> "FunctionNode":
        """Ensure the function's ending line is not before its start line."""

        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class ClassNode(RepositorySchema):
    """A class declaration and its directly declared members."""

    name: Annotated[str, Field(min_length=1)]
    methods: list[FunctionNode] = Field(default_factory=list)
    properties: list[VariableNode] = Field(default_factory=list)


class CodeFile(RepositorySchema):
    """The parsed representation of one source file."""

    file_path: Annotated[str, Field(min_length=1)]
    language: Annotated[str, Field(min_length=1)]
    classes: list[ClassNode] = Field(default_factory=list)
    functions: list[FunctionNode] = Field(default_factory=list)
    variables: list[VariableNode] = Field(default_factory=list)
    raw_content: str


class SDEPattern(RepositorySchema):
    """Strict structured output for stochastic differential equation analysis."""

    pattern_name: Annotated[str, Field(min_length=1)]
    confidence_score: Annotated[float, Field(ge=0, le=100)]
    latex_equation: str | None = None
    evidence_list: list[str] = Field(default_factory=list)
    reasoning: Annotated[str, Field(min_length=1)]
    limitations: list[str] = Field(default_factory=list)
