"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from mmdio.engine.models import FlowchartDiagram
from mmdio.engine.render import render_flowchart
from mmdio.engine.models import SequenceDiagram
from mmdio.engine.render import render_sequence
from mmdio.engine.models import ClassDiagram
from mmdio.engine.render import render_class
from mmdio.engine.models import StateDiagram
from mmdio.engine.render import render_state
from mmdio.engine.models import ERDiagram
from mmdio.engine.render import render_er
from mmdio.engine.models import GanttChart
from mmdio.engine.render import render_gantt
from mmdio.engine.models import PieChart
from mmdio.engine.render import render_pie
from mmdio.engine.models import GitGraph
from mmdio.engine.render import render_git
from mmdio.engine.models import C4Diagram
from mmdio.engine.render import render_c4
from mmdio.engine.models import Mindmap
from mmdio.engine.render import render_mindmap
from mmdio.engine.models import SankeyDiagram
from mmdio.engine.render import render_sankey

GENERATED_RENDER_DISPATCH = {
    FlowchartDiagram: render_flowchart,
    SequenceDiagram: render_sequence,
    ClassDiagram: render_class,
    StateDiagram: render_state,
    ERDiagram: render_er,
    GanttChart: render_gantt,
    PieChart: render_pie,
    GitGraph: render_git,
    C4Diagram: render_c4,
    Mindmap: render_mindmap,
    SankeyDiagram: render_sankey,
}

def render_diagram(diagram) -> str:
    """Render an admitted diagram through the generated dispatch table."""
    try:
        renderer = GENERATED_RENDER_DISPATCH[type(diagram)]
    except KeyError as exc:
        raise ValueError(f"Unknown diagram type: {type(diagram)!r}") from exc
    return renderer(diagram)
