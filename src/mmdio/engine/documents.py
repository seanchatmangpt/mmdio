"""GENERATED FILE — projected from the mmdio 39-type capability ontology."""

from __future__ import annotations

from typing import Literal

from mmdio.engine.universal import DiagramType, MermaidDocument

_DOCUMENT_NAMES: dict[DiagramType, str] = {
    DiagramType.C4: "C4Document",
    DiagramType.FLOWCHART: "FlowchartDocument",
    DiagramType.FLOWCHART_V2: "FlowchartV2Document",
    DiagramType.FLOWCHART_ELK: "FlowchartElkDocument",
    DiagramType.SWIMLANE: "SwimlaneDocument",
    DiagramType.ER: "ERDocument",
    DiagramType.GIT_GRAPH: "GitGraphDocument",
    DiagramType.GANTT: "GanttDocument",
    DiagramType.INFO: "InfoDocument",
    DiagramType.PIE: "PieDocument",
    DiagramType.QUADRANT: "QuadrantChartDocument",
    DiagramType.XYCHART: "XYChartDocument",
    DiagramType.REQUIREMENT: "RequirementDocument",
    DiagramType.SEQUENCE: "SequenceDocument",
    DiagramType.CLASS: "ClassDiagramDocument",
    DiagramType.CLASS_V2: "ClassDiagramV2Document",
    DiagramType.STATE: "StateDiagramDocument",
    DiagramType.STATE_V2: "StateDiagramV2Document",
    DiagramType.JOURNEY: "JourneyDocument",
    DiagramType.TIMELINE: "TimelineDocument",
    DiagramType.MINDMAP: "MindmapDocument",
    DiagramType.KANBAN: "KanbanDocument",
    DiagramType.SANKEY: "SankeyDocument",
    DiagramType.PACKET: "PacketDocument",
    DiagramType.RADAR: "RadarDocument",
    DiagramType.BLOCK: "BlockDocument",
    DiagramType.TREE_VIEW: "TreeViewDocument",
    DiagramType.ARCHITECTURE: "ArchitectureDocument",
    DiagramType.EVENT_MODELING: "EventModelingDocument",
    DiagramType.ISHIKAWA: "IshikawaDocument",
    DiagramType.VENN: "VennDocument",
    DiagramType.TREEMAP: "TreemapDocument",
    DiagramType.WARDLEY: "WardleyDocument",
    DiagramType.CYNEFIN: "CynefinDocument",
    DiagramType.RAILROAD: "RailroadDocument",
    DiagramType.RAILROAD_EBNF: "RailroadEbnfDocument",
    DiagramType.RAILROAD_ABNF: "RailroadAbnfDocument",
    DiagramType.RAILROAD_PEG: "RailroadPegDocument",
    DiagramType.ZENUML: "ZenUMLDocument",
}


def _manufacture_document_class(diagram_type: DiagramType, name: str) -> type[MermaidDocument]:
    """Manufacture one exact Pydantic subclass from admitted ontology identity."""
    namespace = {
        "__module__": __name__,
        "__doc__": f"Lossless structured document for ``{diagram_type.value}``.",
        "__annotations__": {"type": Literal[diagram_type]},
        "expected_type": diagram_type,
        "type": diagram_type,
    }
    return type(name, (MermaidDocument,), namespace)


DOCUMENT_CLASS_BY_TYPE: dict[DiagramType, type[MermaidDocument]] = {}
for _diagram_type, _class_name in _DOCUMENT_NAMES.items():
    _class = _manufacture_document_class(_diagram_type, _class_name)
    globals()[_class_name] = _class
    DOCUMENT_CLASS_BY_TYPE[_diagram_type] = _class

__all__ = [*sorted(_DOCUMENT_NAMES.values()), "DOCUMENT_CLASS_BY_TYPE"]
