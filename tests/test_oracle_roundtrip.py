"""
Test oracle for mmdio: validate rendered output against real mermaid-js parser.

This module tests all 11 supported diagram types by:
1. Creating a sample AST for each type using mmdio's models
2. Rendering it via mmdio.engine.render_diagram()
3. Writing the output to a temp .mmd file
4. Validating with the upstream mermaid-js parser via Node.js

Tests are automatically skipped if Node.js or npm dependencies are not available.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from mmdio.engine import models, render


def get_oracle_node_path() -> str:
    """Get absolute path to verify_mermaid.mjs, relative to this module."""
    this_dir = Path(__file__).parent
    oracle_script = this_dir / "oracle" / "verify_mermaid.mjs"
    return str(oracle_script)


def check_node_available() -> bool:
    """Check if node is available and npm ci has been run in oracle dir."""
    # Check if node is available
    if shutil.which("node") is None:
        return False

    # Check if npm dependencies are installed
    oracle_dir = Path(get_oracle_node_path()).parent
    node_modules = oracle_dir / "node_modules"
    return node_modules.exists() and (node_modules / "mermaid").exists()


# Skip all tests if Node/npm not available
pytestmark = pytest.mark.skipif(
    not check_node_available(),
    reason="Node.js or npm dependencies not available (run: cd tests/oracle && npm ci)"
)


def validate_mermaid_source(mmd_source: str) -> None:
    """
    Validate a mermaid source string against the real mermaid-js parser.

    Args:
        mmd_source: Mermaid diagram source code as a string

    Raises:
        AssertionError: If the mermaid-js parser rejects the diagram
        subprocess.CalledProcessError: If the validation script fails
    """
    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.mmd',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(mmd_source)
        temp_path = f.name

    try:
        # Run the Node.js validator
        result = subprocess.run(
            ['node', get_oracle_node_path(), temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Assert successful parse
        assert result.returncode == 0, (
            f"Mermaid parser rejected diagram.\n"
            f"Exit code: {result.returncode}\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}\n"
            f"Source:\n{mmd_source}"
        )
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass


# ============================================================================
# DIAGRAM TYPE TESTS (11 parametrized tests)
# ============================================================================


class TestOracleFlowchart:
    """Test flowchart diagram rendering."""

    def test_flowchart_simple(self) -> None:
        """Test simple flowchart with nodes and edges."""
        diagram = models.FlowchartDiagram(
            direction="TB",
            nodes=[
                models.FlowchartNode(id="A", label="Start", shape=models.NodeShape.RECTANGLE),
                models.FlowchartNode(id="B", label="Process", shape=models.NodeShape.RECTANGLE),
                models.FlowchartNode(id="C", label="End", shape=models.NodeShape.RECTANGLE),
            ],
            edges=[
                models.FlowchartEdge(source="A", target="B", label="Go"),
                models.FlowchartEdge(source="B", target="C"),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleSequence:
    """Test sequence diagram rendering."""

    def test_sequence_simple(self) -> None:
        """Test simple sequence diagram with participants and messages."""
        diagram = models.SequenceDiagram(
            title="Chat Flow",
            participants=[
                models.SequenceParticipant(id="A", name="Alice", type=models.ParticipantType.ACTOR),
                models.SequenceParticipant(id="B", name="Bob", type=models.ParticipantType.PARTICIPANT),
            ],
            messages=[
                models.SequenceMessage(
                    from_participant="A",
                    to_participant="B",
                    label="Hello",
                    type=models.MessageType.SYNC
                ),
                models.SequenceMessage(
                    from_participant="B",
                    to_participant="A",
                    label="Hi there",
                    type=models.MessageType.SYNC
                ),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleClass:
    """Test class diagram rendering."""

    def test_class_simple(self) -> None:
        """Test simple class diagram with classes and relationships."""
        diagram = models.ClassDiagram(
            classes=[
                models.ClassDefinition(
                    name="Animal",
                    members=[
                        models.ClassMember(name="name", type="str", visibility="+"),
                        models.ClassMember(name="age", type="int", visibility="+"),
                    ],
                    methods=[
                        models.ClassMethod(name="speak", visibility="+"),
                    ]
                ),
                models.ClassDefinition(
                    name="Dog",
                    members=[],
                    methods=[],
                ),
            ],
            relationships=[
                models.ClassRelationship(
                    from_class="Dog",
                    to_class="Animal",
                    type=models.RelationshipType.INHERITANCE,
                    label=None
                ),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleState:
    """Test state diagram rendering."""

    def test_state_simple(self) -> None:
        """Test simple state diagram with states and transitions."""
        diagram = models.StateDiagram(
            states=[
                models.State(id="s1", label="Idle", is_initial=True),
                models.State(id="s2", label="Running"),
                models.State(id="s3", label="Done", is_final=True),
            ],
            transitions=[
                models.Transition(from_state="s1", to_state="s2", event="start"),
                models.Transition(from_state="s2", to_state="s3", event="finish"),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleER:
    """Test entity-relationship diagram rendering."""

    def test_er_simple(self) -> None:
        """Test simple ER diagram with entities and relationships."""
        diagram = models.ERDiagram(
            entities=[
                models.Entity(
                    name="Customer",
                    attributes=[
                        models.EntityAttribute(name="id", type="int", is_key=True, is_nullable=False),
                        models.EntityAttribute(name="name", type="varchar", is_nullable=False),
                    ]
                ),
                models.Entity(
                    name="Order",
                    attributes=[
                        models.EntityAttribute(name="id", type="int", is_key=True, is_nullable=False),
                        models.EntityAttribute(name="customer_id", type="int", is_nullable=False),
                    ]
                ),
            ],
            relationships=[
                models.ERRelationship(
                    from_entity="Customer",
                    to_entity="Order",
                    cardinality=models.CardinityType.ONE_TO_MANY,
                    label="places"
                ),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleGantt:
    """Test Gantt chart rendering."""

    def test_gantt_simple(self) -> None:
        """Test simple Gantt chart with tasks."""
        diagram = models.GanttChart(
            title="Project Timeline",
            tasks=[
                models.GanttTask(
                    id="t1",
                    title="Design",
                    start_date="2024-01-01",
                    end_date="2024-01-10",
                    status=models.TaskStatus.DONE
                ),
                models.GanttTask(
                    id="t2",
                    title="Development",
                    start_date="2024-01-11",
                    end_date="2024-01-20",
                    status=models.TaskStatus.ACTIVE
                ),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOraclePie:
    """Test pie chart rendering."""

    def test_pie_simple(self) -> None:
        """Test simple pie chart with slices."""
        diagram = models.PieChart(
            title="Market Share",
            slices=[
                models.PieSlice(label="Product A", value=45),
                models.PieSlice(label="Product B", value=30),
                models.PieSlice(label="Product C", value=25),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleGit:
    """Test git graph rendering."""

    def test_git_simple(self) -> None:
        """Test simple git graph with branches and commits."""
        diagram = models.GitGraph(
            commits=[
                models.GitCommit(id="c1", message="Initial commit"),
                models.GitCommit(id="c2", message="Add feature"),
                models.GitCommit(id="c3", message="Fix bug"),
            ],
            branches=[
                models.GitBranch(name="main", commit_ids=["c1", "c3"], is_main=True),
                models.GitBranch(name="develop", commit_ids=["c1", "c2"]),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleC4:
    """Test C4 diagram rendering."""

    def test_c4_simple(self) -> None:
        """Test simple C4 context diagram."""
        diagram = models.C4Diagram(
            title="System Architecture",
            elements=[
                models.C4Element(
                    id="s1",
                    name="User",
                    level=models.C4Level.C1,
                    description="External user"
                ),
                models.C4Element(
                    id="s2",
                    name="System",
                    level=models.C4Level.C1,
                    description="Our system",
                    technology="Cloud"
                ),
            ],
            relationships=[
                models.C4Relationship(
                    from_element="s1",
                    to_element="s2",
                    description="Uses",
                    technology="HTTP"
                ),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleMindmap:
    """Test mindmap rendering."""

    def test_mindmap_simple(self) -> None:
        """Test simple mindmap with hierarchy."""
        diagram = models.Mindmap(
            root=models.MindmapNode(
                id="root",
                label="Root",
                children=[
                    models.MindmapNode(
                        id="c1",
                        label="Child 1",
                        children=[
                            models.MindmapNode(id="gc1", label="Grandchild 1a"),
                            models.MindmapNode(id="gc2", label="Grandchild 1b"),
                        ]
                    ),
                    models.MindmapNode(id="c2", label="Child 2"),
                ]
            )
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)


class TestOracleSankey:
    """Test Sankey diagram rendering."""

    def test_sankey_simple(self) -> None:
        """Test simple Sankey diagram with flows."""
        diagram = models.SankeyDiagram(
            flows=[
                models.SankeyFlow(source="A", target="B", value=100),
                models.SankeyFlow(source="B", target="C", value=80),
                models.SankeyFlow(source="B", target="D", value=20),
            ]
        )
        source = render.render_diagram(diagram)
        validate_mermaid_source(source)
