"""Render admitted mmdio models as Mermaid source text.

The model graph and dispatch metadata are generated from RDF. Renderers remain
specialized because Mermaid syntax requires conditional tokens, escaping, and
recursive traversal that fixed row-format templates cannot represent safely.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mmdio.engine.enums import (
    C4Level,
    CardinityType,
    MessageType,
    NodeShape,
    RelationshipType,
)
from mmdio.engine.models import GitBranch

if TYPE_CHECKING:
    from collections.abc import Mapping

    from mmdio.engine.models import (
        C4Diagram,
        ClassDiagram,
        ERDiagram,
        FlowchartDiagram,
        GanttChart,
        GitGraph,
        Mindmap,
        MindmapNode,
        PieChart,
        SankeyDiagram,
        SequenceDiagram,
        StateDiagram,
    )

_NODE_MARKERS: Mapping[NodeShape, tuple[str, str]] = {
    NodeShape.RECTANGLE: ("[", "]"),
    NodeShape.CIRCLE: ("((", "))"),
    NodeShape.ELLIPSE: ("(", ")"),
    NodeShape.DIAMOND: ("{", "}"),
    NodeShape.HEXAGON: ("{{", "}}"),
    NodeShape.PARALLELOGRAM: ("[\\", "\\]"),
    NodeShape.TRAPEZOID: ("[/", "/]"),
    NodeShape.DOCUMENT: ("[\\", "\\]"),
    NodeShape.CYLINDER: ("[(", ")]"),
    NodeShape.SUBROUTINE: ("[[", "]]"),
}
_EDGE_ARROWS: Mapping[str, str] = {
    "solid": "-->",
    "dotted": "-.->",
    "thick": "==>",
}
_MESSAGE_ARROWS: Mapping[MessageType, str] = {
    MessageType.SYNC: "->>",
    MessageType.ASYNC: "-->>",
    MessageType.RETURN: "-->>",
    MessageType.AUTONUMBER: "->>",
}
_CLASS_ARROWS: Mapping[RelationshipType, str] = {
    RelationshipType.INHERITANCE: "<|--",
    RelationshipType.REALIZATION: "--|>",
    RelationshipType.COMPOSITION: "*--",
    RelationshipType.AGGREGATION: "o--",
    RelationshipType.ASSOCIATION: "-->",
    RelationshipType.DEPENDENCY: "..>",
    RelationshipType.LINK: "--",
}
_ER_CARDINALITIES: Mapping[CardinityType, str] = {
    CardinityType.ONE_TO_ONE: "||--||",
    CardinityType.ONE_TO_MANY: "||--o{",
    CardinityType.MANY_TO_ONE: "}o--||",
    CardinityType.MANY_TO_MANY: "}o--o{",
    CardinityType.MANY_TO_MANY_MARKED: "}|--{|",
    CardinityType.ZERO_OR_ONE: "|o--o|",
    CardinityType.ONE: "||--||",
    CardinityType.ZERO_OR_MANY: "||--o{",
    CardinityType.MANY: "}o--o{",
}
_C4_FUNCTIONS: Mapping[C4Level, str] = {
    C4Level.C1: "System",
    C4Level.C2: "Container",
    C4Level.C3: "Component",
    C4Level.C4: "System",
}


def _quote(value: str) -> str:
    """Escape a value embedded in a double-quoted Mermaid token."""
    return value.replace('"', '\\"')


def render_flowchart(diagram: FlowchartDiagram) -> str:
    """Render a flowchart diagram."""
    lines = [f"graph {diagram.direction}"]
    for node in diagram.nodes:
        opening, closing = _NODE_MARKERS.get(node.shape, ("[", "]"))
        lines.append(f"{node.id}{opening}{_quote(node.label)}{closing}")

    for edge in diagram.edges:
        arrow = _EDGE_ARROWS.get(edge.style or "solid", "-->")
        if edge.label:
            lines.append(
                f"{edge.source} {arrow}|{_quote(edge.label)}| {edge.target}",
            )
        else:
            lines.append(f"{edge.source} {arrow} {edge.target}")
    return "\n".join(lines)


def render_sequence(diagram: SequenceDiagram) -> str:
    """Render a sequence diagram."""
    lines = ["sequenceDiagram"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")
    for participant in diagram.participants:
        lines.append(
            f"    {participant.type} {participant.id} as {participant.name}",
        )
    for message in sorted(
        diagram.messages,
        key=lambda item: item.sequence_number or 0,
    ):
        arrow = _MESSAGE_ARROWS.get(message.type, "->>")
        lines.append(
            f"    {message.from_participant}{arrow}{message.to_participant}: "
            f"{_quote(message.label)}",
        )
    return "\n".join(lines)


def render_class(diagram: ClassDiagram) -> str:
    """Render a class diagram."""
    lines = ["classDiagram"]
    for class_definition in diagram.classes:
        lines.append(f"    class {class_definition.name} {{")
        for member in class_definition.members:
            member_type = f"{member.type} " if member.type else ""
            lines.append(f"        {member.visibility}{member_type}{member.name}")
        for method in class_definition.methods:
            signature = method.signature or f"{method.name}()"
            return_type = f" {method.return_type}" if method.return_type else ""
            lines.append(f"        {method.visibility}{signature}{return_type}")
        lines.append("    }")

    for relationship in diagram.relationships:
        arrow = _CLASS_ARROWS.get(relationship.type, "-->")
        if relationship.label:
            lines.append(
                f"    {relationship.from_class} {arrow}|{_quote(relationship.label)}| "
                f"{relationship.to_class}",
            )
        else:
            lines.append(
                f"    {relationship.from_class} {arrow} {relationship.to_class}",
            )
    return "\n".join(lines)


def render_state(diagram: StateDiagram) -> str:
    """Render a state diagram."""
    lines = ["stateDiagram-v2"]
    states_by_id = {state.id: state for state in diagram.states}
    for state in diagram.states:
        if state.label != state.id:
            lines.append(f'    state "{_quote(state.label)}" as {state.id}')

    for transition in diagram.transitions:
        source_state = states_by_id.get(transition.from_state)
        target_state = states_by_id.get(transition.to_state)
        source = "[*]" if source_state and source_state.is_initial else transition.from_state
        target = "[*]" if target_state and target_state.is_final else transition.to_state
        details: list[str] = []
        if transition.event:
            details.append(transition.event)
        if transition.guard:
            details.append(f"[{transition.guard}]")
        if transition.action:
            details.append(f"/ {transition.action}")
        suffix = f" : {' '.join(details)}" if details else ""
        lines.append(f"    {source} --> {target}{suffix}")
    return "\n".join(lines)


def render_er(diagram: ERDiagram) -> str:
    """Render an entity-relationship diagram."""
    lines = ["erDiagram"]
    for relationship in diagram.relationships:
        cardinality = _ER_CARDINALITIES.get(relationship.cardinality, "||--||")
        label = f" : {relationship.label}" if relationship.label else ""
        lines.append(
            f"    {relationship.from_entity} {cardinality} "
            f"{relationship.to_entity}{label}",
        )

    for entity in diagram.entities:
        lines.append(f"    {entity.name} {{")
        for attribute in entity.attributes:
            key_marker = " PK" if attribute.is_key else ""
            lines.append(f"        {attribute.type or 'string'} {attribute.name}{key_marker}")
        lines.append("    }")
    return "\n".join(lines)


def render_gantt(diagram: GanttChart) -> str:
    """Render a Gantt chart."""
    lines = ["gantt"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")
    lines.append("    dateFormat YYYY-MM-DD")
    for task in diagram.tasks:
        status = "milestone" if task.milestone else str(task.status)
        parts = [status]
        if task.dependencies:
            parts.append(f"after {' '.join(task.dependencies)}")
        parts.extend((task.start_date, task.end_date))
        lines.append(f"    {task.title} :{task.id}, {', '.join(parts)}")
    return "\n".join(lines)


def render_pie(diagram: PieChart) -> str:
    """Render a pie chart."""
    lines = [f"pie title {diagram.title}" if diagram.title else "pie"]
    lines.extend(f'    "{_quote(item.label)}" : {item.value}' for item in diagram.slices)
    return "\n".join(lines)


def render_git(diagram: GitGraph) -> str:
    """Render a git graph."""
    lines = ["gitGraph"]
    commits_by_id = {commit.id: commit for commit in diagram.commits}
    branches = diagram.branches or [
        GitBranch(
            name="main",
            commit_ids=[commit.id for commit in diagram.commits],
            is_main=True,
        ),
    ]
    for branch in branches:
        is_main = branch.is_main or branch.name == "main"
        if not is_main:
            lines.append(f"    branch {branch.name}")
        for commit_id in branch.commit_ids:
            commit = commits_by_id.get(commit_id)
            if commit is None:
                continue
            line = (
                f'    commit id: "{_quote(commit.id)}" '
                f'message: "{_quote(commit.message)}"'
            )
            if commit.tag:
                line += f' tag: "{_quote(commit.tag)}"'
            lines.append(line)
        if not is_main:
            lines.append("    checkout main")
    return "\n".join(lines)


def render_c4(diagram: C4Diagram) -> str:
    """Render a C4 context projection."""
    lines = ["C4Context"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")
    for element in diagram.elements:
        function_name = _C4_FUNCTIONS.get(element.level, "System")
        arguments = [element.id, f'"{_quote(element.name)}"']
        if element.technology:
            arguments.append(f'"{_quote(element.technology)}"')
        if element.description:
            arguments.append(f'"{_quote(element.description)}"')
        lines.append(f"    {function_name}({', '.join(arguments)})")

    for relationship in diagram.relationships:
        arguments = [
            relationship.from_element,
            relationship.to_element,
            f'"{_quote(relationship.description)}"',
        ]
        if relationship.technology:
            arguments.append(f'"{_quote(relationship.technology)}"')
        lines.append(f"    Rel({', '.join(arguments)})")
    return "\n".join(lines)


def render_mindmap(diagram: Mindmap) -> str:
    """Render a recursive mindmap."""
    lines = ["mindmap"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")

    def append_node(node: MindmapNode, depth: int) -> None:
        lines.append(f"{'    ' * (depth + 1)}{_quote(node.label)}")
        for child in node.children:
            append_node(child, depth + 1)

    append_node(diagram.root, 0)
    return "\n".join(lines)


def render_sankey(diagram: SankeyDiagram) -> str:
    """Render a Sankey diagram."""
    lines = ["sankey-beta"]
    for flow in diagram.flows:
        source = flow.source.replace(",", "")
        target = flow.target.replace(",", "")
        lines.append(f"    {source},{target},{flow.value}")
    return "\n".join(lines)
