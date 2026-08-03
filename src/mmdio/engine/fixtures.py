"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

One example_<internalId>() builder per top-level diagram model, built from the
mer:fieldExampleValue facts that gate 080 requires on every scalar-required and enum field.

Two-level depth by design: a list/nested-ref field's element type is populated from that
element model's own scalar and enum facts only. A list nested one level further in is left
at its Pydantic default, so the example stays valid without three-level recursion.
"""

from mmdio.engine.models import (
    C4Diagram,
    C4Element,
    C4Relationship,
    ClassDefinition,
    ClassDiagram,
    ClassMember,
    ClassMethod,
    ClassRelationship,
    ERDiagram,
    ERRelationship,
    Entity,
    EntityAttribute,
    FlowchartDiagram,
    FlowchartEdge,
    FlowchartNode,
    GanttChart,
    GanttTask,
    GitBranch,
    GitCommit,
    GitGraph,
    Mindmap,
    MindmapNode,
    PieChart,
    PieSlice,
    SankeyDiagram,
    SankeyFlow,
    SequenceDiagram,
    SequenceMessage,
    SequenceParticipant,
    State,
    StateDiagram,
    Transition,
)
from mmdio.engine.enums import *  # noqa: F401,F403 — enum literals referenced below



def example_c4() -> C4Diagram:
    """One representative C4Diagram built from ontology example values."""
    return C4Diagram(elements=[C4Element(id="user", name="User", level=C4Level.C1, )], relationships=[C4Relationship(from_element="user", to_element="system", description="Uses", )], )


def example_class() -> ClassDiagram:
    """One representative ClassDiagram built from ontology example values."""
    return ClassDiagram(classes=[ClassDefinition(name="User", )], relationships=[ClassRelationship(from_class="User", to_class="Account", )], )


def example_er() -> ERDiagram:
    """One representative ERDiagram built from ontology example values."""
    return ERDiagram(entities=[Entity(name="USER", )], relationships=[ERRelationship(from_entity="USER", to_entity="ORDER", )], )


def example_flowchart() -> FlowchartDiagram:
    """One representative FlowchartDiagram built from ontology example values."""
    return FlowchartDiagram(nodes=[FlowchartNode(id="A", label="Start", )], edges=[FlowchartEdge(source="A", target="B", )], )


def example_gantt() -> GanttChart:
    """One representative GanttChart built from ontology example values."""
    return GanttChart(tasks=[GanttTask(id="task1", title="Design", start_date="2026-08-01", end_date="2026-08-03", )], )


def example_git() -> GitGraph:
    """One representative GitGraph built from ontology example values."""
    return GitGraph(commits=[GitCommit(id="c1", message="Initial commit", )], branches=[GitBranch(name="main", )], )


def example_mindmap() -> Mindmap:
    """One representative Mindmap built from ontology example values."""
    return Mindmap(root=MindmapNode(id="root", label="Root", ), nodes=[MindmapNode(id="root", label="Root", )], )


def example_pie() -> PieChart:
    """One representative PieChart built from ontology example values."""
    return PieChart(slices=[PieSlice(label="Complete", value=100.0, )], )


def example_sankey() -> SankeyDiagram:
    """One representative SankeyDiagram built from ontology example values."""
    return SankeyDiagram(flows=[SankeyFlow(source="A", target="B", value=100.0, )], )


def example_sequence() -> SequenceDiagram:
    """One representative SequenceDiagram built from ontology example values."""
    return SequenceDiagram(participants=[SequenceParticipant(id="A", name="Alice", )], messages=[SequenceMessage(from_participant="A", to_participant="B", label="Hello", )], )


def example_state() -> StateDiagram:
    """One representative StateDiagram built from ontology example values."""
    return StateDiagram(states=[State(id="Idle", label="Idle", )], transitions=[Transition(from_state="Idle", to_state="Active", )], )


GENERATED_FIXTURE_MODEL_CLASSES = {
    "c4": C4Diagram,
    "class": ClassDiagram,
    "er": ERDiagram,
    "flowchart": FlowchartDiagram,
    "gantt": GanttChart,
    "git": GitGraph,
    "mindmap": Mindmap,
    "pie": PieChart,
    "sankey": SankeyDiagram,
    "sequence": SequenceDiagram,
    "state": StateDiagram,
}

GENERATED_FIXTURE_BUILDERS = {
    "c4": example_c4,
    "class": example_class,
    "er": example_er,
    "flowchart": example_flowchart,
    "gantt": example_gantt,
    "git": example_git,
    "mindmap": example_mindmap,
    "pie": example_pie,
    "sankey": example_sankey,
    "sequence": example_sequence,
    "state": example_state,
}
