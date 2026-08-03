"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from mmdio.engine.models import MermaidDiagram
from mmdio.engine.models import C4Diagram
from mmdio.engine.models import ClassDiagram
from mmdio.engine.models import ERDiagram
from mmdio.engine.models import FlowchartDiagram
from mmdio.engine.models import GanttChart
from mmdio.engine.models import GitGraph
from mmdio.engine.models import Mindmap
from mmdio.engine.models import PieChart
from mmdio.engine.models import SankeyDiagram
from mmdio.engine.models import SequenceDiagram
from mmdio.engine.models import StateDiagram
from mmdio.engine.render import render_c4
from mmdio.engine.render import render_class
from mmdio.engine.render import render_er
from mmdio.engine.render import render_flowchart
from mmdio.engine.render import render_gantt
from mmdio.engine.render import render_git
from mmdio.engine.render import render_mindmap
from mmdio.engine.render import render_pie
from mmdio.engine.render import render_sankey
from mmdio.engine.render import render_sequence
from mmdio.engine.render import render_state

GENERATED_RENDER_DISPATCH = {
    C4Diagram: render_c4,
    ClassDiagram: render_class,
    ERDiagram: render_er,
    FlowchartDiagram: render_flowchart,
    GanttChart: render_gantt,
    GitGraph: render_git,
    Mindmap: render_mindmap,
    PieChart: render_pie,
    SankeyDiagram: render_sankey,
    SequenceDiagram: render_sequence,
    StateDiagram: render_state,
}


def render_diagram(diagram: MermaidDiagram) -> str:
    """Render one admitted Mermaid model through generated type dispatch."""
    if isinstance(diagram, C4Diagram):
        return render_c4(diagram)
    if isinstance(diagram, ClassDiagram):
        return render_class(diagram)
    if isinstance(diagram, ERDiagram):
        return render_er(diagram)
    if isinstance(diagram, FlowchartDiagram):
        return render_flowchart(diagram)
    if isinstance(diagram, GanttChart):
        return render_gantt(diagram)
    if isinstance(diagram, GitGraph):
        return render_git(diagram)
    if isinstance(diagram, Mindmap):
        return render_mindmap(diagram)
    if isinstance(diagram, PieChart):
        return render_pie(diagram)
    if isinstance(diagram, SankeyDiagram):
        return render_sankey(diagram)
    if isinstance(diagram, SequenceDiagram):
        return render_sequence(diagram)
    if isinstance(diagram, StateDiagram):
        return render_state(diagram)
    raise ValueError(f"Unknown diagram type: {type(diagram)!r}")


def render_model(diagram: MermaidDiagram) -> str:
    """Compatibility name for generated render dispatch."""
    return render_diagram(diagram)
