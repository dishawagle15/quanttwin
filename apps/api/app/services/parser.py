"""Tree-sitter parsing and structural extraction for supported source files."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from tree_sitter import Language, Node, Parser, Query, Tree
from tree_sitter_languages import get_language

from app.schemas.repository import ClassNode, CodeFile, FunctionNode, VariableNode

LOGGER = logging.getLogger(__name__)
ExtractedNode = TypeVar("ExtractedNode")


@dataclass(frozen=True)
class _ExtractedFunction:
    """A function model paired with its AST node for containment checks."""

    node: Node
    model: FunctionNode


@dataclass(frozen=True)
class _ExtractedClass:
    """A class model identity paired with its AST node."""

    node: Node
    name: str


@dataclass(frozen=True)
class _ExtractedVariable:
    """A variable model paired with its AST node for containment checks."""

    node: Node
    model: VariableNode


class TreeSitterParser:
    """Parse Python and C++ source files into QuantTwin repository schemas."""

    _LANGUAGE_BY_EXTENSION: dict[str, str] = {
        ".py": "python",
        ".c": "cpp",
        ".cc": "cpp",
        ".cpp": "cpp",
        ".cxx": "cpp",
        ".h": "cpp",
        ".hh": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
    }
    _SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(_LANGUAGE_BY_EXTENSION)
    _QUERY_SOURCES: dict[str, dict[str, str]] = {
        "python": {
            "functions": """
                (function_definition
                    name: (identifier) @function.name) @function.definition
            """,
            "classes": """
                (class_definition
                    name: (identifier) @class.name) @class.definition
            """,
            "variables": """
                [
                    (assignment left: (identifier) @variable.name)
                    (annotated_assignment left: (identifier) @variable.name)
                ]
            """,
            "calls": """
                [
                    (call function: (identifier) @call.name)
                    (call function: (attribute attribute: (identifier) @call.name))
                ]
            """,
        },
        "cpp": {
            "functions": """
                (function_definition
                    declarator: (function_declarator
                        declarator: (identifier) @function.name)) @function.definition
            """,
            "classes": """
                (class_specifier
                    name: (type_identifier) @class.name) @class.definition
            """,
            "variables": """
                [
                    (declaration declarator: (identifier) @variable.name)
                    (declaration
                        declarator: (init_declarator
                            declarator: (identifier) @variable.name))
                ]
            """,
            "calls": """
                [
                    (call_expression function: (identifier) @call.name)
                    (call_expression
                        function: (field_expression
                            field: (field_identifier) @call.name))
                ]
            """,
        },
    }

    def __init__(self) -> None:
        """Load grammars, configure parsers, and compile extraction queries."""

        self._languages: dict[str, Language] = {
            "python": get_language("python"),
            "cpp": get_language("cpp"),
        }
        self._parsers: dict[str, Parser] = {}
        self._queries: dict[str, dict[str, Query]] = {}

        for language_name, language in self._languages.items():
            parser = Parser()
            parser.set_language(language)
            self._parsers[language_name] = parser
            self._queries[language_name] = {
                query_name: language.query(query_source)
                for query_name, query_source in self._QUERY_SOURCES[language_name].items()
            }

    def parse_file(self, file_path: str, raw_content: str) -> CodeFile:
        """Parse a file and extract its structural nodes without failing the run."""

        language = self._detect_language(file_path)
        source_bytes = raw_content.encode("utf-8")

        try:
            tree = self._parsers[language].parse(source_bytes)
        except Exception:
            LOGGER.exception("Unable to parse source file: %s", file_path)
            return CodeFile(
                file_path=file_path,
                language=f"{language}-partial",
                raw_content=raw_content,
            )

        extracted_classes = self._safe_extract(
            "classes",
            file_path,
            lambda: self._extract_classes(tree, language, source_bytes),
        )
        extracted_functions = self._safe_extract(
            "functions",
            file_path,
            lambda: self._extract_functions(tree, language, source_bytes),
        )
        extracted_variables = self._safe_extract(
            "variables",
            file_path,
            lambda: self._extract_variables(tree, language, source_bytes),
        )

        classes = self._build_classes(
            extracted_classes,
            extracted_functions,
            extracted_variables,
        )
        methods = {
            self._node_key(function.node)
            for class_node in extracted_classes
            for function in extracted_functions
            if self._contains(class_node.node, function.node)
        }
        functions = [
            function.model
            for function in extracted_functions
            if self._node_key(function.node) not in methods
        ]

        return CodeFile(
            file_path=file_path,
            language=f"{language}-partial" if tree.root_node.has_error else language,
            classes=classes,
            functions=functions,
            variables=[variable.model for variable in extracted_variables],
            raw_content=raw_content,
        )

    def parse_directory(self, directory_path: str) -> list[CodeFile]:
        """Recursively parse all supported source files below a directory."""

        root_directory = Path(directory_path).resolve()
        if not root_directory.is_dir():
            raise ValueError(f"Repository directory does not exist: {directory_path}")

        parsed_files: list[CodeFile] = []
        for source_path in sorted(root_directory.rglob("*")):
            if not source_path.is_file():
                continue
            if source_path.suffix.lower() not in self._SUPPORTED_EXTENSIONS:
                continue

            try:
                raw_content = source_path.read_text(encoding="utf-8", errors="replace")
                relative_path = source_path.relative_to(root_directory).as_posix()
                parsed_files.append(self.parse_file(relative_path, raw_content))
            except Exception:
                LOGGER.exception("Unable to process source file: %s", source_path)

        return parsed_files

    def _extract_classes(
        self,
        tree: Tree,
        language: str,
        source_bytes: bytes,
    ) -> list[_ExtractedClass]:
        """Extract class declarations using the language-specific class query."""

        class_nodes = self._captured_nodes(tree.root_node, language, "classes", "class.definition")
        classes: list[_ExtractedClass] = []

        for class_node in class_nodes:
            try:
                name_node = self._first_capture_within(
                    class_node,
                    tree.root_node,
                    language,
                    "classes",
                    "class.name",
                )
                if name_node is None:
                    continue
                classes.append(
                    _ExtractedClass(
                        node=class_node,
                        name=self._node_text(name_node, source_bytes),
                    )
                )
            except Exception:
                LOGGER.exception("Unable to extract class at byte %s", class_node.start_byte)

        return classes

    def _extract_functions(
        self,
        tree: Tree,
        language: str,
        source_bytes: bytes,
    ) -> list[_ExtractedFunction]:
        """Extract functions, signatures, bodies, and calls from the AST."""

        function_nodes = self._captured_nodes(
            tree.root_node,
            language,
            "functions",
            "function.definition",
        )
        functions: list[_ExtractedFunction] = []

        for function_node in function_nodes:
            try:
                name_node = self._first_capture_within(
                    function_node,
                    tree.root_node,
                    language,
                    "functions",
                    "function.name",
                )
                if name_node is None:
                    continue

                body_node = function_node.child_by_field_name("body")
                functions.append(
                    _ExtractedFunction(
                        node=function_node,
                        model=FunctionNode(
                            name=self._node_text(name_node, source_bytes),
                            parameters=self._parameters(function_node, source_bytes),
                            return_type=self._return_type(function_node, source_bytes),
                            start_line=function_node.start_point[0] + 1,
                            end_line=function_node.end_point[0] + 1,
                            body_snippet=self._node_text(body_node, source_bytes)
                            if body_node is not None
                            else self._node_text(function_node, source_bytes),
                            calls=self._function_calls(
                                function_node,
                                language,
                                source_bytes,
                            ),
                        ),
                    ),
                )
            except Exception:
                LOGGER.exception(
                    "Unable to extract function at byte %s",
                    function_node.start_byte,
                )

        return functions

    def _extract_variables(
        self,
        tree: Tree,
        language: str,
        source_bytes: bytes,
    ) -> list[_ExtractedVariable]:
        """Extract named variable assignments and declarations from the AST."""

        variable_nodes = self._captured_nodes(
            tree.root_node,
            language,
            "variables",
            "variable.name",
        )
        variables: list[_ExtractedVariable] = []
        seen: set[tuple[str, int]] = set()

        for variable_node in variable_nodes:
            try:
                name = self._node_text(variable_node, source_bytes)
                line_number = variable_node.start_point[0] + 1
                key = (name, line_number)
                if key in seen:
                    continue
                seen.add(key)

                declaration = self._containing_declaration(variable_node)
                type_node = declaration.child_by_field_name("type") if declaration else None
                variables.append(
                    _ExtractedVariable(
                        node=variable_node,
                        model=VariableNode(
                            name=name,
                            type=self._node_text(type_node, source_bytes)
                            if type_node is not None
                            else None,
                            line_number=line_number,
                        ),
                    )
                )
            except Exception:
                LOGGER.exception(
                    "Unable to extract variable at byte %s",
                    variable_node.start_byte,
                )

        return variables

    def _build_classes(
        self,
        extracted_classes: list[_ExtractedClass],
        extracted_functions: list[_ExtractedFunction],
        extracted_variables: list[_ExtractedVariable],
    ) -> list[ClassNode]:
        """Associate contained methods and direct properties with each class."""

        classes: list[ClassNode] = []
        for extracted_class in extracted_classes:
            methods = [
                function.model
                for function in extracted_functions
                if self._contains(extracted_class.node, function.node)
            ]
            properties = [
                variable.model
                for variable in extracted_variables
                if self._contains(extracted_class.node, variable.node)
                and not any(
                    self._contains(function.node, variable.node)
                    for function in extracted_functions
                )
            ]
            classes.append(
                ClassNode(
                    name=extracted_class.name,
                    methods=methods,
                    properties=properties,
                )
            )

        return classes

    def _function_calls(
        self,
        function_node: Node,
        language: str,
        source_bytes: bytes,
    ) -> list[str]:
        """Return unique function names called from within a function body."""

        calls = self._captured_nodes(function_node, language, "calls", "call.name")
        return list(dict.fromkeys(self._node_text(call, source_bytes) for call in calls))

    @staticmethod
    def _safe_extract(
        extractor_name: str,
        file_path: str,
        extractor: Callable[[], list[ExtractedNode]],
    ) -> list[ExtractedNode]:
        """Execute one extraction stage without failing the parsed file."""

        try:
            return extractor()
        except Exception:
            LOGGER.exception("Unable to extract %s from %s", extractor_name, file_path)
            return []

    def _parameters(self, function_node: Node, source_bytes: bytes) -> list[str]:
        """Extract parameter declarations from Python or C++ function syntax."""

        parameters_node = function_node.child_by_field_name("parameters")
        if parameters_node is None:
            declarator = function_node.child_by_field_name("declarator")
            parameters_node = self._find_descendant(declarator, "parameter_list")

        if parameters_node is None:
            return []
        return [
            self._node_text(parameter, source_bytes)
            for parameter in parameters_node.named_children
        ]

    @staticmethod
    def _return_type(function_node: Node, source_bytes: bytes) -> str | None:
        """Extract the declared return type when the grammar exposes one."""

        return_type_node = function_node.child_by_field_name("return_type")
        if return_type_node is None:
            return_type_node = function_node.child_by_field_name("type")
        if return_type_node is None:
            return None
        return TreeSitterParser._node_text(return_type_node, source_bytes)

    def _captured_nodes(
        self,
        root_node: Node,
        language: str,
        query_name: str,
        capture_name: str,
    ) -> list[Node]:
        """Return unique nodes for one named capture in a compiled query."""

        captures = self._queries[language][query_name].captures(root_node)
        nodes: list[Node] = []
        seen_ranges: set[tuple[int, int]] = set()
        for node, name in captures:
            if name != capture_name:
                continue
            node_range = (node.start_byte, node.end_byte)
            if node_range not in seen_ranges:
                seen_ranges.add(node_range)
                nodes.append(node)
        return nodes

    def _first_capture_within(
        self,
        container: Node,
        root_node: Node,
        language: str,
        query_name: str,
        capture_name: str,
    ) -> Node | None:
        """Return the first matching capture whose byte range is in a container."""

        for node in self._captured_nodes(root_node, language, query_name, capture_name):
            if self._contains(container, node):
                return node
        return None

    @staticmethod
    def _containing_declaration(node: Node) -> Node | None:
        """Find the nearest assignment or declaration owning a variable node."""

        current = node.parent
        while current is not None:
            if current.type in {"assignment", "annotated_assignment", "declaration"}:
                return current
            current = current.parent
        return None

    @staticmethod
    def _find_descendant(node: Node | None, node_type: str) -> Node | None:
        """Find the first descendant with the requested grammar node type."""

        if node is None:
            return None
        if node.type == node_type:
            return node
        for child in node.children:
            result = TreeSitterParser._find_descendant(child, node_type)
            if result is not None:
                return result
        return None

    @staticmethod
    def _contains(container: Node, candidate: Node) -> bool:
        """Return whether one AST node's byte range fully contains another's."""

        return (
            container.start_byte <= candidate.start_byte
            and container.end_byte >= candidate.end_byte
        )

    @staticmethod
    def _node_key(node: Node) -> tuple[int, int]:
        """Return a stable identity for an AST node within a parsed tree."""

        return (node.start_byte, node.end_byte)

    @staticmethod
    def _node_text(node: Node, source_bytes: bytes) -> str:
        """Decode a node's original source text."""

        return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")

    def _detect_language(self, file_path: str) -> str:
        """Return the grammar identifier for the source file extension."""

        extension = Path(file_path).suffix.lower()
        language = self._LANGUAGE_BY_EXTENSION.get(extension)
        if language is None:
            raise ValueError(
                f"Unsupported source file extension: {extension or '<none>'}"
            )
        return language
