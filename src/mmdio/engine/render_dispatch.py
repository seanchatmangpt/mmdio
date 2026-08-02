"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_render_dispatch.py.tmpl
"""

from mmdio.engine.models import BlockDiagram
from mmdio.engine.render import render_block
from mmdio.engine.models import C4Diagram
from mmdio.engine.render import render_c4
from mmdio.engine.models import ClassDiagram
from mmdio.engine.render import render_class
from mmdio.engine.models import ERDiagram
from mmdio.engine.render import render_er
from mmdio.engine.models import FlowchartDiagram
from mmdio.engine.render import render_flowchart
from mmdio.engine.models import GanttChart
from mmdio.engine.render import render_gantt
from mmdio.engine.models import GitGraph
from mmdio.engine.render import render_git
from mmdio.engine.models import KanbanDiagram
from mmdio.engine.render import render_kanban
from mmdio.engine.models import Mindmap
from mmdio.engine.render import render_mindmap
from mmdio.engine.models import PieChart
from mmdio.engine.render import render_pie
from mmdio.engine.models import SankeyDiagram
from mmdio.engine.render import render_sankey
from mmdio.engine.models import SequenceDiagram
from mmdio.engine.render import render_sequence
from mmdio.engine.models import StateDiagram
from mmdio.engine.render import render_state
from mmdio.engine.models import TimelineDiagram
from mmdio.engine.render import render_timeline
from mmdio.engine.models import XYChartDiagram
from mmdio.engine.render import render_xychart

GENERATED_RENDER_DISPATCH = {
    BlockDiagram: render_block,
    C4Diagram: render_c4,
    ClassDiagram: render_class,
    ERDiagram: render_er,
    FlowchartDiagram: render_flowchart,
    GanttChart: render_gantt,
    GitGraph: render_git,
    KanbanDiagram: render_kanban,
    Mindmap: render_mindmap,
    PieChart: render_pie,
    SankeyDiagram: render_sankey,
    SequenceDiagram: render_sequence,
    StateDiagram: render_state,
    TimelineDiagram: render_timeline,
    XYChartDiagram: render_xychart,

}
