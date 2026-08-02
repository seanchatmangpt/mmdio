"""
Lark Transformer and parser for XYChart diagram type.

Type-scoped parser to avoid conflicts with shared parser.py.
"""

from typing import Any, List

from lark import Lark, Token, Transformer, v_args

from mmdio.engine.types import xychart_models


def _unquote(token: Token | str) -> str:
    """Strip quotes and unescape string literals."""
    s = str(token)
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        s = s[1:-1]
    return s.replace('\\"', '"').replace("\\'", "'")


class XYChartTransformer(Transformer):
    """Transform xychart parse tree to XYChartDiagram."""

    def string(self, items: List[Any]) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def number(self, items: List[Any]) -> float:
        """Parse number."""
        return float(items[0])

    def value(self, items: List[Any]) -> float | str:
        """Parse axis or series value (can be number or string)."""
        if len(items) == 1:
            val = items[0]
            if isinstance(val, float):
                return val
            return val
        return items[0]

    def axis_values(self, items: List[Any]) -> List[float | str]:
        """Build list of axis values."""
        return items

    def series_values(self, items: List[Any]) -> List[float | str]:
        """Build list of series values."""
        return items

    def title(self, items: List[Any]) -> str:
        """Extract title text."""
        return str(items[0])

    def title_text(self, items: List[Any]) -> str:
        """Extract title text."""
        return str(items[0])

    def range(self, items: List[Any]) -> tuple[float, float]:
        """Parse min --> max range."""
        return (float(items[0]), float(items[1]))

    def x_axis(self, items: List[Any]) -> xychart_models.XYAxis:
        """Build x-axis."""
        values = items[0] if items else []
        return xychart_models.XYAxis(values=values)

    def y_axis_content(self, items: List[Any]) -> tuple[str | None, float | None, float | None]:
        """Parse y-axis content (label, range_min, range_max)."""
        label = None
        range_min = None
        range_max = None

        for item in items:
            if isinstance(item, str):
                label = item
            elif isinstance(item, tuple) and len(item) == 2:
                range_min, range_max = item

        return label, range_min, range_max

    def y_axis(self, items: List[Any]) -> xychart_models.XYAxis:
        """Build y-axis."""
        label, range_min, range_max = None, None, None

        if items:
            result = items[0]
            if isinstance(result, tuple):
                label, range_min, range_max = result
            elif isinstance(result, str):
                label = result

        return xychart_models.XYAxis(
            label=label, range_min=range_min, range_max=range_max
        )

    def series(self, items: List[Any]) -> xychart_models.DataSeries:
        """Build a data series."""
        # items[0] is the SERIES_TYPE token, items[1] is the series_values list
        series_type = str(items[0]).lower()
        values = items[1] if len(items) > 1 else []
        return xychart_models.DataSeries(series_type=series_type, values=values)

    def diagram(self, items: List[Any]) -> xychart_models.XYChartDiagram:
        """Build xychart diagram."""
        title = None
        x_axis = None
        y_axis = None
        series_list = []

        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, xychart_models.XYAxis):
                if x_axis is None:
                    x_axis = item
                else:
                    y_axis = item
            elif isinstance(item, xychart_models.DataSeries):
                series_list.append(item)

        # Ensure x_axis and y_axis are set
        if x_axis is None:
            x_axis = xychart_models.XYAxis()
        if y_axis is None:
            y_axis = xychart_models.XYAxis()

        return xychart_models.XYChartDiagram(
            title=title, x_axis=x_axis, y_axis=y_axis, series=series_list
        )

    def start(self, items: List[Any]) -> xychart_models.XYChartDiagram:
        """Start rule: pass through diagram."""
        return items[0] if items else xychart_models.XYChartDiagram(
            x_axis=xychart_models.XYAxis(), y_axis=xychart_models.XYAxis()
        )


def parse_xychart(source: str) -> xychart_models.XYChartDiagram:
    """
    Parse XYChart source into XYChartDiagram AST.

    Args:
        source: XYChart source code

    Returns:
        XYChartDiagram AST

    Raises:
        Exception: If parsing fails
    """
    # Load grammar from file
    import importlib.resources

    try:
        grammar_text = importlib.resources.files(
            "mmdio.engine.grammars"
        ).joinpath("xychart.lark").read_text(encoding="utf-8")
    except (FileNotFoundError, AttributeError):
        # Fallback for older Python versions
        from pathlib import Path

        grammar_path = Path(__file__).parent.parent / "grammars" / "xychart.lark"
        grammar_text = grammar_path.read_text(encoding="utf-8")

    # Parse
    lark_parser = Lark(grammar_text, parser="lalr", start="start")
    parse_tree = lark_parser.parse(source)

    # Transform
    transformer = XYChartTransformer()
    result = transformer.transform(parse_tree)

    return result
