"""Dependency graph generation for parsed source repositories."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import networkx as nx

from app.schemas.repository import CodeFile, FunctionNode

_LAYOUT_SCALE = 400.0
_LAYOUT_SEED = 42


@dataclass(frozen=True)
class _FunctionReference:
    """A parsed function and its globally unique graph node identifier."""

    node_id: str
    function: FunctionNode
    file_path: str


class DependencyGraphBuilder:
    """Build a directed, React Flow-compatible dependency graph."""

    def build_graph(self, files: list[CodeFile]) -> dict[str, list[dict[str, Any]]]:
        """Build file containment and function-call dependencies from parsed files."""

        graph = nx.DiGraph()
        functions_by_name: dict[str, list[_FunctionReference]] = {}

        for code_file in files:
            file_id = self._file_node_id(code_file)
            graph.add_node(
                file_id,
                label=code_file.file_path,
                node_type="file",
                file_path=code_file.file_path,
            )

            for function in self._functions_in(code_file):
                function_id = self._function_node_id(graph, code_file, function)
                reference = _FunctionReference(
                    node_id=function_id,
                    function=function,
                    file_path=code_file.file_path,
                )
                functions_by_name.setdefault(function.name, []).append(reference)
                graph.add_node(
                    function_id,
                    label=function.name,
                    node_type="function",
                    file_path=code_file.file_path,
                )
                graph.add_edge(file_id, function_id, label="contains")

        self._add_call_edges(graph, functions_by_name)
        positions = self._layout_positions(graph)

        return {
            "nodes": [
                {
                    "id": node_id,
                    "type": "default",
                    "position": positions[node_id],
                    "data": {
                        "label": attributes["label"],
                        "node_type": attributes["node_type"],
                        "file_path": attributes["file_path"],
                    },
                }
                for node_id, attributes in graph.nodes(data=True)
            ],
            "edges": [
                {
                    "id": f"{source}-{target}",
                    "source": source,
                    "target": target,
                    "animated": True,
                    "label": attributes["label"],
                }
                for source, target, attributes in graph.edges(data=True)
            ],
        }

    def _add_call_edges(
        self,
        graph: nx.DiGraph,
        functions_by_name: dict[str, list[_FunctionReference]],
    ) -> None:
        """Add edges for calls that resolve to exactly one repository function."""

        for references in functions_by_name.values():
            for reference in references:
                for called_name in reference.function.calls:
                    targets = functions_by_name.get(called_name, [])
                    if len(targets) != 1:
                        continue
                    target_id = targets[0].node_id
                    if target_id != reference.node_id:
                        graph.add_edge(reference.node_id, target_id, label="calls")

    @staticmethod
    def _functions_in(code_file: CodeFile) -> Iterable[FunctionNode]:
        """Yield top-level functions and methods declared by each class."""

        yield from code_file.functions
        for class_node in code_file.classes:
            yield from class_node.methods

    @staticmethod
    def _file_node_id(code_file: CodeFile) -> str:
        """Return a globally unique graph node ID for a file."""

        return f"file::{code_file.file_path}"

    @staticmethod
    def _function_node_id(
        graph: nx.DiGraph,
        code_file: CodeFile,
        function: FunctionNode,
    ) -> str:
        """Return a collision-safe graph node ID for a function declaration."""

        base_id = f"{code_file.file_path}::{function.name}"
        node_id = base_id
        duplicate_index = 2
        while node_id in graph:
            node_id = f"{base_id}#{duplicate_index}"
            duplicate_index += 1
        return node_id

    @staticmethod
    def _layout_positions(graph: nx.DiGraph) -> dict[str, dict[str, float]]:
        """Calculate scaled, deterministic positions for React Flow nodes."""

        if not graph.nodes:
            return {}

        try:
            layout = nx.spring_layout(graph, k=0.5, seed=_LAYOUT_SEED)
            return {
                node_id: {
                    "x": float(coordinates[0] * _LAYOUT_SCALE),
                    "y": float(coordinates[1] * _LAYOUT_SCALE),
                }
                for node_id, coordinates in layout.items()
            }
        except Exception:
            return {
                node_id: {
                    "x": float((index % 4) * _LAYOUT_SCALE),
                    "y": float((index // 4) * _LAYOUT_SCALE),
                }
                for index, node_id in enumerate(graph.nodes)
            }
