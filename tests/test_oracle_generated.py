"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_oracle_tests.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonModel, isTopLevel only)

One TestOracle{ClassName} per top-level diagram model: build the
ontology-derived example fixture, render it, validate against real
mermaid-js. A new type needs zero hand-written test code — only the
ontology.ttl facts that also drive its model/render/fixture generation.
"""

import sys
from pathlib import Path

test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_oracle_roundtrip import validate_mermaid_source

from mmdio.engine.fixtures import (

    example_block,

    example_c4,

    example_class,

    example_er,

    example_flowchart,

    example_gantt,

    example_git,

    example_kanban,

    example_mindmap,

    example_pie,

    example_sankey,

    example_sequence,

    example_state,

    example_timeline,

    example_xychart,

)
from mmdio.engine.render import (

    render_block,

    render_c4,

    render_class,

    render_er,

    render_flowchart,

    render_gantt,

    render_git,

    render_kanban,

    render_mindmap,

    render_pie,

    render_sankey,

    render_sequence,

    render_state,

    render_timeline,

    render_xychart,

)



class TestOracleBlockDiagram:
    """Test BlockDiagram rendering against real mermaid-js (generated fixture)."""

    def test_block_generated(self) -> None:
        """Render the ontology-derived example BlockDiagram and validate against mermaid-js."""
        diagram = example_block()
        source = render_block(diagram)
        validate_mermaid_source(source)


class TestOracleC4Diagram:
    """Test C4Diagram rendering against real mermaid-js (generated fixture)."""

    def test_c4_generated(self) -> None:
        """Render the ontology-derived example C4Diagram and validate against mermaid-js."""
        diagram = example_c4()
        source = render_c4(diagram)
        validate_mermaid_source(source)


class TestOracleClassDiagram:
    """Test ClassDiagram rendering against real mermaid-js (generated fixture)."""

    def test_class_generated(self) -> None:
        """Render the ontology-derived example ClassDiagram and validate against mermaid-js."""
        diagram = example_class()
        source = render_class(diagram)
        validate_mermaid_source(source)


class TestOracleERDiagram:
    """Test ERDiagram rendering against real mermaid-js (generated fixture)."""

    def test_er_generated(self) -> None:
        """Render the ontology-derived example ERDiagram and validate against mermaid-js."""
        diagram = example_er()
        source = render_er(diagram)
        validate_mermaid_source(source)


class TestOracleFlowchartDiagram:
    """Test FlowchartDiagram rendering against real mermaid-js (generated fixture)."""

    def test_flowchart_generated(self) -> None:
        """Render the ontology-derived example FlowchartDiagram and validate against mermaid-js."""
        diagram = example_flowchart()
        source = render_flowchart(diagram)
        validate_mermaid_source(source)


class TestOracleGanttChart:
    """Test GanttChart rendering against real mermaid-js (generated fixture)."""

    def test_gantt_generated(self) -> None:
        """Render the ontology-derived example GanttChart and validate against mermaid-js."""
        diagram = example_gantt()
        source = render_gantt(diagram)
        validate_mermaid_source(source)


class TestOracleGitGraph:
    """Test GitGraph rendering against real mermaid-js (generated fixture)."""

    def test_git_generated(self) -> None:
        """Render the ontology-derived example GitGraph and validate against mermaid-js."""
        diagram = example_git()
        source = render_git(diagram)
        validate_mermaid_source(source)


class TestOracleKanbanDiagram:
    """Test KanbanDiagram rendering against real mermaid-js (generated fixture)."""

    def test_kanban_generated(self) -> None:
        """Render the ontology-derived example KanbanDiagram and validate against mermaid-js."""
        diagram = example_kanban()
        source = render_kanban(diagram)
        validate_mermaid_source(source)


class TestOracleMindmap:
    """Test Mindmap rendering against real mermaid-js (generated fixture)."""

    def test_mindmap_generated(self) -> None:
        """Render the ontology-derived example Mindmap and validate against mermaid-js."""
        diagram = example_mindmap()
        source = render_mindmap(diagram)
        validate_mermaid_source(source)


class TestOraclePieChart:
    """Test PieChart rendering against real mermaid-js (generated fixture)."""

    def test_pie_generated(self) -> None:
        """Render the ontology-derived example PieChart and validate against mermaid-js."""
        diagram = example_pie()
        source = render_pie(diagram)
        validate_mermaid_source(source)


class TestOracleSankeyDiagram:
    """Test SankeyDiagram rendering against real mermaid-js (generated fixture)."""

    def test_sankey_generated(self) -> None:
        """Render the ontology-derived example SankeyDiagram and validate against mermaid-js."""
        diagram = example_sankey()
        source = render_sankey(diagram)
        validate_mermaid_source(source)


class TestOracleSequenceDiagram:
    """Test SequenceDiagram rendering against real mermaid-js (generated fixture)."""

    def test_sequence_generated(self) -> None:
        """Render the ontology-derived example SequenceDiagram and validate against mermaid-js."""
        diagram = example_sequence()
        source = render_sequence(diagram)
        validate_mermaid_source(source)


class TestOracleStateDiagram:
    """Test StateDiagram rendering against real mermaid-js (generated fixture)."""

    def test_state_generated(self) -> None:
        """Render the ontology-derived example StateDiagram and validate against mermaid-js."""
        diagram = example_state()
        source = render_state(diagram)
        validate_mermaid_source(source)


class TestOracleTimelineDiagram:
    """Test TimelineDiagram rendering against real mermaid-js (generated fixture)."""

    def test_timeline_generated(self) -> None:
        """Render the ontology-derived example TimelineDiagram and validate against mermaid-js."""
        diagram = example_timeline()
        source = render_timeline(diagram)
        validate_mermaid_source(source)


class TestOracleXYChartDiagram:
    """Test XYChartDiagram rendering against real mermaid-js (generated fixture)."""

    def test_xychart_generated(self) -> None:
        """Render the ontology-derived example XYChartDiagram and validate against mermaid-js."""
        diagram = example_xychart()
        source = render_xychart(diagram)
        validate_mermaid_source(source)


