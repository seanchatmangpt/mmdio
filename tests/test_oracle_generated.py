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

    example_kanban,

    example_pie,

    example_sankey,

    example_timeline,

)
from mmdio.engine.render import (

    render_block,

    render_kanban,

    render_pie,

    render_sankey,

    render_timeline,

)



class TestOracleBlockDiagram:
    """Test BlockDiagram rendering against real mermaid-js (generated fixture)."""

    def test_block_generated(self) -> None:
        """Render the ontology-derived example BlockDiagram and validate against mermaid-js."""
        diagram = example_block()
        source = render_block(diagram)
        validate_mermaid_source(source)


class TestOracleKanbanDiagram:
    """Test KanbanDiagram rendering against real mermaid-js (generated fixture)."""

    def test_kanban_generated(self) -> None:
        """Render the ontology-derived example KanbanDiagram and validate against mermaid-js."""
        diagram = example_kanban()
        source = render_kanban(diagram)
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


class TestOracleTimelineDiagram:
    """Test TimelineDiagram rendering against real mermaid-js (generated fixture)."""

    def test_timeline_generated(self) -> None:
        """Render the ontology-derived example TimelineDiagram and validate against mermaid-js."""
        diagram = example_timeline()
        source = render_timeline(diagram)
        validate_mermaid_source(source)


