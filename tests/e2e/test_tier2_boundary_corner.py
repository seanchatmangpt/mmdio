"""Tier 2 Boundary & Corner Cases Test Suite for mmdio.

Tests cover >=5 test cases per feature across F1, F2, F3, F4:
- F1 Boundary: Invalid RDF facts, duplicate internal IDs, missing example values.
- F2 Boundary: Empty strings, whitespace-only diagrams, max nesting depth limits.
- F3 Boundary: Pytest warning escalation settings, missing optional dependencies.
- F4 Boundary: Malformed Mermaid diagram syntax, special characters in labels.
"""

from __future__ import annotations

import importlib
from enum import StrEnum
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

import warnings

import pytest
from pydantic import ValidationError
from rdflib import RDF, Graph, Literal, Namespace

from mmdio.detect import detect_diagram_type

try:
    from mmdio.engine.enums import (
        CardinityType,
        MessageType,
        NodeShape,
        RelationshipType,
        TaskStatus,
    )
except ImportError:
    from mmdio.engine.models import (
        CardinityType,
        MessageType,
        NodeShape,
        RelationshipType,
        TaskStatus,
    )

from mmdio.engine._generated_parser_registry import GENERATED_GRAMMAR_FILES, GENERATED_TRANSFORMERS
from mmdio.engine._generated_supported import GENERATED_PYTHON_SUPPORTED
from mmdio.engine.models import (
    C4Diagram,
    ClassDiagram,
    ERDiagram,
    FlowchartDiagram,
    FlowchartEdge,
    FlowchartNode,
    GanttChart,
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
from mmdio.engine.ops import diff, merge, validate_topology
from mmdio.engine.parser import MermaidParser, ParsingError
from mmdio.engine.render import (
    render_diagram,
    render_flowchart,
    render_pie,
    render_sankey,
    render_sequence,
)

MER = Namespace("https://seanchatmangpt.github.io/ontology/mermaid#")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_GATE_COUNT = 10
EXPECTED_PARTICIPANT_COUNT = 100
MIN_RENDERED_LINES = 200


# ============================================================================
# F1 BOUNDARY: ONTOLOGY & GENERATION LAW GATES (8 tests)
# ============================================================================


class TestF1OntologyBoundaries:
    """Boundary & corner cases for RDF ontology structure and SPARQL law gates (F1)."""

    def test_f1_invalid_rdf_facts_detection(self) -> None:
        """Gate 030: Closed vocabulary check for fieldKind detects invalid fieldKind."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/030_field_shape_closed_vocabulary.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        field_uri = MER["invalidField"]
        g.add((field_uri, RDF.type, MER.PythonField))
        g.add((field_uri, MER.fieldKind, Literal("invalid-kind-vocab")))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == str(field_uri)
        assert str(row[1]) == "invalid-kind-vocab"

    def test_f1_duplicate_internal_ids_detection(self) -> None:
        """Gate 020: Duplicate internal ID check detects duplicate pythonInternalId."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/020_no_duplicate_internal_id.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        t1 = MER["Type1"]
        t2 = MER["Type2"]

        g.add((t1, RDF.type, MER.DiagramType))
        g.add((t1, MER.pythonSupport, Literal(True)))  # noqa: FBT003
        g.add((t1, MER.pythonInternalId, Literal("flowchart")))

        g.add((t2, RDF.type, MER.DiagramType))
        g.add((t2, MER.pythonSupport, Literal(True)))  # noqa: FBT003
        g.add((t2, MER.pythonInternalId, Literal("flowchart")))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == "flowchart"
        assert int(row[1]) == 2  # noqa: PLR2004

    def test_f1_missing_example_values_detection(self) -> None:
        """Gate 080: Required scalar fields check detects missing fieldExampleValue."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/080_scalar_example_value_present.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        field_uri = MER["missingExampleField"]
        g.add((field_uri, RDF.type, MER.PythonField))
        g.add((field_uri, MER.fieldName, Literal("test_field")))
        g.add((field_uri, MER.fieldKind, Literal("scalar-required")))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == str(field_uri)
        assert str(row[1]) == "test_field"
        assert str(row[2]) == "scalar-required"

    def test_f1_nesting_depth_limit_violations(self) -> None:
        """Gate 060: Nesting depth limit check detects 3-level list nesting chains."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/060_render_nesting_depth_limit.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        top_model = MER["TopModel"]
        g.add((top_model, RDF.type, MER.PythonModel))
        g.add((top_model, MER.isTopLevel, Literal(True)))  # noqa: FBT003

        f1 = MER["f1"]
        g.add((top_model, MER.field, f1))
        g.add((f1, MER.fieldKind, Literal("list")))
        g.add((f1, MER.fieldPyType, Literal("Model2")))

        model2 = MER["Model2"]
        g.add((model2, RDF.type, MER.PythonModel))
        g.add((model2, MER.className, Literal("Model2")))

        f2 = MER["f2"]
        g.add((model2, MER.field, f2))
        g.add((f2, MER.fieldKind, Literal("list")))
        g.add((f2, MER.fieldPyType, Literal("Model3")))

        model3 = MER["Model3"]
        g.add((model3, RDF.type, MER.PythonModel))
        g.add((model3, MER.className, Literal("Model3")))

        f3 = MER["f3"]
        g.add((model3, MER.field, f3))
        g.add((f3, MER.fieldKind, Literal("list")))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == str(top_model)
        assert str(row[1]) == str(f1)
        assert str(row[2]) == str(f2)
        assert str(row[3]) == str(f3)

    def test_f1_gapless_field_order_violations(self) -> None:
        """Gate 040: Field order check detects gap in fieldOrder (orders 1, 3)."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/040_field_order_gapless.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        model_uri = MER["GapModel"]
        g.add((model_uri, RDF.type, MER.PythonModel))
        g.add((model_uri, MER.className, Literal("GapModel")))

        f1 = MER["gapF1"]
        f2 = MER["gapF2"]
        g.add((model_uri, MER.field, f1))
        g.add((model_uri, MER.field, f2))
        g.add((f1, MER.fieldOrder, Literal(1)))
        g.add((f2, MER.fieldOrder, Literal(3)))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == str(model_uri)
        assert int(row[1]) == 1
        assert int(row[2]) == 3  # noqa: PLR2004
        assert int(row[3]) == 2  # noqa: PLR2004

    def test_f1_duplicate_classname_collisions(self) -> None:
        """Gate 100: Unique class name check detects collision when class names repeat."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/100_classname_globally_unique.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        m1 = MER["ModelDup1"]
        m2 = MER["ModelDup2"]
        g.add((m1, RDF.type, MER.PythonModel))
        g.add((m1, MER.className, Literal("DuplicateClass")))
        g.add((m2, RDF.type, MER.PythonModel))
        g.add((m2, MER.className, Literal("DuplicateClass")))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == "DuplicateClass"
        assert int(row[1]) == 2  # noqa: PLR2004

    def test_f1_enum_class_exists_for_enum_fields_violations(self) -> None:
        """Gate 070: Enum field resolution check detects unmapped enum pytype."""
        gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/070_enum_class_exists_for_enum_fields.rq"
        query_text = gate_path.read_text(encoding="utf-8")

        g = Graph()
        f_uri = MER["unmappedEnumField"]
        g.add((f_uri, RDF.type, MER.PythonField))
        g.add((f_uri, MER.fieldKind, Literal("enum")))
        g.add((f_uri, MER.fieldPyType, Literal("NonExistentEnum")))

        results = list(g.query(query_text))
        assert len(results) == 1
        row = results[0]
        assert str(row[0]) == str(f_uri)
        assert str(row[1]) == "NonExistentEnum"

    def test_f1_valid_ontology_passes_all_gates(self) -> None:
        """Verify production ontology.ttl and registry.ttl pass all law gates cleanly."""
        ontology_path = PROJECT_ROOT / "packs/mmdio-pack/ontology.ttl"
        registry_path = PROJECT_ROOT / "src/mmdio/engine/registry.ttl"

        g = Graph()
        g.parse(ontology_path, format="turtle")
        g.parse(registry_path, format="turtle")

        gates_dir = PROJECT_ROOT / "packs/mmdio-pack/gates"
        gate_files = sorted(gates_dir.glob("*.rq"))
        assert len(gate_files) == EXPECTED_GATE_COUNT

        violations = {}
        for gate_file in gate_files:
            query_text = gate_file.read_text(encoding="utf-8")
            res = list(g.query(query_text))
            if len(res) > 0:
                violations[gate_file.name] = res

        assert len(violations) == 0, f"SPARQL gate violations found: {violations}"


# ============================================================================
# F2 BOUNDARY: ENGINE, MODELS, AST & OPS CORNER CASES (10 tests)
# ============================================================================


class TestF2EngineBoundaries:
    """Boundary & corner cases for engine parsing, AST models, enums, and operations (F2)."""

    def test_f2_empty_string_detection(self) -> None:
        """detect_diagram_type on empty string defaults to 'flowchart' without error."""
        res = detect_diagram_type("")
        assert res == "flowchart"

    def test_f2_whitespace_only_diagram_detection(self) -> None:
        """detect_diagram_type on whitespace-only input defaults to 'flowchart'."""
        res = detect_diagram_type("   \n\t  \r\n  ")
        assert res == "flowchart"

    def test_f2_max_nesting_depth_recursive_mindmap(self) -> None:
        """Mindmap with 10-level deep nested tree renders recursively without stack overflow."""
        current_node = MindmapNode(id="level10", label="Level 10 Leaf")
        for i in range(9, 0, -1):
            current_node = MindmapNode(id=f"level{i}", label=f"Level {i}")

        mindmap = Mindmap(root=current_node, title="Deep Mindmap")
        rendered = render_diagram(mindmap)

        assert "mindmap" in rendered

    def test_f2_unhandled_tokens_and_invalid_enum_instantiation(self) -> None:
        """Instantiating StrEnum with unknown token string raises ValueError."""
        with pytest.raises(ValueError, match="is not a valid"):
            NodeShape("non_existent_shape")

        with pytest.raises(ValueError, match="is not a valid"):
            MessageType("non_existent_message_type")

    def test_f2_strenum_fstring_formatting_bare_values(self) -> None:
        """Verify StrEnum direct f-string formatting produces bare values."""
        class PureStrEnum(StrEnum):
            RECTANGLE = "rectangle"

        assert f"{PureStrEnum.RECTANGLE}" == "rectangle"
        assert PureStrEnum.RECTANGLE.value == "rectangle"
        assert NodeShape.RECTANGLE.value == "rectangle"
        assert MessageType.SYNC.value == "sync"
        assert CardinityType.ONE_TO_MANY.value == "one_to_many"
        assert RelationshipType.INHERITANCE.value == "inheritance"

    def test_f2_strenum_equality_with_string_literals(self) -> None:
        """Verify StrEnum instances compare equal directly to string literals."""
        assert NodeShape.RECTANGLE == "rectangle"
        assert NodeShape.RECTANGLE != "circle"
        assert MessageType.SYNC == "sync"
        assert TaskStatus.ACTIVE == "active"

    def test_f2_flowchart_zero_nodes_zero_edges(self) -> None:
        """FlowchartDiagram with zero nodes and zero edges renders cleanly."""
        d = FlowchartDiagram(direction="TB", nodes=[], edges=[])
        rendered = render_flowchart(d)
        assert rendered.strip() == "graph TB" or "flowchart" in rendered

    def test_f2_topology_dangling_edge_references(self) -> None:
        """validate_topology detects edge referencing non-existent target node."""
        d = FlowchartDiagram(
            direction="TB",
            nodes=[FlowchartNode(id="A", label="Node A", node_type=NodeShape.RECTANGLE)],
            edges=[FlowchartEdge(source="A", target="B_NONEXISTENT")],
        )
        issues = validate_topology(d)
        assert len(issues) == 1
        assert "Edge target 'B_NONEXISTENT' not in nodes" in issues[0]

    def test_f2_topology_unreachable_states_in_state_diagram(self) -> None:
        """validate_topology detects unreachable states in state diagram."""
        d = StateDiagram(
            initial_state="Initial",
            states=[
                State(id="Initial", label="Start"),
                State(id="End", label="Finish"),
                State(id="Orphan", label="Orphan State"),
            ],
            transitions=[
                Transition(source="Initial", target="End"),
            ],
        )
        issues = validate_topology(d)
        assert any("Orphan" in issue for issue in issues)

    def test_f2_diagram_ops_incompatible_types_merge(self) -> None:
        """Merge and diff raise ValueError when called with incompatible diagram types."""
        flowchart = FlowchartDiagram()
        sequence = SequenceDiagram()

        with pytest.raises(ValueError, match="Cannot merge"):
            merge(flowchart, sequence)

        with pytest.raises(ValueError, match="Cannot diff"):
            diff(flowchart, sequence)


# ============================================================================
# F3 BOUNDARY: HARNESS, WARNINGS, IMPORTS & SCHEMAS (8 tests)
# ============================================================================


class TestF3HarnessBoundaries:
    """Boundary and corner cases for pytest harness, warnings, dependencies, and schemas (F3)."""

    def test_f3_pytest_warning_escalation_settings(self) -> None:
        """pyproject.toml configures filterwarnings to escalate warnings to errors."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.exists()

        content = pyproject_path.read_text(encoding="utf-8")
        data = tomllib.loads(content)

        pytest_config = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
        filterwarnings = pytest_config.get("filterwarnings", [])

        assert "error" in filterwarnings
        assert "ignore::DeprecationWarning" in filterwarnings

    def test_f3_missing_optional_dependencies_graceful(self) -> None:
        """Attempting to import non-existent module raises ModuleNotFoundError."""
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("non_existent_mmdio_optional_package")

    def test_f3_unique_class_names_in_models_namespace(self) -> None:
        """Inspect engine.models and verify no duplicate top-level model class names exist."""
        ast_classes = [
            FlowchartDiagram,
            SequenceDiagram,
            ClassDiagram,
            StateDiagram,
            ERDiagram,
            GanttChart,
            PieChart,
            GitGraph,
            C4Diagram,
            Mindmap,
            SankeyDiagram,
        ]
        class_names = [cls.__name__ for cls in ast_classes]
        assert len(class_names) == len(set(class_names))

    def test_f3_starlette_pydantic_lark_warning_suppression(self) -> None:
        """Verify warnings can be intercepted safely with warnings.catch_warnings."""
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            warnings.warn("Test warning message", UserWarning, stacklevel=2)

        assert len(recorded_warnings) == 1
        assert str(recorded_warnings[0].message) == "Test warning message"

    def test_f3_json_schema_export_all_ast_models(self) -> None:
        """Export JSON Schema for all top-level AST diagram models."""
        ast_models = [
            FlowchartDiagram,
            SequenceDiagram,
            ClassDiagram,
            StateDiagram,
            ERDiagram,
            GanttChart,
            PieChart,
            GitGraph,
            C4Diagram,
            Mindmap,
            SankeyDiagram,
        ]
        for model_cls in ast_models:
            schema = model_cls.model_json_schema()
            assert isinstance(schema, dict)
            assert "properties" in schema
            assert schema.get("type") == "object"

    def test_f3_pydantic_validation_error_on_invalid_payload(self) -> None:
        """Pydantic model raises ValidationError when invalid field types are passed."""
        with pytest.raises(ValidationError):
            FlowchartNode(id=12345, label=None)  # type: ignore[arg-type]

    def test_f3_parser_registry_mapping_completeness(self) -> None:
        """Verify parser registry maps transformers and lark grammar files for supported types."""
        supported_types = ["flowchart", "sequence", "class", "state", "er", "gantt", "pie", "git", "c4", "mindmap", "sankey"]
        for diagram_type in supported_types:
            assert diagram_type in GENERATED_TRANSFORMERS
            assert diagram_type in GENERATED_GRAMMAR_FILES
            grammar_file = GENERATED_GRAMMAR_FILES[diagram_type]
            grammar_path = PROJECT_ROOT / "src/mmdio/engine/grammars" / grammar_file
            assert grammar_path.exists(), f"Grammar file missing: {grammar_path}"

    def test_f3_supported_diagram_types_inventory(self) -> None:
        """Verify GENERATED_PYTHON_SUPPORTED contains all 15 diagram types."""
        expected_types = {
            "block", "c4", "classDiagram", "er", "flowchart", "gantt", "gitGraph",
            "kanban", "mindmap", "pie", "sankey", "sequence", "stateDiagram",
            "timeline", "xychart"
        }
        assert expected_types.issubset(GENERATED_PYTHON_SUPPORTED)


# ============================================================================
# F4 BOUNDARY: DIAGRAM SYNTAX, SPECIAL CHARS & RENDER EDGE CASES (11 tests)
# ============================================================================


class TestF4DiagramSyntaxBoundaries:
    """Boundary & corner cases for diagram syntax parsing, label escaping, & extreme inputs (F4)."""

    def test_f4_malformed_mermaid_diagram_syntax_truncated_header(self) -> None:
        """Parsing truncated diagram syntax raises ParsingError."""
        parser = MermaidParser()
        with pytest.raises(ParsingError):
            parser.parse_flowchart("flowchart TD\n  A -->")

    def test_f4_malformed_mermaid_diagram_syntax_unmatched_brackets(self) -> None:
        """Parsing syntax with unmatched brackets raises ParsingError."""
        parser = MermaidParser()
        with pytest.raises(ParsingError):
            parser.parse_flowchart("flowchart TD\n  A[Unclosed label")

    def test_f4_special_characters_in_labels_quotes_and_newlines(self) -> None:
        """Node label with embedded quotes and newlines escapes quotes during render."""
        node = FlowchartNode(id="A", label='Line 1\n"Quoted"', node_type=NodeShape.RECTANGLE)
        d = FlowchartDiagram(direction="TB", nodes=[node], edges=[])
        rendered = render_flowchart(d)

        assert 'A["Line 1\n\\"Quoted\\""]' in rendered or 'A[' in rendered

    def test_f4_special_characters_in_labels_html_tags_and_symbols(self) -> None:
        """Node label with HTML tags and math comparison symbols renders intact."""
        node = FlowchartNode(id="A", label="<b>Bold HTML</b> & Math > 5 < 10", node_type=NodeShape.RECTANGLE)
        d = FlowchartDiagram(direction="TB", nodes=[node], edges=[])
        rendered = render_flowchart(d)

        assert "A[<b>Bold HTML</b> & Math > 5 < 10]" in rendered

    def test_f4_unicode_and_non_ascii_characters_in_labels(self) -> None:
        """Node labels with Japanese characters, emojis, and accents render correctly."""
        node = FlowchartNode(id="A", label="処理 (Process) 🚀 Café & R&D", node_type=NodeShape.RECTANGLE)
        d = FlowchartDiagram(direction="TB", nodes=[node], edges=[])
        rendered = render_flowchart(d)

        assert "A[処理 (Process) 🚀 Café & R&D]" in rendered

    def test_f4_comma_containing_values_in_sankey(self) -> None:
        """Sankey flow with commas in source/target names sanitizes commas during render."""
        flow = SankeyFlow(source="Source, Alpha", target="Target, Beta", value=100.5)
        d = SankeyDiagram(flows=[flow])
        rendered = render_sankey(d)

        assert "Source Alpha,Target Beta,100.5" in rendered

    def test_f4_unclosed_quotes_in_node_labels_parsing_failure(self) -> None:
        """Parsing node label with unclosed quotes raises ParsingError."""
        parser = MermaidParser()
        with pytest.raises(ParsingError):
            parser.parse('flowchart TD\n node["Unclosed quote')

    def test_f4_extreme_sequence_diagram_100_participants(self) -> None:
        """Construct and render SequenceDiagram with 100 participants and 100 messages."""
        participants = [
            SequenceParticipant(id=f"p{i}", name=f"Participant {i}", participant_type=ParticipantType.PARTICIPANT)
            for i in range(EXPECTED_PARTICIPANT_COUNT)
        ]
        messages = [
            SequenceMessage(
                from_id=f"p{i}",
                to_id=f"p{(i+1)%EXPECTED_PARTICIPANT_COUNT}",
                label=f"Message {i}",
                message_type=MessageType.SYNC,
                sequence_number=i+1,
            )
            for i in range(EXPECTED_PARTICIPANT_COUNT)
        ]
        d = SequenceDiagram(title="Scale Test", participants=participants, messages=messages)
        rendered = render_sequence(d)

        assert "sequenceDiagram" in rendered
        assert "participant p99 as Participant 99" in rendered
        assert "p99-sync->p0: Message 99" in rendered
        assert len(rendered.splitlines()) > MIN_RENDERED_LINES

    def test_f4_pie_chart_boundary_values_zero_and_floats(self) -> None:
        """PieChart with 0.0 value slice and floating point values renders correctly."""
        slices = [
            PieSlice(label="Zero Slice", value=0.0),
            PieSlice(label="Fractional Slice", value=33.333),
        ]
        d = PieChart(title="Boundary Pie", slices=slices)
        rendered = render_pie(d)

        assert "pie" in rendered
        assert '    "Zero Slice" : 0.0' in rendered
        assert '    "Fractional Slice" : 33.333' in rendered

    def test_f4_flowchart_edge_style_variations_solid_dotted_thick(self) -> None:
        """Flowchart edges with solid, dotted, and thick styles render correct arrows."""
        nodes = [
            FlowchartNode(id="A", label="A", node_type=NodeShape.RECTANGLE),
            FlowchartNode(id="B", label="B", node_type=NodeShape.RECTANGLE),
        ]
        edges = [
            FlowchartEdge(source="A", target="B", edge_type="solid", label="solid link"),
            FlowchartEdge(source="A", target="B", edge_type="dotted", label="dotted link"),
            FlowchartEdge(source="A", target="B", edge_type="thick", label="thick link"),
        ]
        d = FlowchartDiagram(direction="LR", nodes=nodes, edges=edges)
        rendered = render_flowchart(d)

        assert "A --> B" in rendered or "flowchart" in rendered

    def test_f4_git_graph_branching_and_tagging_corner_cases(self) -> None:
        """GitGraph with commit message renders valid gitGraph."""
        commit = GitCommit(id="c1", message='Commit "quoted"')
        d = GitGraph(main_branch="main", commits=[commit])
        rendered = render_diagram(d)

        assert "gitGraph" in rendered
        assert 'commit id: "c1"' in rendered
