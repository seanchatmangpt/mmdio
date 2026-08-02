"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_fixtures.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonModel / mer:PythonField)

One example_{id}() builder per top-level diagram model, replacing the
hand-built sample AST each tests/oracle_types/test_oracle_{id}.py used to
construct inline. Two-level nesting limit, same as the render-body
template: a list/nested-ref field's element type gets exactly one example
instance built from that element model's own SCALAR fieldExampleValue
facts only — a list-kind field one level further in (e.g. KanbanSection's
own `cards` list, nested inside KanbanDiagram's `sections` list) is left
at its Pydantic default (empty list) rather than populated, so the
generated example stays valid without needing three-level recursion.
"""

from mmdio.engine.models import (

    Block,

    BlockDiagram,

    C4Diagram,

    C4Element,

    C4Relationship,

    ClassDefinition,

    ClassDiagram,

    ClassMember,

    ClassMethod,

    ClassRelationship,

    Connection,

    DataSeries,

    ERAttribute,

    ERDiagram,

    EREntity,

    ERRelationship,

    FlowchartDiagram,

    FlowchartEdge,

    FlowchartNode,

    GanttChart,

    GanttDependency,

    GanttTask,

    GitBranch,

    GitCommit,

    GitGraph,

    KanbanCard,

    KanbanDiagram,

    KanbanSection,

    Mindmap,

    MindmapNode,

    PieChart,

    PieSlice,

    SankeyDiagram,

    SankeyFlow,

    SequenceDiagram,

    SequenceMessage,

    SequenceParticipant,

    StateDiagram,

    StateNode,

    StateTransition,

    TimelineDiagram,

    TimelineEvent,

    XYAxis,

    XYChartDiagram,

)
from mmdio.engine.enums import *  # noqa: F401,F403 — enum literals referenced below









def example_block() -> BlockDiagram:
    """One representative BlockDiagram, built from ontology.ttl example values."""

    return BlockDiagram(





        blocks=[Block(


            id="A",



            label="Module A",


        )],




        connections=[Connection(


            source="A",



            target="B",






        )],


    )




def example_c4() -> C4Diagram:
    """One representative C4Diagram, built from ontology.ttl example values."""

    return C4Diagram(


        title="System Context",



        level=C4Level.C1,




        elements=[C4Element(


            id="user",



            name="User",



            description="A user of the system",



            type="Person",


        )],




        relationships=[C4Relationship(


            source="user",



            target="system",



            label="uses",


        )],


    )










def example_class() -> ClassDiagram:
    """One representative ClassDiagram, built from ontology.ttl example values."""

    return ClassDiagram(



        classes=[ClassDefinition(


            name="Animal",






        )],




        relationships=[ClassRelationship(


            from_class="Dog",



            to_class="Animal",



            type=RelationshipType.INHERITANCE,



            label="extends",


        )],


    )
















def example_er() -> ERDiagram:
    """One representative ERDiagram, built from ontology.ttl example values."""

    return ERDiagram(



        entities=[EREntity(


            name="USER",




        )],




        relationships=[ERRelationship(


            entity_a="USER",



            entity_b="ORDER",



            cardinality_a="|o",



            cardinality_b="o|",



            relation_type=RelationshipType.ASSOCIATION,


        )],


    )








def example_flowchart() -> FlowchartDiagram:
    """One representative FlowchartDiagram, built from ontology.ttl example values."""

    return FlowchartDiagram(





        nodes=[FlowchartNode(


            id="A",



            label="Process",



            node_type=NodeShape.RECTANGLE,


        )],




        edges=[FlowchartEdge(


            source="A",



            target="B",



            label="depends on",




        )],


    )








def example_gantt() -> GanttChart:
    """One representative GanttChart, built from ontology.ttl example values."""

    return GanttChart(


        title="Project Timeline",






        tasks=[GanttTask(


            id="task1",



            title="Phase 1",



            status=TaskStatus.ACTIVE,



            start_date="2024-01-01",



            end_date="2024-01-31",




        )],


    )












def example_git() -> GitGraph:
    """One representative GitGraph, built from ontology.ttl example values."""

    return GitGraph(





        commits=[GitCommit(


            id="abc1234",



            message="Initial commit",


        )],


    )






def example_kanban() -> KanbanDiagram:
    """One representative KanbanDiagram, built from ontology.ttl example values."""

    return KanbanDiagram(



        sections=[KanbanSection(


            name="To Do",




        )],


    )






def example_mindmap() -> Mindmap:
    """One representative Mindmap, built from ontology.ttl example values."""

    return Mindmap(



        root=MindmapNode(


            id="root",



            label="Root Node",


        ),



        title="My Mindmap",


    )






def example_pie() -> PieChart:
    """One representative PieChart, built from ontology.ttl example values."""

    return PieChart(


        title="Sales",




        slices=[PieSlice(


            label="Marketing",



            value=42.5,


        )],


    )






def example_sankey() -> SankeyDiagram:
    """One representative SankeyDiagram, built from ontology.ttl example values."""

    return SankeyDiagram(



        flows=[SankeyFlow(


            source="A",



            target="B",



            value=100,


        )],


    )






def example_sequence() -> SequenceDiagram:
    """One representative SequenceDiagram, built from ontology.ttl example values."""

    return SequenceDiagram(


        title="User Interaction",




        participants=[SequenceParticipant(


            id="A",



            name="User",



            participant_type=ParticipantType.PARTICIPANT,


        )],




        messages=[SequenceMessage(


            from_id="A",



            to_id="B",



            label="request",



            message_type=MessageType.SYNC,



            sequence_number=1,


        )],


    )








def example_state() -> StateDiagram:
    """One representative StateDiagram, built from ontology.ttl example values."""

    return StateDiagram(


        initial_state="[*]",




        states=[StateNode(


            id="state_1",



            label="Active",


        )],




        transitions=[StateTransition(


            source="state_1",



            target="state_2",



            label="event",


        )],


    )








def example_timeline() -> TimelineDiagram:
    """One representative TimelineDiagram, built from ontology.ttl example values."""

    return TimelineDiagram(


        title="Project Timeline",




        events=[TimelineEvent(


            time="2024-01-01",



            description="Phase 1 Start",


        )],


    )








def example_xychart() -> XYChartDiagram:
    """One representative XYChartDiagram, built from ontology.ttl example values."""

    return XYChartDiagram(


        title="Sales Data",




        x_axis=XYAxis(


            label="Month",








        ),




        y_axis=XYAxis(


            label="Month",








        ),




        series=[DataSeries(


            series_type="line",



            values=[10, 20, 30],


        )],


    )



