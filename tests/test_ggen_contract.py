from __future__ import annotations
import json
from mmdio.engine import models
from mmdio.engine.fixtures import *
from mmdio.engine.render_dispatch import GENERATED_RENDER_DISPATCH, render_diagram
from mmdio.engine.schemas import GENERATED_JSON_SCHEMAS


def test_all_admitted_models_dispatch_and_schema():
    examples=[example_flowchart(),example_sequence(),example_class(),example_state(),example_er(),example_gantt(),example_pie(),example_git(),example_c4(),example_mindmap(),example_sankey()]
    assert len(examples)==11
    assert len(GENERATED_RENDER_DISPATCH)==11
    assert len(GENERATED_JSON_SCHEMAS)==11
    for item in examples:
        text=render_diagram(item)
        assert text and "\n" not in text[:1]
        json.dumps(item.model_dump(mode="json"))


def test_parser_constructor_aliases_are_admitted():
    assert models.FlowchartNode(id="A",label="A",node_type="circle").shape == models.NodeShape.CIRCLE
    assert models.FlowchartEdge(source="A",target="B",edge_type="dotted").style == "dotted"
    assert models.SequenceParticipant(id="A",name="Alice",participant_type="actor").type == models.ParticipantType.ACTOR
    msg=models.SequenceMessage(from_id="A",to_id="B",label="x",message_type="async")
    assert (msg.from_participant,msg.to_participant,msg.type)==("A","B",models.MessageType.ASYNC)
    assert models.ClassMethod(name="save",type="bool").return_type == "bool"
    assert models.ClassRelationship(from_class="A",to_class="B",relation_type="dependency").type == models.RelationshipType.DEPENDENCY
    assert models.GitBranch(name="main",commits=["c1"]).commit_ids == ["c1"]
    rel=models.C4Relationship(from_id="a",to_id="b",description="uses")
    assert (rel.from_element,rel.to_element)==("a","b")
    mm=models.Mindmap(root=models.MindmapNode(id="r",label="R"),nodes=[])
    assert mm.root.id == "r"
