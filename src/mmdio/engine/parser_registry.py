"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""
from mmdio.engine.parser import C4Transformer
from mmdio.engine.parser import ClassTransformer
from mmdio.engine.parser import ERTransformer
from mmdio.engine.parser import FlowchartTransformer
from mmdio.engine.parser import GanttTransformer
from mmdio.engine.parser import GitTransformer
from mmdio.engine.parser import MindmapTransformer
from mmdio.engine.parser import PieTransformer
from mmdio.engine.parser import SankeyTransformer
from mmdio.engine.parser import SequenceTransformer
from mmdio.engine.parser import StateTransformer

GENERATED_TRANSFORMERS = {
    "c4": C4Transformer(),
    "class": ClassTransformer(),
    "er": ERTransformer(),
    "flowchart": FlowchartTransformer(),
    "gantt": GanttTransformer(),
    "git": GitTransformer(),
    "mindmap": MindmapTransformer(),
    "pie": PieTransformer(),
    "sankey": SankeyTransformer(),
    "sequence": SequenceTransformer(),
    "state": StateTransformer(),
}
GENERATED_GRAMMAR_FILES = {
    "c4": "c4.lark",
    "class": "class_diagram.lark",
    "er": "er.lark",
    "flowchart": "flowchart.lark",
    "gantt": "gantt.lark",
    "git": "git.lark",
    "mindmap": "mindmap.lark",
    "pie": "pie.lark",
    "sankey": "sankey.lark",
    "sequence": "sequence.lark",
    "state": "state.lark",
}
