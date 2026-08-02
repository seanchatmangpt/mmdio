"""Render admitted Mermaid AST models as Mermaid source text."""

from __future__ import annotations

from enum import StrEnum

from mmdio.engine.models import (
    C4Diagram,
    ClassDiagram,
    ERDiagram,
    FlowchartDiagram,
    GanttChart,
    GitGraph,
    Mindmap,
    MindmapNode,
    NodeShape,
    PieChart,
    SankeyDiagram,
    SequenceDiagram,
    SequenceMessage,
    StateDiagram,
)


def _enum_value(value: str | StrEnum) -> str:
    """Return the serialized value of a string enum or plain string."""
    return value.value if isinstance(value, StrEnum) else value


def _escape(value: str) -> str:
    """Escape a value for a Mermaid double-quoted string."""
    return value.replace('"', '\\"')


def render_flowchart(diagram: FlowchartDiagram) -> str:
    """Render a flowchart diagram."""
    lines = [f"flowchart {diagram.direction}"]
    for node in diagram.nodes:
        marker_open, marker_close = _NODE_MARKERS.get(node.shape, ("[", "]"))
        lines.append(f"    {node.id}{marker_open}{_escape(node.label)}{marker_close}")
    for edge in diagram.edges:
        arrow = _EDGE_ARROWS.get(edge.style or "solid", "-->")
        label = f"|{_escape(edge.label)}|" if edge.label else ""
        lines.append(f"    {edge.source} {arrow}{label} {edge.target}")
    return "\n".join(lines)


def render_sequence(diagram: SequenceDiagram) -> str:
    """Render a sequence diagram."""
    lines = ["sequenceDiagram"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")
    for participant in diagram.participants:
        lines.append(
            f"    {_enum_value(participant.type)} {participant.id} as "
            f"{_escape(participant.name)}"
        )
    for message in sorted(diagram.messages, key=_sequence_order):
        arrow = _SEQUENCE_ARROWS.get(_enum_value(message.type), "->>")
        lines.append(
            f"    {message.from_participant}{arrow}{message.to_participant}: "
            f"{_escape(message.label)}"
        )
    return "\n".join(lines)


def _sequence_order(message: SequenceMessage) -> int:
    """Return a stable sort key for sequence messages."""
    return message.sequence_number or 0


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
        arrow = _CLASS_ARROWS.get(_enum_value(relationship.type), "-->")
        label = f" : {_escape(relationship.label)}" if relationship.label else ""
        lines.append(
            f"    {relationship.from_class} {arrow} {relationship.to_class}{label}"
        )
    return "\n".join(lines)


def render_state(diagram: StateDiagram) -> str:
    """Render a state diagram."""
    lines = ["stateDiagram-v2"]
    states = {state.id: state for state in diagram.states}
    for state in diagram.states:
        if state.label != state.id:
            lines.append(f'    state "{_escape(state.label)}" as {state.id}')
        if state.entry_action:
            lines.append(f"    {state.id}: entry / {state.entry_action}")
        if state.exit_action:
            lines.append(f"    {state.id}: exit / {state.exit_action}")
    for transition in diagram.transitions:
        source_state = states.get(transition.from_state)
        target_state = states.get(transition.to_state)
        source = "[*]" if source_state and source_state.is_initial else transition.from_state
        target = "[*]" if target_state and target_state.is_final else transition.to_state
        label = _transition_label(transition.event, transition.guard, transition.action)
        suffix = f" : {label}" if label else ""
        lines.append(f"    {source} --> {target}{suffix}")
    return "\n".join(lines)


def _transition_label(event: str | None, guard: str | None, action: str | None) -> str:
    """Construct a state-transition label."""
    parts: list[str] = []
    if event:
        parts.append(event)
    if guard:
        parts.append(f"[{guard}]")
    if action:
        parts.append(f"/ {action}")
    return " ".join(parts)


def render_er(diagram: ERDiagram) -> str:
    """Render an entity-relationship diagram."""
    lines = ["erDiagram"]
    for relationship in diagram.relationships:
        cardinality = _ER_CARDINALITIES.get(
            _enum_value(relationship.cardinality),
            "||--o{",
        )
        label = relationship.label or "relates to"
        lines.append(
            f'    {relationship.from_entity} {cardinality} '
            f'{relationship.to_entity} : "{_escape(label)}"'
        )
    for entity in diagram.entities:
        lines.append(f"    {entity.name} {{")
        for attribute in entity.attributes:
            attribute_type = attribute.type or "string"
            key = " PK" if attribute.is_key else ""
            lines.append(f"        {attribute_type} {attribute.name}{key}")
        lines.append("    }")
    return "\n".join(lines)


def render_gantt(diagram: GanttChart) -> str:
    """Render a Gantt chart."""
    lines = ["gantt"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")
    lines.append("    dateFormat YYYY-MM-DD")
    for task in diagram.tasks:
        status = "milestone" if task.milestone else _enum_value(task.status)
        dependencies = f"after {task.dependencies[-1]}, " if task.dependencies else ""
        lines.append(
            f"    {task.title} :{status}, {task.id}, {dependencies}"
            f"{task.start_date}, {task.end_date}"
        )
    return "\n".join(lines)


def render_pie(diagram: PieChart) -> str:
    """Render a pie chart."""
    header = f"pie title {diagram.title}" if diagram.title else "pie"
    lines = [header]
    lines.extend(f'    "{_escape(item.label)}" : {item.value}' for item in diagram.slices)
    return "\n".join(lines)


def render_git(diagram: GitGraph) -> str:
    """Render a Git graph."""
    lines = ["gitGraph"]
    commits = {commit.id: commit for commit in diagram.commits}
    for branch in diagram.branches:
        if not branch.is_main and branch.name != "main":
            lines.append(f"    branch {branch.name}")
        for commit_id in branch.commit_ids:
            commit = commits.get(commit_id)
            if commit is None:
                continue
            line = f'    commit id: "{_escape(commit.id)}"'
            if commit.message:
                line += f' tag: "{_escape(commit.message)}"'
            lines.append(line)
            if commit.tag:
                lines.append(f'    commit tag: "{_escape(commit.tag)}"')
        if not branch.is_main and branch.name != "main":
            lines.append("    checkout main")
    return "\n".join(lines)


def render_c4(diagram: C4Diagram) -> str:
    """Render a C4 context diagram."""
    lines = ["C4Context"]
    if diagram.title:
        lines.append(f"    title {diagram.title}")
    for element in diagram.elements:
        element_kind = element.element_type if element.element_type != "generic" else "System"
        arguments = [element.id, f'"{_escape(element.name)}"']
        if element.description:
            arguments.append(f'"{_escape(element.description)}"')
        lines.append(f"    {element_kind}({', '.join(arguments)})")
    for relationship in diagram.relationships:
        arguments = [
            relationship.from_element,
            relationship.to_element,
            f'"{_escape(relationship.description)}"',
        ]
        if relationship.technology:
            arguments.append(f'"{_escape(relationship.technology)}"')
        lines.append(f"    Rel({', '.join(arguments)})")
    return "\n".join(lines)


def render_mindmap(diagram: Mindmap) -> str:
    """Render a recursive mindmap."""
    lines = ["mindmap"]
    _append_mindmap_node(lines, diagram.root, 1)
    return "\n".join(lines)


def _append_mindmap_node(lines: list[str], node: MindmapNode, depth: int) -> None:
    """Append one mindmap node and its descendants."""
    lines.append(f"{'    ' * depth}{node.id}({_escape(node.label)})")
    for child in node.children:
        _append_mindmap_node(lines, child, depth + 1)


def render_sankey(diagram: SankeyDiagram) -> str:
    """Render a Sankey diagram."""
    lines = ["sankey-beta"]
    lines.extend(f"{flow.source},{flow.target},{flow.value}" for flow in diagram.flows)
    return "\n".join(lines)


_NODE_MARKERS = {
    NodeShape.RECTANGLE: ("[", "]"),
    NodeShape.CIRCLE: ("((", "))"),
    NodeShape.ELLIPSE: ("(", ")"),
    NodeShape.DIAMOND: ("{", "}"),
    NodeShape.HEXAGON: ("{{", "}}"),
    NodeShape.PARALLELOGRAM: ("[/", "/]"),
    NodeShape.TRAPEZOID: ("[/", "\\]"),
    NodeShape.DOCUMENT: ("[\\", "\\]"),
    NodeShape.CYLINDER: ("[(", ")]"),
    NodeShape.SUBROUTINE: ("[[", "]]"),
}
_EDGE_ARROWS = {"solid": "-->", "dotted": "-.->", "thick": "==>"}
_SEQUENCE_ARROWS = {"sync": "->>", "async": "-->>", "return": "-->>", "autonumber": "->>"}
_CLASS_ARROWS = {
    "inheritance": "<|--",
    "realization": "..|>",
    "composition": "*--",
    "aggregation": "o--",
    "association": "-->",
    "dependency": "..>",
    "link": "--",
}
_ER_CARDINALITIES = {
    "one_to_one": "||--||",
    "one_to_many": "||--o{",
    "many_to_one": "}o--||",
    "many_to_many": "}o--o{",
    "many_to_many_marked": "}|--{|",
    "zero_or_one": "|o--o|",
    "one": "||--||",
    "zero_or_many": "o{--{o",
    "many": "}|--|{",
}
