"""Deterministic Mermaid projections for canonical planning graphs."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import io
import json

from .model import PlanningEdge, PlanningEdgeKind, PlanningGraph, PlanningNodeKind


@dataclass(frozen=True, slots=True)
class PlanningDocument:
    """One non-actuating Mermaid projection of an exact planning subject."""

    name: str
    diagram_type: str
    content: str
    planning_digest: str

    def content_sha256(self) -> str:
        """Return the exact byte identity of the Mermaid source."""
        return sha256(self.content.encode()).hexdigest()


def generate_planning_documents(subject: PlanningGraph) -> tuple[PlanningDocument, ...]:
    """Generate every Mermaid view justified by information present in the graph."""
    subject.validate()
    candidates = (
        ("topology", "flowchart", project_flowchart(subject)),
        ("summary", "mindmap", project_mindmap(subject)),
        ("states", "stateDiagram-v2", project_state_diagram(subject)),
        ("requirements", "requirement", project_requirements(subject)),
        ("timeline", "timeline", project_timeline(subject)),
        ("schedule", "gantt", project_gantt(subject)),
        ("value-flow", "sankey", project_sankey(subject)),
        ("interactions", "sequence", project_sequence(subject)),
    )
    digest = subject.digest()
    return tuple(
        PlanningDocument(name=name, diagram_type=diagram_type, content=content, planning_digest=digest)
        for name, diagram_type, content in candidates
        if content
    )


def project_flowchart(subject: PlanningGraph) -> str:
    """Project all nodes and semantic relations into the crowned flowchart profile."""
    lines = ["flowchart LR"]
    for node in sorted(subject.nodes, key=lambda item: item.id):
        label = f"{node.kind.value}: {node.label}"
        lines.append(f"  {_id(node.id)}[{json.dumps(label, ensure_ascii=False)}]")
    for edge in sorted(subject.edges, key=_edge_sort_key):
        label = _edge_semantic_label(edge)
        lines.append(f"  {_id(edge.source)} -->|{_edge_label(label)}| {_id(edge.target)}")
    return "\n".join(lines) + "\n"


def project_mindmap(subject: PlanningGraph) -> str:
    """Project a compact human summary grouped by semantic node kind."""
    if not subject.nodes:
        return ""
    lines = ["mindmap", f"  root(({_mindmap_text(subject.subject)}))"]
    kinds = sorted({node.kind for node in subject.nodes}, key=lambda item: item.value)
    for kind in kinds:
        lines.append(f"    {_mindmap_text(kind.value)}")
        for node in sorted((item for item in subject.nodes if item.kind == kind), key=lambda item: item.id):
            lines.append(f"      {_mindmap_text(node.label)}")
    return "\n".join(lines) + "\n"


def project_state_diagram(subject: PlanningGraph) -> str:
    """Project explicit state-to-state transitions without inventing intermediate states."""
    state_kinds = {PlanningNodeKind.STATE, PlanningNodeKind.GOAL}
    state_ids = {node.id for node in subject.nodes if node.kind in state_kinds}
    admitted_edges = {
        PlanningEdgeKind.TRANSITION,
        PlanningEdgeKind.PROBABILISTIC,
        PlanningEdgeKind.TEMPORAL,
        PlanningEdgeKind.CAUSAL,
    }
    transitions = [
        edge
        for edge in subject.edges
        if edge.source in state_ids and edge.target in state_ids and edge.kind in admitted_edges
    ]
    if not transitions:
        return ""
    lines = ["stateDiagram-v2"]
    for node in sorted((item for item in subject.nodes if item.id in state_ids), key=lambda item: item.id):
        lines.append(f'  state "{_quoted_text(node.label)}" as {_id(node.id)}')
    for edge in sorted(transitions, key=_edge_sort_key):
        lines.append(
            f"  {_id(edge.source)} --> {_id(edge.target)} : "
            f"{_state_text(_edge_semantic_label(edge))}"
        )
    return "\n".join(lines) + "\n"


def project_requirements(subject: PlanningGraph) -> str:
    """Project goals and constraints into a SysML-style Mermaid requirement diagram."""
    requirement_nodes = [
        node
        for node in subject.nodes
        if node.kind in {PlanningNodeKind.GOAL, PlanningNodeKind.CONSTRAINT}
    ]
    if not requirement_nodes:
        return ""
    lines = ["requirementDiagram", "  direction LR"]
    requirement_ids = {node.id for node in requirement_nodes}
    for index, node in enumerate(sorted(requirement_nodes, key=lambda item: item.id), start=1):
        keyword = "designConstraint" if node.kind == PlanningNodeKind.CONSTRAINT else "requirement"
        risk = _enum_value(node.attributes.get("risk", "medium"), {"low", "medium", "high"}, "medium")
        method = _enum_value(
            node.attributes.get("verify", "test"),
            {"analysis", "inspection", "test", "demonstration"},
            "test",
        )
        lines.extend(
            (
                f"  {keyword} {_id(node.id)} {{",
                f"    id: R{index}",
                f"    text: {json.dumps(node.label, ensure_ascii=False)}",
                f"    risk: {risk}",
                f"    verifymethod: {method}",
                "  }",
            )
        )
    for edge in sorted(subject.edges, key=_edge_sort_key):
        if edge.source in requirement_ids and edge.target in requirement_ids:
            lines.append(f"  {_id(edge.source)} - traces -> {_id(edge.target)}")
    return "\n".join(lines) + "\n"


def project_timeline(subject: PlanningGraph) -> str:
    """Project explicit process/event/time observations into a chronology."""
    temporal = [
        node
        for node in subject.nodes
        if node.kind in {PlanningNodeKind.EVENT, PlanningNodeKind.PROCESS}
        or "time" in node.attributes
    ]
    if not temporal:
        return ""
    lines = ["timeline", f"  title {_timeline_text(subject.subject)}"]
    for node in sorted(temporal, key=lambda item: (_time_sort_value(item.attributes.get("time")), item.id)):
        marker = node.attributes.get("time")
        if marker is None:
            marker = f"{node.kind.value}"
        lines.append(f"  {_timeline_text(str(marker))} : {_timeline_text(node.label)}")
    return "\n".join(lines) + "\n"


def project_gantt(subject: PlanningGraph) -> str:
    """Project explicitly scheduled or durative actions/processes into a Gantt chart."""
    scheduled = [
        node
        for node in subject.nodes
        if node.kind in {PlanningNodeKind.ACTION, PlanningNodeKind.PROCESS}
        and ("start" in node.attributes or "duration" in node.attributes)
    ]
    if not scheduled:
        return ""
    lines = [
        "gantt",
        f"  title {_gantt_text(subject.subject)}",
        "  dateFormat X",
        "  axisFormat %s",
        "  section Plan",
    ]
    cursor = 0.0
    ordered = sorted(scheduled, key=lambda item: (float(item.attributes.get("start", cursor)), item.id))
    for index, node in enumerate(ordered, start=1):
        start = float(node.attributes.get("start", cursor))
        duration = max(0.001, float(node.attributes.get("duration", 1.0)))
        lines.append(
            f"  {_gantt_text(node.label)} :p{index}, {_number(start)}, {_number(duration)}s"
        )
        cursor = max(cursor, start + duration)
    return "\n".join(lines) + "\n"


def project_sankey(subject: PlanningGraph) -> str:
    """Project non-negative numeric probability/value/weight relations into Sankey flow."""
    weighted: list[tuple[PlanningEdge, float]] = []
    for edge in subject.edges:
        weight = _edge_weight(edge)
        if weight is not None and weight >= 0:
            weighted.append((edge, weight))
    if not weighted:
        return ""
    labels = {node.id: node.label for node in subject.nodes}
    stream = io.StringIO()
    stream.write("sankey\n")
    for edge, weight in sorted(weighted, key=lambda item: _edge_sort_key(item[0])):
        stream.write(
            f"{_csv(labels[edge.source])},{_csv(labels[edge.target])},{_number(weight)}\n"
        )
    return stream.getvalue()


def project_sequence(subject: PlanningGraph) -> str:
    """Project actions carrying explicit actor/target_actor metadata into interactions."""
    actions = [
        node
        for node in subject.nodes
        if node.kind == PlanningNodeKind.ACTION
        and node.attributes.get("actor")
        and node.attributes.get("target_actor")
    ]
    if not actions:
        return ""
    actor_names = sorted(
        {
            str(value)
            for node in actions
            for value in (node.attributes["actor"], node.attributes["target_actor"])
        }
    )
    actor_ids = {name: f"actor_{index}" for index, name in enumerate(actor_names, start=1)}
    lines = ["sequenceDiagram"]
    for name in actor_names:
        lines.append(f"  participant {actor_ids[name]} as {_sequence_text(name)}")
    for node in sorted(actions, key=lambda item: (float(item.attributes.get("start", 0)), item.id)):
        source = actor_ids[str(node.attributes["actor"])]
        target = actor_ids[str(node.attributes["target_actor"])]
        lines.append(f"  {source}->>{target}: {_sequence_text(node.label)}")
    return "\n".join(lines) + "\n"


def _edge_sort_key(edge: PlanningEdge) -> tuple[str, str, str, str]:
    return edge.source, edge.target, edge.kind.value, edge.label or ""


def _edge_semantic_label(edge: PlanningEdge) -> str:
    label = edge.label or edge.kind.value
    probability = edge.attributes.get("probability")
    if probability is not None:
        return f"{label} p={_number(float(probability))}"
    return label


def _edge_weight(edge: PlanningEdge) -> float | None:
    for key in ("probability", "value", "weight"):
        value = edge.attributes.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _id(value: str) -> str:
    rendered = "".join(char if char.isalnum() or char == "_" else "_" for char in value)
    if not rendered or rendered[0].isdigit():
        rendered = f"n_{rendered}"
    return rendered


def _edge_label(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").replace("\r", " ").strip()


def _quoted_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")


def _state_text(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace(":", " - ").strip()


def _mindmap_text(value: str) -> str:
    translation = str.maketrans({char: " " for char in "()[]{}"})
    return value.translate(translation).replace("\n", " ").replace("\r", " ").replace(":", " - ").strip()


def _timeline_text(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace(":", " - ").strip()


def _gantt_text(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace(":", " - ").strip()


def _sequence_text(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace(":", " - ").strip()


def _enum_value(value: object, allowed: set[str], default: str) -> str:
    candidate = str(value).lower()
    return candidate if candidate in allowed else default


def _number(value: float) -> str:
    return f"{value:g}"


def _csv(value: str) -> str:
    return '"' + value.replace('"', '""').replace("\n", " ").replace("\r", " ") + '"'


def _time_sort_value(value: object) -> tuple[int, float | str]:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return 0, float(value)
    if value is None:
        return 2, ""
    return 1, str(value)
