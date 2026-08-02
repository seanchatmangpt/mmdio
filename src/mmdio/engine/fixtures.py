"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""
from mmdio.engine.models import *  # noqa: F401,F403


def example_flowchart(): return FlowchartDiagram(nodes=[FlowchartNode(id="A",label="Start")],edges=[FlowchartEdge(source="A",target="B")])
def example_sequence(): return SequenceDiagram(title="Login Flow",participants=[SequenceParticipant(id="A",name="Alice")],messages=[SequenceMessage(from_participant="A",to_participant="B",label="Hello")])
def example_class(): return ClassDiagram(classes=[ClassDefinition(name="User",members=[ClassMember(name="id",type="int")])],relationships=[ClassRelationship(from_class="User",to_class="Account")])
def example_state(): return StateDiagram(states=[State(id="Idle",label="Idle",is_initial=True),State(id="Active",label="Active")],transitions=[Transition(from_state="Idle",to_state="Active",event="start")])
def example_er(): return ERDiagram(entities=[Entity(name="USER",attributes=[EntityAttribute(name="id",type="int",is_key=True)])],relationships=[ERRelationship(from_entity="USER",to_entity="ORDER",label="places")])
def example_gantt(): return GanttChart(title="Conversion Plan",tasks=[GanttTask(id="task1",title="Design",start_date="2026-08-01",end_date="2026-08-03")])
def example_pie(): return PieChart(title="Progress",slices=[PieSlice(label="Complete",value=100.0)])
def example_git(): return GitGraph(commits=[GitCommit(id="c1",message="Initial commit")],branches=[GitBranch(name="main",commit_ids=["c1"],is_main=True)])
def example_c4(): return C4Diagram(title="System Context",elements=[C4Element(id="user",name="User",level=C4Level.C1)],relationships=[])
def example_mindmap(): return Mindmap(title="Ideas",root=MindmapNode(id="root",label="Root",children=[MindmapNode(id="child",label="Child")]))
def example_sankey(): return SankeyDiagram(title="Energy Flow",flows=[SankeyFlow(source="A",target="B",value=100.0)])
