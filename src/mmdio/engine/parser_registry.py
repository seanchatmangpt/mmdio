"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_parser_registry.py.tmpl
"""

from mmdio.engine.parser import BlockTransformer
from mmdio.engine.parser import C4Transformer
from mmdio.engine.parser import ClassTransformer
from mmdio.engine.parser import ERTransformer
from mmdio.engine.parser import FlowchartTransformer
from mmdio.engine.parser import GanttTransformer
from mmdio.engine.parser import GitTransformer
from mmdio.engine.parser import KanbanTransformer
from mmdio.engine.parser import MindmapTransformer
from mmdio.engine.parser import PieTransformer
from mmdio.engine.parser import SankeyTransformer
from mmdio.engine.parser import SequenceTransformer
from mmdio.engine.parser import StateTransformer
from mmdio.engine.parser import TimelineTransformer
from mmdio.engine.parser import XYChartTransformer

GENERATED_TRANSFORMERS = {
    "block": BlockTransformer(),
    "c4": C4Transformer(),
    "class": ClassTransformer(),
    "er": ERTransformer(),
    "flowchart": FlowchartTransformer(),
    "gantt": GanttTransformer(),
    "git": GitTransformer(),
    "kanban": KanbanTransformer(),
    "mindmap": MindmapTransformer(),
    "pie": PieTransformer(),
    "sankey": SankeyTransformer(),
    "sequence": SequenceTransformer(),
    "state": StateTransformer(),
    "timeline": TimelineTransformer(),
    "xychart": XYChartTransformer(),

}

GENERATED_GRAMMAR_FILES = {
    "block": "block.lark",
    "c4": "c4.lark",
    "class": "class_diagram.lark",
    "er": "er.lark",
    "flowchart": "flowchart.lark",
    "gantt": "gantt.lark",
    "git": "git.lark",
    "kanban": "kanban.lark",
    "mindmap": "mindmap.lark",
    "pie": "pie.lark",
    "sankey": "sankey.lark",
    "sequence": "sequence.lark",
    "state": "state.lark",
    "timeline": "timeline.lark",
    "xychart": "xychart.lark",

}
