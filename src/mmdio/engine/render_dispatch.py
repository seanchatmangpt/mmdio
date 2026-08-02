"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from mmdio.engine.models import (
    C4Diagram,
    ClassDiagram,
    ERDiagram,
    FlowchartDiagram,
    GanttChart,
    GitGraph,
    MermaidDiagram,
    Mindmap,
    PieChart,
    SankeyDiagram,
    SequenceDiagram,
    StateDiagram,
)
from mmdio.engine.render import (
    render_c4,
    render_class,
    render_er,
    render_flowchart,
    render_gantt,
    render_git,
    render_mindmap,
    render_pie,
    render_sankey,
    render_sequence,
    render_state,
)

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


def render_diagram(d) -> str:
    """Render any MermaidDiagram model instance to Mermaid syntax string."""
    renderer = GENERATED_RENDER_DISPATCH.get(type(d))
    if not renderer:
        raise ValueError(f"Unsupported or unregistered diagram model type: {type(d)}")
    return renderer(d)

