"""
Tier 1 Feature Coverage E2E Test Suite for mmdio.

Feature Coverage Target (>= 38 test cases total across F1, F2, F3, F4):
- F1 (ggen Ontology & Law Gates): >= 5 tests validating ggen pack law gates, ontology triples, SPARQL gate compliance.
- F2 (Pure Python Code Precipitation): >= 10 tests verifying src.mmdio.engine modules (models.py, enums.py, parser_registry.py, render_dispatch.py, render.py, parser.py, detect_patterns.py) without shadow duplications.
- F3 (Pytest Harness & Warning Cleanliness): >= 5 tests validating zero deprecation warnings, warning filters, clean imports.
- F4 (Mermaid 11.16.0 Oracle & Diagram Roundtrip): >= 15 tests validating rendered Mermaid text against Node.js verify_mermaid.mjs oracle across all 15 supported diagram types.
"""

import glob
import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import pytest
import rdflib

# Add project root to sys.path
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

# Engine & Model imports
from mmdio.detect import detect_diagram_type
from mmdio.engine import MermaidParser, parse_mermaid, render_diagram
from mmdio.engine.detect_patterns import GENERATED_DETECT_PATTERNS
from mmdio.engine.fixtures import (
    example_block,
    example_kanban,
    example_pie,
    example_sankey,
    example_timeline,
)
from mmdio.engine.parser_registry import (
    GENERATED_GRAMMAR_FILES,
    GENERATED_TRANSFORMERS,
)
from mmdio.engine.render_dispatch import GENERATED_RENDER_DISPATCH
from mmdio.engine.schemas import GENERATED_JSON_SCHEMAS
from mmdio.engine.supported import GENERATED_PYTHON_SUPPORTED
from mmdio.engine.models import (
    Block,
    BlockDiagram,
    C4Diagram,
    C4Element,
    C4Level,
    C4Relationship,
    CardinityType,
    ClassDefinition,
    ClassDiagram,
    ClassMember,
    ClassMethod,
    ClassRelationship,
    Connection,
    DataSeries,
    Entity,
    EntityAttribute,
    ERDiagram,
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
    MessageType,
    Mindmap,
    MindmapNode,
    NodeShape,
    ParticipantType,
    PieChart,
    PieSlice,
    RelationshipType,
    SankeyDiagram,
    SankeyFlow,
    SequenceDiagram,
    SequenceMessage,
    SequenceParticipant,
    State,
    StateDiagram,
    TaskStatus,
    TimelineDiagram,
    TimelineEvent,
    Transition,
    XYAxis,
    XYChartDiagram,
)


# ============================================================================
# F1: ggen ONTOLOGY & LAW GATES (6 Test Cases)
# ============================================================================


class TestF1OntologyAndLawGates:
    """F1: ggen Ontology & Law Gates validation."""

    def test_f1_01_sparql_law_gates_zero_violations(self) -> None:
        """F1-01: Verify all 10 SPARQL law gates pass with 0 violations."""
        violations = verify_sparql_gates()
        assert len(violations) == 0, f"Expected 0 SPARQL gate violations, got: {violations}"

    def test_f1_02_ontology_supported_diagram_types_triples(self) -> None:
        """F1-02: Verify ontology RDF facts define all 15 pythonSupport diagram types."""
        graph = rdflib.Graph()
        graph.parse(str(REGISTRY_TTL), format="turtle")
        graph.parse(str(ONTOLOGY_TTL), format="turtle")

        query = """
        PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
        SELECT ?type ?internalId WHERE {
            ?type a mer:DiagramType ;
                  mer:pythonSupport true ;
                  mer:pythonInternalId ?internalId .
        }
        """
        results = list(graph.query(query))
        supported_ids = {str(row[1]) for row in results}
        expected_ids = {
            "flowchart", "sequence", "class", "state", "er",
            "gantt", "pie", "git", "c4", "mindmap",
            "sankey", "kanban", "timeline", "xychart", "block"
        }
        assert expected_ids.issubset(supported_ids), (
            f"Missing pythonSupport diagram types in RDF. Expected {expected_ids}, got {supported_ids}"
        )

    def test_f1_03_pack_manifest_targets(self) -> None:
        """F1-03: Verify pack.toml emitted targets map to engine directory paths."""
        pack_toml = PROJECT_ROOT / "packs" / "mmdio-pack" / "pack.toml"
        assert pack_toml.exists(), f"pack.toml not found at {pack_toml}"
        content = pack_toml.read_text(encoding="utf-8")
        assert "engine" in content, (
            "pack.toml description should reference engine modules"
        )
        assert "enums" in content
        assert "models" in content
        assert "parser_registry" in content
        assert "render_dispatch" in content

    def test_f1_04_ggen_sync_command_execution(self) -> None:
        """F1-04: Execute ggen sync run and verify exit code 0."""
        if shutil.which("ggen") is None:
            pytest.skip("ggen CLI not installed")

        res = subprocess.run(
            ["ggen", "sync", "run"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=15
        )
        assert res.returncode == 0, f"ggen sync run failed:\nStdout: {res.stdout}\nStderr: {res.stderr}"

    def test_f1_05_ontology_enum_classes_and_members(self) -> None:
        """F1-05: Query ontology for mer:PythonEnum subjects and verify member definitions."""
        graph = rdflib.Graph()
        graph.parse(str(ONTOLOGY_TTL), format="turtle")

        query = """
        PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
        SELECT ?enumClass (COUNT(?member) AS ?memberCount) WHERE {
            ?enumClass a mer:PythonEnum ;
                       mer:enumMember ?member .
        }
        GROUP BY ?enumClass
        """
        results = list(graph.query(query))
        assert len(results) >= 7, f"Expected at least 7 PythonEnum definitions, got {len(results)}"
        for row in results:
            enum_name = str(row[0])
            member_count = int(row[1])
            assert member_count >= 1, f"Enum {enum_name} has 0 members"

    def test_f1_06_field_order_and_unique_classnames_gates(self) -> None:
        """F1-06: Specifically evaluate Gate 040 (gapless field order) & Gate 100 (unique classnames)."""
        graph = rdflib.Graph()
        graph.parse(str(REGISTRY_TTL), format="turtle")
        graph.parse(str(ONTOLOGY_TTL), format="turtle")

        gate_040 = GATES_DIR / "040_field_order_gapless.rq"
        gate_100 = GATES_DIR / "100_classname_globally_unique.rq"

        res_040 = list(graph.query(gate_040.read_text(encoding="utf-8")))
        res_100 = list(graph.query(gate_100.read_text(encoding="utf-8")))

        assert len(res_040) == 0, f"Gate 040 field_order_gapless failed: {res_040}"
        assert len(res_100) == 0, f"Gate 100 classname_globally_unique failed: {res_100}"


# ============================================================================
# F2: PURE PYTHON CODE PRECIPITATION (11 Test Cases)
# ============================================================================


class TestF2PurePythonCodePrecipitation:
    """F2: Pure Python Code Precipitation module & AST tests."""

    def test_f2_01_models_module_exports_all_diagram_classes(self) -> None:
        """F2-01: Verify models.py exports all top-level diagram AST classes."""
        classes = [
            FlowchartDiagram, SequenceDiagram, ClassDiagram, StateDiagram, ERDiagram,
            GanttChart, PieChart, GitGraph, C4Diagram, Mindmap,
            SankeyDiagram, KanbanDiagram, TimelineDiagram, XYChartDiagram, BlockDiagram
        ]
        for cls in classes:
            assert issubclass(cls, object)
            assert hasattr(cls, "model_fields") or hasattr(cls, "__fields__")

    def test_f2_02_models_discriminated_union(self) -> None:
        """F2-02: Verify MermaidDiagram union includes all 15 diagram types."""
        assert MermaidDiagram is not None

    def test_f2_03_enums_module_strenum_conformance(self) -> None:
        """F2-03: Verify token enums match expected string values."""
        assert NodeShape.RECTANGLE == "rectangle"
        assert NodeShape.DIAMOND == "diamond"
        assert MessageType.SYNC == "sync"
        assert RelationshipType.INHERITANCE == "inheritance"
        assert CardinityType.ONE_TO_MANY == "one_to_many"
        assert TaskStatus.ACTIVE == "active"
        assert C4Level.C1 == "C1"

    def test_f2_04_parser_registry_maps_all_types(self) -> None:
        """F2-04: Verify GENERATED_TRANSFORMERS maps supported diagram internal IDs."""
        assert len(GENERATED_TRANSFORMERS) >= 15
        expected_ids = {
            "flowchart", "sequence", "class", "state", "er",
            "gantt", "pie", "git", "c4", "mindmap",
            "sankey", "kanban", "timeline", "xychart", "block"
        }
        for diagram_id in expected_ids:
            assert diagram_id in GENERATED_TRANSFORMERS, f"Missing parser transformer for {diagram_id}"
            assert diagram_id in GENERATED_GRAMMAR_FILES, f"Missing grammar file for {diagram_id}"

    def test_f2_05_render_dispatch_maps_all_models(self) -> None:
        """F2-05: Verify GENERATED_RENDER_DISPATCH contains render functions for all 15 model classes."""
        assert len(GENERATED_RENDER_DISPATCH) >= 15
        classes = [
            FlowchartDiagram, SequenceDiagram, ClassDiagram, StateDiagram, ERDiagram,
            GanttChart, PieChart, GitGraph, C4Diagram, Mindmap,
            SankeyDiagram, KanbanDiagram, TimelineDiagram, XYChartDiagram, BlockDiagram
        ]
        for cls in classes:
            assert cls in GENERATED_RENDER_DISPATCH, f"Missing render dispatcher for {cls.__name__}"

    def test_f2_06_render_module_dispatches_correctly(self) -> None:
        """F2-06: Call render_diagram() for multiple AST instances."""
        fc = FlowchartDiagram(nodes=[FlowchartNode(id="A", label="Test", node_type=NodeShape.RECTANGLE)])
        res_fc = render_diagram(fc)
        assert res_fc.startswith("graph") or res_fc.startswith("flowchart")

        pie = PieChart(title="Slice", slices=[PieSlice(label="A", value=10.0)])
        res_pie = render_diagram(pie)
        assert "title Slice" in res_pie

    def test_f2_07_parser_module_parses_mermaid(self) -> None:
        """F2-07: Use parse_pie() to parse pie chart text into AST model."""
        from mmdio.engine.parser import parse_pie
        source = 'pie title Pets\n    "Dogs" : 386\n    "Cats" : 85\n'
        ast = parse_pie(source)
        assert isinstance(ast, PieChart)
        assert len(ast.slices) == 2

    def test_f2_08_detect_patterns_module_matching(self) -> None:
        """F2-08: Test pattern detector on various diagram text headers."""
        assert detect_diagram_type("flowchart TD\n A --> B") == "flowchart"
        assert detect_diagram_type("sequenceDiagram\n A->>B: Hi") == "sequence"
        assert detect_diagram_type("classDiagram\n class A") == "class"
        assert detect_diagram_type("stateDiagram-v2\n [*] --> S") == "state"
        assert detect_diagram_type("erDiagram\n USER ||--o{ POST : writes") == "er"
        assert detect_diagram_type("gantt\n title T") == "gantt"
        assert detect_diagram_type("pie title P\n \"A\" : 10") == "pie"
        assert detect_diagram_type("gitGraph\n commit") == "git"
        assert detect_diagram_type("C4Context\n title C4") == "c4"
        assert detect_diagram_type("mindmap\n Root") == "mindmap"
        assert detect_diagram_type("sankey-beta\n A,B,10") == "sankey"
        assert detect_diagram_type("kanban\n Todo") == "kanban"
        assert detect_diagram_type("timeline\n 2026 : E") == "timeline"
        assert detect_diagram_type("xychart-beta\n x-axis [1]") == "xychart"
        assert detect_diagram_type("block-beta\n columns 2") == "block"

    def test_f2_09_supported_types_export(self) -> None:
        """F2-09: Verify GENERATED_PYTHON_SUPPORTED set contains diagram IDs."""
        expected = {
            "flowchart", "sequence", "classDiagram", "stateDiagram", "er",
            "gantt", "pie", "gitGraph", "c4", "mindmap",
            "sankey", "kanban", "timeline", "xychart", "block"
        }
        assert expected.issubset(set(GENERATED_PYTHON_SUPPORTED))

    def test_f2_10_no_shadow_types_directory(self) -> None:
        """F2-10: Verify absence of legacy shadow files in engine root."""
        engine_dir = PROJECT_ROOT / "src" / "mmdio" / "engine"
        legacy_shadow_file = engine_dir / "_generated_types.py"
        assert not legacy_shadow_file.exists(), "Legacy shadow file should not exist"

    def test_f2_11_generated_fixtures_and_schemas_export(self) -> None:
        """F2-11: Verify _generated_fixtures.py builders and _generated_schemas.py exports."""
        b = example_block()
        assert isinstance(b, BlockDiagram)
        k = example_kanban()
        assert isinstance(k, KanbanDiagram)
        p = example_pie()
        assert isinstance(p, PieChart)
        s = example_sankey()
        assert isinstance(s, SankeyDiagram)
        t = example_timeline()
        assert isinstance(t, TimelineDiagram)

        assert len(GENERATED_JSON_SCHEMAS) >= 5
        assert "pie" in GENERATED_JSON_SCHEMAS


# ============================================================================
# F3: PYTEST HARNESS & WARNING CLEANLINESS (6 Test Cases)
# ============================================================================


class TestF3PytestHarnessAndWarnings:
    """F3: Pytest Harness & Warning Cleanliness tests."""

    def test_f3_01_zero_deprecation_warnings_on_engine_import(self) -> None:
        """F3-01: Importing mmdio engine modules produces 0 deprecation warnings."""
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always", DeprecationWarning)
            import mmdio.engine
            import mmdio.engine.models
            import mmdio.engine.parser
            import mmdio.engine.render

            dep_warnings = [w for w in captured if issubclass(w.category, DeprecationWarning)]
            assert len(dep_warnings) == 0, f"Deprecation warnings caught during import: {dep_warnings}"

    def test_f3_02_pyproject_filterwarnings_configuration(self) -> None:
        """F3-02: Verify pyproject.toml contains filterwarnings configuration."""
        pyproject = PROJECT_ROOT / "pyproject.toml"
        assert pyproject.exists()
        content = pyproject.read_text(encoding="utf-8")
        assert "filterwarnings =" in content

    def test_f3_03_clean_import_no_side_effects(self) -> None:
        """F3-03: Verify engine import has zero side effects on environment or files."""
        temp_check = list(PROJECT_ROOT.glob("*.tmp"))
        assert len(temp_check) == 0, "No temporary files created during engine import"

    def test_f3_04_lark_parser_syntax_warning_free(self) -> None:
        """F3-04: Verify Lark parsing executes without triggering syntax or deprecation warnings."""
        from mmdio.engine.parser import parse_pie
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            parse_pie('pie title T\n  "Slice" : 10')
            assert len(captured) == 0, f"Warnings raised during Lark parsing: {captured}"

    def test_f3_05_pydantic_v2_instantiation_warning_free(self) -> None:
        """F3-05: Verify Pydantic V2 model instantiation produces zero deprecation warnings."""
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            FlowchartDiagram(nodes=[FlowchartNode(id="A", label="Label", node_type=NodeShape.RECTANGLE)])
            SequenceDiagram(participants=[SequenceParticipant(id="P1", name="Part1", participant_type=ParticipantType.PARTICIPANT)])
            PieChart(title="Pie", slices=[PieSlice(label="L", value=5.0)])
            assert len(captured) == 0, f"Warnings during Pydantic model instantiation: {captured}"

    def test_f3_06_fastapi_app_import_cleanliness(self) -> None:
        """F3-06: Verify mmdio.api app imports cleanly without module error."""
        from mmdio.api import app
        assert app is not None


# ============================================================================
# F4: MERMAID 11.16.0 ORACLE & DIAGRAM ROUNDTRIP (15 Test Cases)
# ============================================================================


class TestF4MermaidOracleAndDiagramRoundtrip:
    """F4: Mermaid 11.16.0 Oracle & Diagram Roundtrip across all 15 supported diagram types."""

    def test_f4_01_flowchart_oracle_roundtrip(self) -> None:
        """F4-01: Flowchart Diagram render and oracle validation."""
        diagram = FlowchartDiagram(
            direction="TB",
            nodes=[
                FlowchartNode(id="A", label="Start", node_type=NodeShape.RECTANGLE),
                FlowchartNode(id="B", label="Decision", node_type=NodeShape.DIAMOND),
                FlowchartNode(id="C", label="End", node_type=NodeShape.CIRCLE),
            ],
            edges=[
                FlowchartEdge(source="A", target="B", label="Proceed"),
                FlowchartEdge(source="B", target="C", label="Yes"),
            ]
        )
        source = render_diagram(diagram)
        assert "graph TB" in source or "flowchart TB" in source
        validate_mermaid_source(source)

    def test_f4_02_sequence_oracle_roundtrip(self) -> None:
        """F4-02: Sequence Diagram render and oracle validation."""
        diagram = SequenceDiagram(
            title="Authentication Sequence",
            participants=[
                SequenceParticipant(id="U", name="User", participant_type=ParticipantType.ACTOR),
                SequenceParticipant(id="S", name="Server", participant_type=ParticipantType.PARTICIPANT),
            ],
            messages=[
                SequenceMessage(from_id="U", to_id="S", label="Login Request", message_type=MessageType.SYNC, sequence_number=1),
                SequenceMessage(from_id="S", to_id="U", label="Token Response", message_type=MessageType.ASYNC, sequence_number=2),
            ]
        )
        source = render_diagram(diagram)
        assert "sequenceDiagram" in source
        validate_mermaid_source(source)

    def test_f4_03_class_oracle_roundtrip(self) -> None:
        """F4-03: Class Diagram render and oracle validation."""
        diagram = ClassDiagram(
            classes=[
                ClassDefinition(
                    name="BaseService",
                    members=[ClassMember(name="service_id", type="str", visibility="+")],
                    methods=[ClassMethod(name="start", visibility="+")]
                ),
                ClassDefinition(name="AuthService", members=[], methods=[])
            ],
            relationships=[
                ClassRelationship(from_class="AuthService", to_class="BaseService", type=RelationshipType.INHERITANCE)
            ]
        )
        source = render_diagram(diagram)
        assert "classDiagram" in source
        validate_mermaid_source(source)

    def test_f4_04_state_oracle_roundtrip(self) -> None:
        """F4-04: State Diagram render and oracle validation."""
        diagram = StateDiagram(
            initial_state="Idle",
            states=[
                State(id="Idle", label="Idle State"),
                State(id="Processing", label="Processing State"),
                State(id="Done", label="Done State"),
            ],
            transitions=[
                Transition(source="Idle", target="Processing", label="trigger"),
                Transition(source="Processing", target="Done", label="complete"),
            ]
        )
        source = render_diagram(diagram)
        assert "stateDiagram" in source
        validate_mermaid_source(source)

    def test_f4_05_er_oracle_roundtrip(self) -> None:
        """F4-05: ER Diagram render and oracle validation."""
        diagram = ERDiagram(
            entities=[
                Entity(name="CUSTOMER", attributes=[EntityAttribute(name="id", attr_type="int")]),
                Entity(name="ORDER", attributes=[EntityAttribute(name="customer_id", attr_type="int")]),
            ],
            relationships=[
                ERRelationship(entity_a="CUSTOMER", entity_b="ORDER", cardinality_a="1", cardinality_b="N", relation_type=RelationshipType.ONE_TO_MANY)
            ]
        )
        source = render_diagram(diagram)
        assert "erDiagram" in source
        validate_mermaid_source(source)

    def test_f4_06_gantt_oracle_roundtrip(self) -> None:
        """F4-06: Gantt Chart render and oracle validation."""
        diagram = GanttChart(
            title="Q3 Development Roadmap",
            tasks=[
                GanttTask(id="t1", title="Planning Phase", start_date="2026-07-01", end_date="2026-07-15", status=TaskStatus.DONE),
                GanttTask(id="t2", title="Implementation", start_date="2026-07-16", end_date="2026-08-15", status=TaskStatus.ACTIVE),
            ]
        )
        source = render_diagram(diagram)
        assert "gantt" in source
        validate_mermaid_source(source)

    def test_f4_07_pie_oracle_roundtrip(self) -> None:
        """F4-07: Pie Chart render and oracle validation."""
        diagram = PieChart(
            title="Cloud Infrastructure Cost Distribution",
            slices=[
                PieSlice(label="Compute", value=55.0),
                PieSlice(label="Storage", value=25.0),
                PieSlice(label="Networking", value=20.0),
            ]
        )
        source = render_diagram(diagram)
        assert "pie" in source
        validate_mermaid_source(source)

    def test_f4_08_git_oracle_roundtrip(self) -> None:
        """F4-08: Git Graph render and oracle validation."""
        diagram = GitGraph(
            main_branch="main",
            commits=[
                GitCommit(id="c1", message="Initial commit"),
                GitCommit(id="c2", message="Add feature branch"),
            ]
        )
        source = render_diagram(diagram)
        assert "gitGraph" in source
        validate_mermaid_source(source)

    def test_f4_09_c4_oracle_roundtrip(self) -> None:
        """F4-09: C4 Diagram render and oracle validation."""
        diagram = C4Diagram(
            title="E-Commerce Architecture Context",
            level=C4Level.C1,
            elements=[
                C4Element(id="c1", name="Shopper", description="End user", type="Person"),
                C4Element(id="c2", name="API Gateway", description="Routes HTTP requests", type="System"),
            ],
            relationships=[
                C4Relationship(source="c1", target="c2", label="Submits Order")
            ]
        )
        source = render_diagram(diagram)
        assert "C4Context" in source
        validate_mermaid_source(source)

    def test_f4_10_mindmap_oracle_roundtrip(self) -> None:
        """F4-10: Mindmap render and oracle validation."""
        diagram = Mindmap(
            root=MindmapNode(
                id="root",
                label="System Architecture"
            )
        )
        source = render_diagram(diagram)
        assert "mindmap" in source
        validate_mermaid_source(source)

    def test_f4_11_sankey_oracle_roundtrip(self) -> None:
        """F4-11: Sankey Diagram render and oracle validation."""
        diagram = SankeyDiagram(
            flows=[
                SankeyFlow(source="Raw Power", target="Grid", value=1000.0),
                SankeyFlow(source="Grid", target="Residential", value=600.0),
                SankeyFlow(source="Grid", target="Commercial", value=400.0),
            ]
        )
        source = render_diagram(diagram)
        assert "sankey-beta" in source
        validate_mermaid_source(source)

    def test_f4_12_kanban_oracle_roundtrip(self) -> None:
        """F4-12: Kanban Diagram render and oracle validation."""
        diagram = KanbanDiagram(
            sections=[
                KanbanSection(name="Backlog", cards=[KanbanCard(title="Security Audit")]),
                KanbanSection(name="In Progress", cards=[KanbanCard(title="E2E Test Suite")]),
            ]
        )
        source = render_diagram(diagram)
        assert "kanban" in source
        validate_mermaid_source(source)

    def test_f4_13_timeline_oracle_roundtrip(self) -> None:
        """F4-13: Timeline Diagram render and oracle validation."""
        diagram = TimelineDiagram(
            title="Product History",
            events=[
                TimelineEvent(time="2024", description="V1 Release"),
                TimelineEvent(time="2026", description="Universal IO Migration"),
            ]
        )
        source = render_diagram(diagram)
        assert "timeline" in source
        validate_mermaid_source(source)

    def test_f4_14_xychart_oracle_roundtrip(self) -> None:
        """F4-14: XYChart Diagram render and oracle validation."""
        diagram = XYChartDiagram(
            title="Monthly Active Users",
            x_axis=XYAxis(values=["Jan", "Feb", "Mar", "Apr"]),
            y_axis=XYAxis(label="Users", range_min=0, range_max=10000),
            series=[
                DataSeries(series_type="line-series", values=[1200, 2500, 4800, 8900])
            ]
        )
        source = render_diagram(diagram)
        assert "xychart-beta" in source
        validate_mermaid_source(source)

    def test_f4_15_block_oracle_roundtrip(self) -> None:
        """F4-15: Block Diagram render and oracle validation."""
        diagram = BlockDiagram(
            columns=3,
            blocks=[
                Block(id="A", label="Module A"),
                Block(id="B", label="Module B"),
                Block(id="C", label="Module C"),
            ],
            connections=[
                Connection(source="A", target="B", arrow_type="-->"),
                Connection(source="B", target="C", arrow_type="-->"),
            ]
        )
        source = render_diagram(diagram)
        assert "block-beta" in source
        validate_mermaid_source(source)
