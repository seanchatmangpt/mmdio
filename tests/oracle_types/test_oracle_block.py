"""Oracle tests for Block diagrams (type-scoped)."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mmdio.engine.types import block_models
from mmdio.engine.types import block_render

# Import validate_mermaid_source from the parent test module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_oracle_roundtrip import validate_mermaid_source


class TestOracleBlock:
    """Test block diagram rendering."""

    def test_block_simple(self) -> None:
        """Test simple block diagram with blocks and connections."""
        diagram = block_models.BlockDiagram(
            blocks=[
                block_models.Block(id="A", label="Module A"),
                block_models.Block(id="B", label="Module B"),
                block_models.Block(id="C", label="Module C"),
            ],
            connections=[
                block_models.Connection(source="A", target="B", arrow_type="-->"),
                block_models.Connection(source="B", target="C", arrow_type="-->"),
            ]
        )
        source = block_render.render_block(diagram)
        validate_mermaid_source(source)

    def test_block_with_columns(self) -> None:
        """Test block diagram with column configuration."""
        diagram = block_models.BlockDiagram(
            columns=3,
            blocks=[
                block_models.Block(id="A", label="Step 1"),
                block_models.Block(id="B", label="Step 2"),
                block_models.Block(id="C", label="Step 3"),
            ],
            connections=[
                block_models.Connection(source="A", target="B"),
                block_models.Connection(source="B", target="C"),
            ]
        )
        source = block_render.render_block(diagram)
        validate_mermaid_source(source)

    def test_block_with_labels(self) -> None:
        """Test block diagram with connection labels."""
        diagram = block_models.BlockDiagram(
            blocks=[
                block_models.Block(id="A", label="Start"),
                block_models.Block(id="B", label="Process"),
                block_models.Block(id="C", label="End"),
            ],
            connections=[
                block_models.Connection(source="A", target="B", label="begin"),
                block_models.Connection(source="B", target="C", label="finish"),
            ]
        )
        source = block_render.render_block(diagram)
        validate_mermaid_source(source)

    def test_block_different_arrows(self) -> None:
        """Test block diagram with different arrow types."""
        diagram = block_models.BlockDiagram(
            blocks=[
                block_models.Block(id="A", label="Source"),
                block_models.Block(id="B", label="Target"),
            ],
            connections=[
                block_models.Connection(source="A", target="B", arrow_type="-->"),
                block_models.Connection(source="B", target="A", arrow_type="<--"),
            ]
        )
        source = block_render.render_block(diagram)
        validate_mermaid_source(source)
