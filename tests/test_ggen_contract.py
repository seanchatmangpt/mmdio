"""Contract tests for the RDF/ggen conversion boundary."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import BaseModel
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from mmdio.detect import detect_diagram_type
from mmdio.engine import (
    C4Diagram,
    ClassDiagram,
    ERDiagram,
    FlowchartDiagram,
    GanttChart,
    GitGraph,
    Mindmap,
    PieChart,
    SankeyDiagram,
    SequenceDiagram,
    StateDiagram,
    is_supported,
    parse_mermaid,
    render_diagram,
    render_model,
    schema_for_type,
)
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

ROOT = Path(__file__).resolve().parents[1]
MMDIO = Namespace("https://seanchatmangpt.github.io/ontology/mermaid#")
EXPECTED_TYPES: dict[str, tuple[str, type[BaseModel], Callable[[], BaseModel], str]] = {
    "c4": ("c4", C4Diagram, example_c4, "C4Context\n"),
    "classDiagram": ("class", ClassDiagram, example_class, "classDiagram\n"),
    "er": ("er", ERDiagram, example_er, "erDiagram\n"),
    "flowchart": ("flowchart", FlowchartDiagram, example_flowchart, "flowchart TD\n"),
    "gantt": ("gantt", GanttChart, example_gantt, "gantt\n"),
    "gitGraph": ("git", GitGraph, example_git, "gitGraph\n"),
    "mindmap": ("mindmap", Mindmap, example_mindmap, "mindmap\n  root\n"),
    "pie": ("pie", PieChart, example_pie, 'pie\n  "A": 1\n'),
    "sankey": ("sankey", SankeyDiagram, example_sankey, "sankey-beta\nA,B,1\n"),
    "sequence": ("sequence", SequenceDiagram, example_sequence, "sequenceDiagram\n"),
    "stateDiagram": ("state", StateDiagram, example_state, "stateDiagram-v2\n"),
}


@pytest.fixture(scope="module")
def graph() -> Graph:
    """Load the canonical Mermaid registry and executable model ontology."""
    result = Graph()
    result.parse(ROOT / "src/mmdio/engine/registry.ttl")
    result.parse(ROOT / "packs/mmdio-pack/ontology.ttl")
    return result


def test_registry_contains_all_mermaid_types(graph: Graph) -> None:
    diagram_types = set(graph.subjects(RDF.type, MMDIO.DiagramType))
    assert len(diagram_types) == 39
    assert sum(bool(graph.value(item, MMDIO.pythonSupport)) for item in diagram_types) == 11


@pytest.mark.parametrize(
    ("canonical_id", "case"),
    EXPECTED_TYPES.items(),
    ids=EXPECTED_TYPES,
)
def test_model_dispatch_schema_and_support(
    canonical_id: str,
    case: tuple[str, type[BaseModel], Callable[[], BaseModel], str],
) -> None:
    internal_id, model_class, factory, source = case
    model = factory()
    assert isinstance(model, model_class)
    assert is_supported(canonical_id)
    assert is_supported(internal_id)
    assert detect_diagram_type(source) == internal_id
    assert schema_for_type(canonical_id)["title"] == model_class.__name__
    assert render_model(model) == render_diagram(model)


@pytest.mark.parametrize(
    "gate",
    sorted((ROOT / "packs/mmdio-pack/gates").glob("*.rq")),
)
def test_all_sparql_gates_pass(graph: Graph, gate: Path) -> None:
    results = list(graph.query(gate.read_text(encoding="utf-8")))
    assert not results, f"{gate.name}: {results}"


def test_detection_patterns_are_runtime_regexes(graph: Graph) -> None:
    samples = {canonical_id: case[3] for canonical_id, case in EXPECTED_TYPES.items()}
    for subject, pattern in graph.subject_objects(MMDIO.detectPattern):
        canonical_id = str(graph.value(subject, MMDIO.diagramId))
        if canonical_id not in samples:
            continue
        match = re.search(
            str(pattern),
            samples[canonical_id],
            re.IGNORECASE | re.MULTILINE,
        )
        assert match is not None


def test_alias_validation_and_schemas_are_json_serializable() -> None:
    flowchart = FlowchartDiagram(nodes=[{"id": "start", "label": "Start", "node_type": "circle"}])
    sequence = SequenceDiagram(
        participants=[{"id": "alice", "name": "Alice", "participant_type": "actor"}],
        messages=[{"from_id": "alice", "to_id": "bob", "label": "hello"}],
    )
    class_diagram = ClassDiagram(
        classes=[{"name": "User", "methods": [{"name": "save", "type": "bool"}]}],
    )

    assert flowchart.nodes[0].shape.value == "circle"
    assert sequence.participants[0].type.value == "actor"
    assert sequence.messages[0].from_participant == "alice"
    assert class_diagram.classes[0].methods[0].return_type == "bool"
    schema = schema_for_type("flowchart")
    assert json.loads(json.dumps(schema, sort_keys=True)) == schema


def test_parser_accepts_flowchart_smoke_sample() -> None:
    model = parse_mermaid("flowchart TD\n    start[Start]\n")
    assert isinstance(model, FlowchartDiagram)
    assert model.nodes
    assert model.nodes[0].id == "start"
