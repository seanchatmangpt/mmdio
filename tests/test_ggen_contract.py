"""Contract tests for the bounded RDF-backed ggen conversion."""

from __future__ import annotations

import json

from mmdio.engine import models
from mmdio.engine.fixtures import (
    example_c4,
    example_class,
    example_er,
    example_flowchart,
    example_gantt,
    example_git,
    example_mindmap,
    example_pie,
    example_sankey,
    example_sequence,
    example_state,
)
from mmdio.engine.render_dispatch import GENERATED_RENDER_DISPATCH, render_diagram
from mmdio.engine.schemas import GENERATED_JSON_SCHEMAS


def test_all_admitted_models_dispatch_and_schema() -> None:
    examples = [
        example_flowchart(),
        example_sequence(),
        example_class(),
        example_state(),
        example_er(),
        example_gantt(),
        example_pie(),
        example_git(),
        example_c4(),
        example_mindmap(),
        example_sankey(),
    ]
    assert len(examples) == 11
    assert len(GENERATED_RENDER_DISPATCH) == 11
    assert len(GENERATED_JSON_SCHEMAS) == 11
    for item in examples:
        rendered = render_diagram(item)
        assert rendered and "\n" not in rendered[:1]
        assert json.dumps(item.model_dump(mode="json"))


def test_parser_constructor_aliases_are_admitted() -> None:
    flowchart_node = models.FlowchartNode.model_validate(
        {"id": "A", "label": "A", "node_type": "circle"},
    )
    assert flowchart_node.shape == models.NodeShape.CIRCLE

    flowchart_edge = models.FlowchartEdge.model_validate(
        {"source": "A", "target": "B", "edge_type": "dotted"},
    )
    assert flowchart_edge.style == "dotted"

    participant = models.SequenceParticipant.model_validate(
        {"id": "A", "name": "Alice", "participant_type": "actor"},
    )
    assert participant.type == models.ParticipantType.ACTOR

    message = models.SequenceMessage.model_validate(
        {
            "from_id": "A",
            "to_id": "B",
            "label": "x",
            "message_type": "async",
        },
    )
    assert message.from_participant == "A"
    assert message.to_participant == "B"
    assert message.type == models.MessageType.ASYNC

    class_method = models.ClassMethod.model_validate({"name": "save", "type": "bool"})
    assert class_method.return_type == "bool"
    relationship = models.ClassRelationship.model_validate(
        {
            "from_class": "A",
            "to_class": "B",
            "relation_type": "dependency",
        },
    )
    assert relationship.type == models.RelationshipType.DEPENDENCY
    git_branch = models.GitBranch.model_validate(
        {"name": "main", "commits": ["c1"]},
    )
    assert git_branch.commit_ids == ["c1"]

    c4_relationship = models.C4Relationship.model_validate(
        {"from_id": "a", "to_id": "b", "description": "uses"},
    )
    assert c4_relationship.from_element == "a"
    assert c4_relationship.to_element == "b"

    mindmap = models.Mindmap(
        root=models.MindmapNode(id="r", label="R"),
        nodes=[],
    )
    assert mindmap.root.id == "r"
