"""
Oracle test for XYChart diagram type.

Validates rendered output against real mermaid-js parser.
"""

import sys
from pathlib import Path

import pytest

# Add parent test directory to path to import validate_mermaid_source
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_oracle_roundtrip import check_node_available, validate_mermaid_source

from mmdio.engine.types import xychart_models, xychart_render


# Skip tests if Node/npm not available
pytestmark = pytest.mark.skipif(
    not check_node_available(),
    reason="Node.js or npm dependencies not available (run: cd tests/oracle && npm ci)"
)


class TestOracleXYChart:
    """Test XYChart rendering and oracle validation."""

    def test_xychart_simple(self) -> None:
        """Test simple XY chart with line and bar series."""
        # Create XYChart AST
        diagram = xychart_models.XYChartDiagram(
            title="Sales Data",
            x_axis=xychart_models.XYAxis(
                values=[1, 2, 3, 4, 5]
            ),
            y_axis=xychart_models.XYAxis(
                label="Revenue",
                range_min=0,
                range_max=100
            ),
            series=[
                xychart_models.DataSeries(
                    series_type="line-series",
                    values=[10, 20, 30, 40, 50]
                ),
                xychart_models.DataSeries(
                    series_type="bar-series",
                    values=[15, 25, 35, 45, 55]
                ),
            ]
        )

        # Render to Mermaid source
        source = xychart_render.render_xychart(diagram)

        # Validate against mermaid-js
        validate_mermaid_source(source)

    def test_xychart_with_strings(self) -> None:
        """Test XY chart with string axis values."""
        diagram = xychart_models.XYChartDiagram(
            title="Quarterly Performance",
            x_axis=xychart_models.XYAxis(
                values=["Q1", "Q2", "Q3", "Q4"]
            ),
            y_axis=xychart_models.XYAxis(
                label="Profit",
                range_min=0,
                range_max=200
            ),
            series=[
                xychart_models.DataSeries(
                    series_type="bar-series",
                    values=[50, 75, 100, 125]
                ),
            ]
        )

        source = xychart_render.render_xychart(diagram)
        validate_mermaid_source(source)

    def test_xychart_without_title(self) -> None:
        """Test XY chart without title."""
        diagram = xychart_models.XYChartDiagram(
            x_axis=xychart_models.XYAxis(
                values=[1, 2, 3]
            ),
            y_axis=xychart_models.XYAxis(
                range_min=0,
                range_max=50
            ),
            series=[
                xychart_models.DataSeries(
                    series_type="scatter-series",
                    values=[10, 20, 30]
                ),
            ]
        )

        source = xychart_render.render_xychart(diagram)
        validate_mermaid_source(source)
