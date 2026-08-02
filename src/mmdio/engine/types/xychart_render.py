"""
Render XYChart diagram to Mermaid syntax.

Type-scoped renderer to avoid conflicts with shared render.py.
"""

from mmdio.engine.types import xychart_models


def render_xychart(diagram: xychart_models.XYChartDiagram) -> str:
    """
    Render XYChart diagram to Mermaid syntax.

    Format:
        xychart-beta
            title My XY Chart
            x-axis [1, 2, 3, 4, 5]
            y-axis "Values" 0 --> 100
            line-series [10, 20, 30, 40, 50]

    Args:
        diagram: XYChartDiagram to render

    Returns:
        Mermaid source code
    """
    lines = ["xychart-beta"]

    # Add title if present
    if diagram.title:
        lines.append(f"    title {diagram.title}")

    # Add x-axis
    x_values = _format_values(diagram.x_axis.values)
    lines.append(f"    x-axis [{x_values}]")

    # Add y-axis
    y_axis_line = "    y-axis"
    if diagram.y_axis.label:
        # Check if label needs quoting
        label = diagram.y_axis.label
        if " " in label or any(c in label for c in ["-", ">"]):
            label = f'"{label}"'
        y_axis_line += f' {label}'
    if diagram.y_axis.range_min is not None and diagram.y_axis.range_max is not None:
        # Format numbers
        min_val = diagram.y_axis.range_min
        max_val = diagram.y_axis.range_max
        if isinstance(min_val, float) and min_val.is_integer():
            min_val = int(min_val)
        if isinstance(max_val, float) and max_val.is_integer():
            max_val = int(max_val)
        y_axis_line += f" {min_val} --> {max_val}"
    lines.append(y_axis_line)

    # Add data series
    for series in diagram.series:
        series_values = _format_values(series.values)
        lines.append(f"    {series.series_type} [{series_values}]")

    return "\n".join(lines)


def _format_values(values: list) -> str:
    """
    Format a list of values for output.

    Args:
        values: List of float or string values

    Returns:
        Comma-separated string representation
    """
    formatted = []
    for val in values:
        if isinstance(val, str):
            # Numeric strings should remain unquoted, non-numeric should be kept as-is
            # The parser handles string extraction from quotes
            formatted.append(val)
        else:
            # Numeric value
            if isinstance(val, float) and val.is_integer():
                formatted.append(str(int(val)))
            else:
                formatted.append(str(val))
    return ", ".join(formatted)
