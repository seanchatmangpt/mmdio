"""Specialized Mermaid renderers for the eleven deep semantic projections.

Generated from ``packs/mmdio-pack/templates/specialized_render.py.tmpl``.
The universal 39-type CST uses ``render_document``; these functions preserve
the richer compatibility models and are independently checked by mermaid-js.
"""

from __future__ import annotations

from collections.abc import Iterable

from mmdio.engine.enums import (
    C4Level,
    CardinityType,
    MessageType,
    NodeShape,
    ParticipantType,
    RelationshipType,
    TaskStatus,
)
from mmdio.engine.models import (
    C4Diagram,
    C4Element,
    ClassDefinition,
    ClassDiagram,
    ERDiagram,
    Entity,
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


def _quote(value: object | None) -> str:
    text = "" if value is None else str(value)
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _finish(lines: Iterable[str]) -> str:
    return "\n".join(lines) + "\n"


def _c4_element(element: C4Element) -> str:
    description = _quote(element.description)
    technology = _quote(element.technology)
    name = _quote(element.name)
    element_id = element.id
    if element.level == C4Level.C1:
        constructor = "Person" if element.element_type.lower() in {"person", "user"} else "System"
        return f'  {constructor}({element_id}, "{name}", "{description}")'
    if element.level == C4Level.C2:
        return f'  Container({element_id}, "{name}", "{technology}", "{description}")'
    return f'  Component({element_id}, "{name}", "{technology}", "{description}")'


def render_c4(diagram: C4Diagram) -> str:
    """Render a C4 context-compatible diagram."""
    lines = ["C4Context"]
    if diagram.title:
        lines.append(f'title "{_quote(diagram.title)}"')
    lines.extend(_c4_element(element) for element in diagram.elements)
    for relationship in diagram.relationships:
        technology = (
            f', "{_quote(relationship.technology)}"' if relationship.technology else ""
        )
        lines.append(
            f'  Rel({relationship.from_element}, {relationship.to_element}, '
            f'"{_quote(relationship.description)}"{technology})'
        )
    return _finish(lines)


def _class_body(definition: ClassDefinition) -> list[str]:
    lines = [f"  class {definition.name} {{"]
    for member in definition.members:
        suffix = f" {member.type}" if member.type else ""
        lines.append(f"    {member.visibility}{member.name}{suffix}")
    for method in definition.methods:
        signature = method.signature or f"{method.name}()"
        return_type = f" {method.return_type}" if method.return_type else ""
        lines.append(f"    {method.visibility}{signature}{return_type}")
    lines.append("  }")
    if definition.is_interface:
        lines.append(f"  <<interface>> {definition.name}")
    elif definition.is_abstract:
        lines.append(f"  <<abstract>> {definition.name}")
    return lines


_RELATIONSHIP_TOKENS = {
    RelationshipType.INHERITANCE: "--|>",
    RelationshipType.REALIZATION: "..|>",
    RelationshipType.COMPOSITION: "*--",
    RelationshipType.AGGREGATION: "o--",
    RelationshipType.ASSOCIATION: "-->",
    RelationshipType.DEPENDENCY: "..>",
    RelationshipType.LINK: "--",
}


def render_class(diagram: ClassDiagram) -> str:
    """Render a class diagram with members, methods, and typed relations."""
    lines = ["classDiagram"]
    for definition in diagram.classes:
        lines.extend(_class_body(definition))
    for relationship in diagram.relationships:
        label = f" : {_quote(relationship.label)}" if relationship.label else ""
        token = _RELATIONSHIP_TOKENS[relationship.type]
        lines.append(f"  {relationship.from_class} {token} {relationship.to_class}{label}")
    return _finish(lines)


def _entity_body(entity: Entity) -> list[str]:
    lines = [f"  {entity.name} {{"]
    for attribute in entity.attributes:
        attribute_type = attribute.type or "string"
        key = " PK" if attribute.is_key else ""
        lines.append(f"    {attribute_type} {attribute.name}{key}")
    lines.append("  }")
    return lines


_CARDINALITY_TOKENS = {
    CardinityType.ONE_TO_ONE: "||--||",
    CardinityType.ONE_TO_MANY: "||--o{",
    CardinityType.MANY_TO_ONE: "}o--||",
    CardinityType.MANY_TO_MANY: "}o--o{",
    CardinityType.MANY_TO_MANY_MARKED: "}|--|{",
    CardinityType.ZERO_OR_ONE: "|o--o|",
    CardinityType.ONE: "||--||",
    CardinityType.ZERO_OR_MANY: "}o--o{",
    CardinityType.MANY: "}|--|{",
}


def render_er(diagram: ERDiagram) -> str:
    """Render entities, attributes, and cardinality-preserving relationships."""
    lines = ["erDiagram"]
    if diagram.title:
        lines.append(f"  %% title: {_quote(diagram.title)}")
    for entity in diagram.entities:
        lines.extend(_entity_body(entity))
    for relationship in diagram.relationships:
        label = _quote(relationship.label or "relates")
        token = _CARDINALITY_TOKENS[relationship.cardinality]
        lines.append(
            f'  {relationship.from_entity} {token} {relationship.to_entity} : "{label}"'
        )
    return _finish(lines)


_NODE_SHAPES = {
    NodeShape.RECTANGLE: ('["', '"]'),
    NodeShape.CIRCLE: ('(("', '"))'),
    NodeShape.ELLIPSE: ('(["', '"])'),
    NodeShape.DIAMOND: ('{"', '"}'),
    NodeShape.HEXAGON: ('{{"', '"}}'),
    NodeShape.PARALLELOGRAM: ('[/"', '"/]'),
    NodeShape.TRAPEZOID: ('[/"', '"\\]'),
    NodeShape.DOCUMENT: ('["', '"]'),
    NodeShape.CYLINDER: ('[("', '")]'),
    NodeShape.SUBROUTINE: ('[["', '"]]'),
}


def render_flowchart(diagram: FlowchartDiagram) -> str:
    """Render a flowchart while preserving direction, shapes, labels, and styles."""
    lines = [f"flowchart {diagram.direction}"]
    for node in diagram.nodes:
        opening, closing = _NODE_SHAPES[node.shape]
        lines.append(f"  {node.id}{opening}{_quote(node.label)}{closing}")
    for edge in diagram.edges:
        token = edge.style if edge.style in {"-->", "-.->", "==>"} else "-->"
        label = f'|{_quote(edge.label)}|' if edge.label else ""
        lines.append(f"  {edge.source} {token}{label} {edge.target}")
    return _finish(lines)


_STATUS_TOKENS = {
    TaskStatus.ACTIVE: "active",
    TaskStatus.DONE: "done",
    TaskStatus.MILESTONE: "milestone",
    TaskStatus.CRIT: "crit",
    TaskStatus.ACTIVE_CRIT: "crit, active",
    TaskStatus.DONE_CRIT: "crit, done",
}


def render_gantt(diagram: GanttChart) -> str:
    """Render a deterministic ISO-date Gantt chart."""
    lines = ["gantt"]
    if diagram.title:
        lines.append(f"  title {_quote(diagram.title)}")
    lines.extend(["  dateFormat YYYY-MM-DD", "  section Tasks"])
    for task in diagram.tasks:
        status = _STATUS_TOKENS[task.status]
        schedule = f"after {task.dependencies[-1]}" if task.dependencies else task.start_date
        lines.append(
            f"  {_quote(task.title)} :{status}, {task.id}, {schedule}, {task.end_date}"
        )
    return _finish(lines)


def render_git(diagram: GitGraph) -> str:
    """Render commits and named branches as valid gitGraph syntax."""
    lines = ["gitGraph"]
    for commit in diagram.commits:
        tag = f' tag: "{_quote(commit.tag)}"' if commit.tag else ""
        lines.append(f'  commit id: "{_quote(commit.id)}"{tag}')
    for branch in diagram.branches:
        if branch.is_main or branch.name in {"main", "master"}:
            continue
        lines.append(f"  branch {branch.name}")
    return _finish(lines)


def _mindmap_lines(node: MindmapNode, depth: int) -> list[str]:
    indent = "  " * depth
    lines = [f'{indent}{node.id}(("{_quote(node.label)}"))']
    for child in node.children:
        lines.extend(_mindmap_lines(child, depth + 1))
    return lines


def render_mindmap(diagram: Mindmap) -> str:
    """Render the recursive mindmap root and descendants."""
    lines = ["mindmap"]
    lines.extend(_mindmap_lines(diagram.root, 1))
    return _finish(lines)


def render_pie(diagram: PieChart) -> str:
    """Render a pie chart."""
    lines = ["pie"]
    if diagram.title:
        lines.append(f"  title {_quote(diagram.title)}")
    lines.extend(f'  "{_quote(item.label)}" : {item.value}' for item in diagram.slices)
    return _finish(lines)


def render_sankey(diagram: SankeyDiagram) -> str:
    """Render a Sankey CSV carrier."""
    lines = ["sankey-beta"]
    lines.extend(
        f"{_quote(flow.source)},{_quote(flow.target)},{flow.value}" for flow in diagram.flows
    )
    return _finish(lines)


_MESSAGE_TOKENS = {
    MessageType.SYNC: "->>",
    MessageType.ASYNC: "-)",
    MessageType.RETURN: "-->>",
    MessageType.AUTONUMBER: "->>",
}


def render_sequence(diagram: SequenceDiagram) -> str:
    """Render participants and messages with valid Mermaid arrow tokens."""
    lines = ["sequenceDiagram"]
    if diagram.title:
        lines.append(f"  title {_quote(diagram.title)}")
    if any(message.type == MessageType.AUTONUMBER for message in diagram.messages):
        lines.append("  autonumber")
    for participant in diagram.participants:
        declaration = "actor" if participant.type == ParticipantType.ACTOR else "participant"
        lines.append(f"  {declaration} {participant.id} as {_quote(participant.name)}")
    for message in diagram.messages:
        token = _MESSAGE_TOKENS[message.type]
        lines.append(
            f"  {message.from_participant}{token}{message.to_participant}: "
            f"{_quote(message.label)}"
        )
    return _finish(lines)


def render_state(diagram: StateDiagram) -> str:
    """Render states, initial/final markers, and guarded transitions."""
    lines = ["stateDiagram-v2"]
    for state in diagram.states:
        if state.label != state.id:
            lines.append(f'  state "{_quote(state.label)}" as {state.id}')
        else:
            lines.append(f"  state {state.id}")
        if state.is_initial:
            lines.append(f"  [*] --> {state.id}")
        if state.is_final:
            lines.append(f"  {state.id} --> [*]")
    for transition in diagram.transitions:
        details = [item for item in (transition.event, transition.guard, transition.action) if item]
        label = f" : {' / '.join(_quote(item) for item in details)}" if details else ""
        lines.append(f"  {transition.from_state} --> {transition.to_state}{label}")
    return _finish(lines)
