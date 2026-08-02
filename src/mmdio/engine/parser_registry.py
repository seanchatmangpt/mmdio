"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from mmdio.engine.parser import FlowchartTransformer
from mmdio.engine.parser import SequenceTransformer
from mmdio.engine.parser import ClassTransformer
from mmdio.engine.parser import StateTransformer
from mmdio.engine.parser import ERTransformer
from mmdio.engine.parser import GanttTransformer
from mmdio.engine.parser import PieTransformer
from mmdio.engine.parser import GitTransformer
from mmdio.engine.parser import C4Transformer
from mmdio.engine.parser import MindmapTransformer
from mmdio.engine.parser import SankeyTransformer

GENERATED_TRANSFORMERS = {
    "flowchart": FlowchartTransformer(),
    "sequence": SequenceTransformer(),
    "class": ClassTransformer(),
    "state": StateTransformer(),
    "er": ERTransformer(),
    "gantt": GanttTransformer(),
    "pie": PieTransformer(),
    "git": GitTransformer(),
    "c4": C4Transformer(),
    "mindmap": MindmapTransformer(),
    "sankey": SankeyTransformer(),
}

GENERATED_GRAMMAR_FILES = {
    "flowchart": "flowchart.lark",
    "sequence": "sequence.lark",
    "class": "class_diagram.lark",
    "state": "state.lark",
    "er": "er.lark",
    "gantt": "gantt.lark",
    "pie": "pie.lark",
    "git": "git.lark",
    "c4": "c4.lark",
    "mindmap": "mindmap.lark",
    "sankey": "sankey.lark",
}
