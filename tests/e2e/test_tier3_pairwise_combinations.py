"""
Tier 3 Cross-Feature Pairwise Interaction E2E Test Suite for mmdio.

Implements >=15 test cases validating pairwise interactions across 7 feature categories:
1. Diagram Detector ↔ Parser Registry
2. Parser ↔ AST Model discriminated union
3. AST Model ↔ Render Dispatcher
4. Renderer ↔ Node Mermaid 11.16.0 Oracle
5. Ontology SPARQL Law Gates ↔ Pytest Fixtures
6. Enum formatting (enum.StrEnum) ↔ String template rendering
7. Schema Export ↔ Model Validation
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import pytest
import rdflib
from pydantic import TypeAdapter, ValidationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tests.e2e.conftest import (
    GATES_DIR,
    ONTOLOGY_TTL,
    REGISTRY_TTL,
    validate_mermaid_source,
    verify_sparql_gates,
)

from mmdio.detect import detect_diagram_type
from mmdio.engine.detect_patterns import GENERATED_DETECT_PATTERNS
from mmdio.engine.enums import (
    C4Level,
    CardinityType,
    MessageType,
    NodeShape,
    ParticipantType,
    RelationshipType,
    TaskStatus,
)
from mmdio.engine.fixtures import (
    example_block,
    example_kanban,
    example_pie,
    example_sankey,
    example_timeline,
)
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
    GanttTask,
    GitBranch,
    GitCommit,
    GitGraph,
    KanbanCard,
    KanbanDiagram,
    KanbanSection,
    MermaidDiagram,
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
from mmdio.engine.parser import MermaidParser, ParsingError, parse_pie
from mmdio.engine.parser_registry import (
    GENERATED_GRAMMAR_FILES,
    GENERATED_TRANSFORMERS,
)
from mmdio.engine.render import render_diagram
from mmdio.engine.render_dispatch import GENERATED_RENDER_DISPATCH
from mmdio.engine.schemas import GENERATED_JSON_SCHEMAS
from mmdio.engine.supported import GENERATED_PYTHON_SUPPORTED


# ============================================================================
# CATEGORY 1: DIAGRAM DETECTOR ↔ PARSER REGISTRY
# ============================================================================

class TestPairwiseDetectorRegistry:
    """Pairwise interaction tests between Diagram Detector and Parser Registry."""

    def test_detector_to_registry_all_15_types(self, all_sample_diagram_sources: Dict[str, str]) -> None:
        """Verify detect_diagram_type output routes to a registered transformer for all 15 supported types."""
        assert len(all_sample_diagram_sources) == 15, "Expected 15 diagram source fixtures"
        id_alias_map = {"class": "classDiagram", "state": "stateDiagram", "git": "gitGraph"}
        for diagram_type, source_text in all_sample_diagram_sources.items():
            detected_id = detect_diagram_type(source_text)
            supported_id = id_alias_map.get(detected_id, detected_id)
            assert supported_id in GENERATED_PYTHON_SUPPORTED, (
                f"Supported ID '{supported_id}' for '{diagram_type}' is not in GENERATED_PYTHON_SUPPORTED"
            )
            assert detected_id in GENERATED_TRANSFORMERS, (
                f"Detected type '{detected_id}' for '{diagram_type}' is missing from GENERATED_TRANSFORMERS"
            )
            assert detected_id in GENERATED_GRAMMAR_FILES, (
                f"Detected type '{detected_id}' for '{diagram_type}' is missing from GENERATED_GRAMMAR_FILES"
            )

    def test_detector_fallback_to_registry(self) -> None:
        """Verify unrecognized or empty diagram headers fall back to 'flowchart' in parser registry."""
        fallback_id = detect_diagram_type("unrecognized_diagram_header_123\n  A --> B")
        assert fallback_id == "flowchart"
        assert fallback_id in GENERATED_TRANSFORMERS
        transformer = GENERATED_TRANSFORMERS[fallback_id]
        assert transformer.__class__.__name__ == "FlowchartTransformer"

    def test_detector_case_insensitivity_and_registry_lookup(self) -> None:
        """Verify mixed-case diagram headers detect correctly and map to parser registry transformers."""
        mixed_case_samples = [
            ("FLOWCHART TD\n  A --> B", "flowchart"),
            ("SeQuEnCeDiAgRaM\n  Alice->>Bob: Hi", "sequence"),
            ("cLaSsDiAgRaM\n  class Animal", "class"),
            ("ErDiAgRaM\n  CUSTOMER ||--o{ ORDER : places", "er"),
            ("pIe title Test\n  \"A\" : 10", "pie"),
        ]
        for raw_text, expected_internal_id in mixed_case_samples:
            detected_id = detect_diagram_type(raw_text)
            assert detected_id == expected_internal_id
            assert detected_id in GENERATED_TRANSFORMERS


# ============================================================================
# CATEGORY 2: PARSER ↔ AST MODEL DISCRIMINATED UNION
# ============================================================================

class TestPairwiseParserModelUnion:
    """Pairwise interaction tests between Parser and AST Model discriminated union."""

    def test_parser_output_satisfies_discriminated_union(self, sample_pie_source: str) -> None:
        """Verify parser output satisfies the MermaidDiagram discriminated union."""
        pie_ast = parse_pie(sample_pie_source)
        assert isinstance(pie_ast, PieChart)
        assert hasattr(pie_ast, "type")
        assert pie_ast.type == "pie"

        adapter = TypeAdapter(MermaidDiagram)
        validated_ast = adapter.validate_python(pie_ast.model_dump())
        assert isinstance(validated_ast, PieChart)
        assert validated_ast.type == "pie"

    def test_discriminated_union_model_validation_from_parsed_dict(self) -> None:
        """Verify AST dumped to dict can be re-validated into the MermaidDiagram union for multiple models."""
        adapter = TypeAdapter(MermaidDiagram)

        fc_ast = FlowchartDiagram(
            direction="TD",
            nodes=[FlowchartNode(id="A", label="Start", node_type=NodeShape.RECTANGLE)],
            edges=[FlowchartEdge(source="A", target="B", label="rel", edge_type="-->")],
        )
        fc_dict = fc_ast.model_dump()
        revalidated_fc = adapter.validate_python(fc_dict)
        assert isinstance(revalidated_fc, FlowchartDiagram)
        assert revalidated_fc.direction == fc_ast.direction

        pie_ast = PieChart(title="Pets", slices=[PieSlice(label="Dogs", value=50.0)])
        pie_dict = pie_ast.model_dump()
        revalidated_pie = adapter.validate_python(pie_dict)
        assert isinstance(revalidated_pie, PieChart)
        assert revalidated_pie.title == pie_ast.title

    def test_discriminated_union_invalid_type_raises_validation_error(self) -> None:
        """Verify dictionary payload with invalid discriminator raises Pydantic ValidationError."""
        adapter = TypeAdapter(MermaidDiagram)
        invalid_payload = {
            "type": "unsupported_diagram_xyz",
            "title": "Invalid Diagram",
        }
        with pytest.raises(ValidationError):
            adapter.validate_python(invalid_payload)


# ============================================================================
# CATEGORY 3: AST MODEL ↔ RENDER DISPATCHER
# ============================================================================

class TestPairwiseModelRenderDispatch:
    """Pairwise interaction tests between AST Models and Render Dispatcher."""

    def test_model_to_render_dispatch_all_15_types(self) -> None:
        """Verify render_diagram dispatches all 15 model types via GENERATED_RENDER_DISPATCH."""
        models_to_test = [
            FlowchartDiagram(direction="TD", nodes=[FlowchartNode(id="A", label="Start", node_type=NodeShape.RECTANGLE)]),
            SequenceDiagram(participants=[SequenceParticipant(id="Alice", name="Alice", participant_type=ParticipantType.PARTICIPANT)], messages=[SequenceMessage(from_id="Alice", to_id="Alice", message_type=MessageType.SYNC, sequence_number=1, label="Self")]),
            ClassDiagram(classes=[ClassDefinition(name="Animal")]),
            StateDiagram(states=[StateNode(id="Idle", label="Idle")]),
            ERDiagram(entities=[EREntity(name="USER")]),
            GanttChart(title="Gantt", tasks=[GanttTask(id="t1", title="Task 1", status=TaskStatus.ACTIVE, start_date="2024-01-01", end_date="2024-01-10")]),
            PieChart(title="Pie", slices=[PieSlice(label="Slice A", value=10.0)]),
            GitGraph(commits=[GitCommit(id="c1")]),
            C4Diagram(title="C4", level=C4Level.C1, elements=[C4Element(id="sys", name="System", description="Main System", type="Person")]),
            Mindmap(title="Root", root=MindmapNode(id="root", label="Root")),
            SankeyDiagram(flows=[SankeyFlow(source="A", target="B", value=5.0)]),
            example_kanban(),
            example_timeline(),
            XYChartDiagram(title="Chart", x_axis=XYAxis(label="X", values=["a", "b"]), y_axis=XYAxis(label="Y", range_min=0.0, range_max=100.0)),
            example_block(),
        ]
        for model in models_to_test:
            model_cls = model.__class__
            assert model_cls in GENERATED_RENDER_DISPATCH, (
                f"Model class {model_cls.__name__} missing from GENERATED_RENDER_DISPATCH"
            )
            rendered = render_diagram(model)
            assert isinstance(rendered, str)
            assert len(rendered.strip()) > 0

    def test_ast_mutation_to_render_dispatch(self) -> None:
        """Verify mutating an AST model updates rendered string output from render_diagram."""
        fc = FlowchartDiagram(direction="TD", nodes=[FlowchartNode(id="NodeA", label="Initial", node_type=NodeShape.RECTANGLE)])
        initial_render = render_diagram(fc)
        assert "NodeA" in initial_render
        assert "NodeB" not in initial_render

        # Mutate AST by adding a node and edge
        fc.nodes.append(FlowchartNode(id="NodeB", label="Updated", node_type=NodeShape.RECTANGLE))
        fc.edges.append(FlowchartEdge(source="NodeA", target="NodeB", label="rel", edge_type="-->"))
        updated_render = render_diagram(fc)
        assert "NodeA" in updated_render
        assert "NodeB" in updated_render

    def test_render_dispatcher_unregistered_model_raises_error(self) -> None:
        """Verify passing an unregistered model or object to render_diagram raises ValueError."""
        class DummyModel:
            pass

        with pytest.raises((ValueError, TypeError)):
            render_diagram(DummyModel())


# ============================================================================
# CATEGORY 4: RENDERER ↔ NODE MERMAID 11.16.0 ORACLE
# ============================================================================

class TestPairwiseRendererOracle:
    """Pairwise interaction tests between Renderer and Node Mermaid Oracle."""

    def test_rendered_flowchart_oracle_validation(self, oracle_validator: Callable[[str], str]) -> None:
        """Verify rendered flowchart AST passes Node oracle validation."""
        fc = FlowchartDiagram(
            direction="LR",
            nodes=[
                FlowchartNode(id="A", label="Start", node_type=NodeShape.RECTANGLE),
                FlowchartNode(id="B", label="Decision", node_type=NodeShape.DIAMOND),
            ],
            edges=[
                FlowchartEdge(source="A", target="B", label="Go", edge_type="-->"),
            ]
        )
        rendered_text = render_diagram(fc)
        oracle_output = oracle_validator(rendered_text)
        assert "SUCCESS" in oracle_output

    def test_rendered_sequence_and_c4_oracle_validation(self, oracle_validator: Callable[[str], str]) -> None:
        """Verify rendered Sequence and C4 diagrams pass Node oracle validation."""
        seq = SequenceDiagram(
            autonumber=True,
            participants=[
                SequenceParticipant(id="Alice", name="Alice", participant_type=ParticipantType.ACTOR),
                SequenceParticipant(id="Bob", name="Bob", participant_type=ParticipantType.PARTICIPANT),
            ],
            messages=[
                SequenceMessage(from_id="Alice", to_id="Bob", label="Ping", message_type=MessageType.SYNC, sequence_number=1),
            ]
        )
        seq_rendered = render_diagram(seq)
        oracle_validator(seq_rendered)

        c4 = C4Diagram(
            title="System Architecture",
            level=C4Level.C1,
            elements=[
                C4Element(id="user", name="User", description="Banking Customer", type="Person"),
            ],
            relationships=[
                C4Relationship(source="user", target="app", label="Uses"),
            ]
        )
        c4_rendered = render_diagram(c4)
        oracle_validator(c4_rendered)

    def test_rendered_pie_and_sankey_oracle_validation(self, oracle_validator: Callable[[str], str]) -> None:
        """Verify rendered Pie and Sankey diagrams pass Node oracle validation."""
        pie = PieChart(
            title="Market Share",
            slices=[
                PieSlice(label="Alpha", value=60.0),
                PieSlice(label="Beta", value=40.0),
            ]
        )
        pie_rendered = render_diagram(pie)
        oracle_output = oracle_validator(pie_rendered)
        assert "SUCCESS" in oracle_output

        sankey = SankeyDiagram(
            flows=[
                SankeyFlow(source="SourceA", target="TargetB", value=10.5),
            ]
        )
        sankey_rendered = render_diagram(sankey)
        oracle_validator(sankey_rendered)


# ============================================================================
# CATEGORY 5: ONTOLOGY SPARQL LAW GATES ↔ PYTEST FIXTURES
# ============================================================================

class TestPairwiseOntologyGatesFixtures:
    """Pairwise interaction tests between Ontology SPARQL Law Gates and Pytest Fixtures."""

    def test_sparql_gate_080_scalar_examples_match_fixtures(self) -> None:
        """Verify scalar example values from Gate 080 exist in ontology and match fixture definitions."""
        graph = rdflib.Graph()
        graph.parse(str(REGISTRY_TTL), format="turtle")
        graph.parse(str(ONTOLOGY_TTL), format="turtle")

        query = """
        PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
        SELECT ?field ?name ?exampleValue WHERE {
            ?field a mer:PythonField ;
                   mer:fieldName ?name ;
                   mer:fieldExampleValue ?exampleValue .
        }
        """
        results = list(graph.query(query))
        assert len(results) > 0, "No fieldExampleValue entries found in ontology"

        example_names = {str(row.name) for row in results}
        assert "direction" in example_names or "id" in example_names or "title" in example_names

        # Verify auto-generated fixtures load correctly
        block_ast = example_block()
        assert block_ast is not None
        assert len(block_ast.blocks) > 0

        kanban_ast = example_kanban()
        assert kanban_ast is not None
        assert len(kanban_ast.sections) > 0

    def test_sparql_gate_010_completeness_matches_fixture_inventory(
        self,
        all_sample_diagram_sources: Dict[str, str],
    ) -> None:
        """Verify all pythonSupport true types in SPARQL Gate 010 match the sample fixture inventory."""
        graph = rdflib.Graph()
        graph.parse(str(REGISTRY_TTL), format="turtle")
        graph.parse(str(ONTOLOGY_TTL), format="turtle")

        query = """
        PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
        SELECT ?internalId WHERE {
            ?type a mer:DiagramType ;
                  mer:pythonInternalId ?internalId .
        }
        """
        ontology_ids = {str(row.internalId) for row in graph.query(query)}
        assert len(ontology_ids) >= 15

        fixture_keys = set(all_sample_diagram_sources.keys())
        for ont_id in ontology_ids:
            assert ont_id in fixture_keys or ont_id in ["class", "state", "git"] or any(
                ont_id in k for k in fixture_keys
            ), f"Ontology type '{ont_id}' missing from sample fixture inventory"

    def test_sparql_gate_070_enum_classes_match_fixtures(self) -> None:
        """Verify enum classes from Gate 070 (enum_class_exists) map to python enums used in fixtures."""
        graph = rdflib.Graph()
        graph.parse(str(REGISTRY_TTL), format="turtle")
        graph.parse(str(ONTOLOGY_TTL), format="turtle")

        query = """
        PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
        SELECT DISTINCT ?enumClassName WHERE {
            ?enum a mer:PythonEnum ;
                  mer:enumClassName ?enumClassName .
        }
        """
        enum_names = {str(row.enumClassName) for row in graph.query(query)}
        expected_enums = {
            "NodeShape",
            "MessageType",
            "RelationshipType",
            "CardinityType",
            "TaskStatus",
            "C4Level",
            "ParticipantType",
        }
        assert expected_enums.issubset(enum_names), f"Missing enums in ontology: {expected_enums - enum_names}"

        node = FlowchartNode(id="A", label="Node A", node_type=NodeShape.DIAMOND)
        assert node.node_type == NodeShape.DIAMOND


# ============================================================================
# CATEGORY 6: ENUM FORMATTING (enum.StrEnum) ↔ STRING TEMPLATE RENDERING
# ============================================================================

class TestPairwiseEnumFormattingTemplates:
    """Pairwise interaction tests between Enum formatting (StrEnum) and String Template Rendering."""

    def test_strenum_formatting_flowchart_shapes(self) -> None:
        """Verify StrEnum shapes format as bare string tokens in rendered flowchart text."""
        fc = FlowchartDiagram(
            direction="TD",
            nodes=[
                FlowchartNode(id="N1", label="Rect", node_type=NodeShape.RECTANGLE),
                FlowchartNode(id="N2", label="Dec", node_type=NodeShape.DIAMOND),
            ],
            edges=[
                FlowchartEdge(source="N1", target="N2", label="rel", edge_type="-->"),
            ]
        )
        rendered = render_diagram(fc)
        assert "NodeShape." not in rendered, "Rendered text contains polluted 'NodeShape.' prefix"
        assert ".value" not in rendered
        assert "N1" in rendered and "N2" in rendered

    def test_strenum_formatting_sequence_messages(self) -> None:
        """Verify MessageType StrEnum formats as correct arrow syntax without enum class pollution."""
        seq = SequenceDiagram(
            participants=[
                SequenceParticipant(id="A", name="A", participant_type=ParticipantType.PARTICIPANT),
                SequenceParticipant(id="B", name="B", participant_type=ParticipantType.PARTICIPANT),
            ],
            messages=[
                SequenceMessage(from_id="A", to_id="B", label="msg1", message_type=MessageType.SYNC, sequence_number=1),
            ]
        )
        rendered = render_diagram(seq)
        assert "MessageType." not in rendered
        assert "A" in rendered and "B" in rendered

    def test_strenum_formatting_c4_and_class(self) -> None:
        """Verify StrEnum formatting in C4 and Class diagram rendering."""
        c4 = C4Diagram(
            title="C1 Context",
            level=C4Level.C1,
            elements=[C4Element(id="sys", name="Main System", description="Core App", type="System")],
        )
        rendered_c4 = render_diagram(c4)
        assert "C4Level." not in rendered_c4
        assert "Main System" in rendered_c4

        cls_diag = ClassDiagram(
            classes=[
                ClassDefinition(name="Base"),
                ClassDefinition(name="Derived"),
            ],
            relationships=[
                ClassRelationship(from_class="Derived", to_class="Base", type=RelationshipType.INHERITANCE, label="extends")
            ]
        )
        rendered_cls = render_diagram(cls_diag)
        assert "RelationshipType." not in rendered_cls
        assert "Base" in rendered_cls and "Derived" in rendered_cls


# ============================================================================
# CATEGORY 7: SCHEMA EXPORT ↔ MODEL VALIDATION
# ============================================================================

class TestPairwiseSchemaExportModelValidation:
    """Pairwise interaction tests between Schema Export and Model Validation."""

    def test_json_schema_export_completeness(self) -> None:
        """Verify GENERATED_JSON_SCHEMAS contains valid object schemas for supported diagram types."""
        assert isinstance(GENERATED_JSON_SCHEMAS, dict)
        assert len(GENERATED_JSON_SCHEMAS) >= 5
        for schema_key, schema_dict in GENERATED_JSON_SCHEMAS.items():
            assert isinstance(schema_dict, dict)
            assert schema_dict.get("type") == "object"
            assert "properties" in schema_dict

    def test_schema_export_properties_match_pydantic_fields(self) -> None:
        """Verify Pydantic model_json_schema properties match expected field definitions."""
        fc_schema = FlowchartDiagram.model_json_schema()
        assert fc_schema["type"] == "object"
        assert "properties" in fc_schema
        assert "direction" in fc_schema["properties"]
        assert "nodes" in fc_schema["properties"]
        assert "edges" in fc_schema["properties"]

        seq_schema = SequenceDiagram.model_json_schema()
        assert "properties" in seq_schema
        assert "participants" in seq_schema["properties"]
        assert "messages" in seq_schema["properties"]

    def test_model_validation_against_schema_derived_payloads(self) -> None:
        """Verify valid AST dictionary payloads pass model validation while invalid payloads fail."""
        valid_flowchart_payload = {
            "type": "flowchart",
            "direction": "LR",
            "nodes": [{"id": "A", "label": "Start", "node_type": "rectangle"}],
            "edges": [{"source": "A", "target": "B", "label": None, "edge_type": "-->"}],
        }
        fc_model = FlowchartDiagram.model_validate(valid_flowchart_payload)
        assert fc_model.direction == "LR"
        assert len(fc_model.nodes) == 1

        invalid_flowchart_payload = {
            "type": "flowchart",
            "direction": "LR",
            "nodes": "not_a_list",  # Invalid type for nodes list
        }
        with pytest.raises(ValidationError):
            FlowchartDiagram.model_validate(invalid_flowchart_payload)
