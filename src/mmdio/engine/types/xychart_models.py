"""
Pydantic AST models for XYChart diagram type.

Type-scoped models to avoid conflicts with shared models.py.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AxisValue:
    """Represents a single axis value (number or string)."""
    pass


class XYAxisValue(BaseModel):
    """
    Represents a numeric or string value on an axis.
    """
    value: float | str = Field(
        ...,
        description="Numeric or string value for axis"
    )


class XYAxis(BaseModel):
    """
    Represents an XY chart axis (x or y).

    Attributes:
        label: Optional axis label
        values: List of axis values or tick marks
        range_min: Optional minimum value for y-axis range
        range_max: Optional maximum value for y-axis range
    """
    label: Optional[str] = Field(
        default=None,
        description="Optional axis label"
    )
    values: List[float | str] = Field(
        default_factory=list,
        description="Axis values or tick marks"
    )
    range_min: Optional[float] = Field(
        default=None,
        description="Minimum value for range (y-axis)"
    )
    range_max: Optional[float] = Field(
        default=None,
        description="Maximum value for range (y-axis)"
    )


class DataSeries(BaseModel):
    """
    Represents a data series in an XY chart.

    Attributes:
        series_type: Type of series (line, bar, scatter, bubble)
        values: List of numeric values for the series
    """
    series_type: str = Field(
        ...,
        description="Series type: line-series, bar-series, scatter-series, bubble-series"
    )
    values: List[float | str] = Field(
        default_factory=list,
        description="Numeric values for the series"
    )


class XYChartDiagram(BaseModel):
    """
    Represents an XY Chart diagram.

    XY charts plot data points on a Cartesian coordinate system with
    x and y axes, typically showing the relationship between two variables.

    Attributes:
        type: Discriminator field, always "xychart"
        title: Optional chart title
        x_axis: X-axis configuration
        y_axis: Y-axis configuration
        series: List of data series to plot
    """
    type: Literal["xychart"] = "xychart"
    title: Optional[str] = Field(
        default=None,
        description="Optional XY chart title"
    )
    x_axis: XYAxis = Field(
        ...,
        description="X-axis configuration"
    )
    y_axis: XYAxis = Field(
        ...,
        description="Y-axis configuration"
    )
    series: List[DataSeries] = Field(
        default_factory=list,
        description="List of data series"
    )
