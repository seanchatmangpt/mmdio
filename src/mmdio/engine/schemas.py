"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_schemas.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonModel / mer:PythonField)

One file, all types: GENERATED_JSON_SCHEMAS maps each top-level diagram id
to its JSON Schema dict (nested models inlined, not $ref'd — every model
in this codebase is at most two levels deep, so inlining stays readable).
This is a free correctness/interop artifact, not consumed by mmdio's own
parse/render path.
"""

_PY_TO_JSON_TYPE = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
}


def _json_type_for(py_type: str) -> dict:
    """Map a bare Python type fragment to a JSON Schema type fragment."""
    if py_type in _PY_TO_JSON_TYPE:
        return {"type": _PY_TO_JSON_TYPE[py_type]}
    if "|" in py_type:
        return {"type": [_PY_TO_JSON_TYPE.get(p.strip(), "string") for p in py_type.split("|")]}
    return {"$comment": f"nested model {py_type}", "type": "object"}



_SCHEMA_Block = {
    "type": "object",
    "description": "Block",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Block identifier",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Block label text",
        },

    },
    "required": [


        "id",



        "label",


    ],
}

_SCHEMA_BlockDiagram = {
    "type": "object",
    "description": "BlockDiagram",
    "properties": {


        "columns": {

            **_json_type_for("int"),

            "description": "Optional column count for layout",
        },

        "blocks": {

            "type": "array",
            "items": _json_type_for("Block"),

            "description": "List of blocks in the diagram",
        },

        "connections": {

            "type": "array",
            "items": _json_type_for("Connection"),

            "description": "List of connections between blocks",
        },

    },
    "required": [







    ],
}

_SCHEMA_C4Diagram = {
    "type": "object",
    "description": "C4Diagram",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Diagram title",
        },

        "level": {

            **_json_type_for("C4Level"),

            "description": "C4 level (C1, C2, C3, C4)",
        },

        "elements": {

            "type": "array",
            "items": _json_type_for("C4Element"),

            "description": "Systems, containers, or components",
        },

        "relationships": {

            "type": "array",
            "items": _json_type_for("C4Relationship"),

            "description": "Relationships between elements",
        },

    },
    "required": [









    ],
}

_SCHEMA_C4Element = {
    "type": "object",
    "description": "C4Element",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Element identifier",
        },

        "name": {

            **_json_type_for("str"),

            "description": "Element name",
        },

        "description": {

            **_json_type_for("str"),

            "description": "Element description",
        },

        "type": {

            **_json_type_for("str"),

            "description": "Element type (System, Person, Container, etc.)",
        },

    },
    "required": [


        "id",



        "name",





        "type",


    ],
}

_SCHEMA_C4Relationship = {
    "type": "object",
    "description": "C4Relationship",
    "properties": {


        "source": {

            **_json_type_for("str"),

            "description": "Source element ID",
        },

        "target": {

            **_json_type_for("str"),

            "description": "Target element ID",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Relationship description",
        },

    },
    "required": [


        "source",



        "target",




    ],
}

_SCHEMA_ClassDefinition = {
    "type": "object",
    "description": "ClassDefinition",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Class/interface name",
        },

        "members": {

            "type": "array",
            "items": _json_type_for("ClassMember"),

            "description": "List of class members",
        },

        "methods": {

            "type": "array",
            "items": _json_type_for("ClassMethod"),

            "description": "List of class methods",
        },

    },
    "required": [


        "name",






    ],
}

_SCHEMA_ClassDiagram = {
    "type": "object",
    "description": "ClassDiagram",
    "properties": {


        "classes": {

            "type": "array",
            "items": _json_type_for("ClassDefinition"),

            "description": "List of class definitions",
        },

        "relationships": {

            "type": "array",
            "items": _json_type_for("ClassRelationship"),

            "description": "List of relationships between classes",
        },

    },
    "required": [





    ],
}

_SCHEMA_ClassMember = {
    "type": "object",
    "description": "ClassMember",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Member name",
        },

        "type": {

            **_json_type_for("str"),

            "description": "Type annotation",
        },

        "visibility": {

            **_json_type_for("str"),

            "description": "Visibility modifier (+, -, #, ~)",
        },

    },
    "required": [


        "name",






    ],
}

_SCHEMA_ClassMethod = {
    "type": "object",
    "description": "ClassMethod",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Method name",
        },

        "signature": {

            **_json_type_for("str"),

            "description": "Full method signature",
        },

        "return_type": {

            **_json_type_for("str"),

            "description": "Return type annotation",
        },

        "visibility": {

            **_json_type_for("str"),

            "description": "Visibility modifier",
        },

    },
    "required": [


        "name",








    ],
}

_SCHEMA_ClassRelationship = {
    "type": "object",
    "description": "ClassRelationship",
    "properties": {


        "from_class": {

            **_json_type_for("str"),

            "description": "Source class name",
        },

        "to_class": {

            **_json_type_for("str"),

            "description": "Target class name",
        },

        "type": {

            **_json_type_for("RelationshipType"),

            "description": "Type of relationship",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Optional relationship label",
        },

    },
    "required": [


        "from_class",



        "to_class",






    ],
}

_SCHEMA_Connection = {
    "type": "object",
    "description": "Connection",
    "properties": {


        "source": {

            **_json_type_for("str"),

            "description": "Source block ID",
        },

        "target": {

            **_json_type_for("str"),

            "description": "Target block ID",
        },

        "arrow_type": {

            **_json_type_for("str"),

            "description": "Arrow type (-->, <--, <-->, ===, --x, o--)",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Optional connection label",
        },

    },
    "required": [


        "source",



        "target",






    ],
}

_SCHEMA_DataSeries = {
    "type": "object",
    "description": "DataSeries",
    "properties": {


        "series_type": {

            **_json_type_for("str"),

            "description": "Series type: line, bar, scatter, bubble",
        },

        "values": {

            "type": "array",
            "items": _json_type_for("float | str"),

            "description": "Series data values",
        },

    },
    "required": [


        "series_type",




    ],
}

_SCHEMA_ERAttribute = {
    "type": "object",
    "description": "ERAttribute",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Attribute name",
        },

        "attr_type": {

            **_json_type_for("str"),

            "description": "Attribute type (int, string, etc.)",
        },

    },
    "required": [


        "name",



        "attr_type",


    ],
}

_SCHEMA_ERDiagram = {
    "type": "object",
    "description": "ERDiagram",
    "properties": {


        "entities": {

            "type": "array",
            "items": _json_type_for("EREntity"),

            "description": "List of entities",
        },

        "relationships": {

            "type": "array",
            "items": _json_type_for("ERRelationship"),

            "description": "List of entity relationships",
        },

    },
    "required": [





    ],
}

_SCHEMA_EREntity = {
    "type": "object",
    "description": "EREntity",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Entity name",
        },

        "attributes": {

            "type": "array",
            "items": _json_type_for("ERAttribute"),

            "description": "Entity attributes",
        },

    },
    "required": [


        "name",




    ],
}

_SCHEMA_ERRelationship = {
    "type": "object",
    "description": "ERRelationship",
    "properties": {


        "entity_a": {

            **_json_type_for("str"),

            "description": "First entity name",
        },

        "entity_b": {

            **_json_type_for("str"),

            "description": "Second entity name",
        },

        "cardinality_a": {

            **_json_type_for("str"),

            "description": "Cardinality of entity_a side",
        },

        "cardinality_b": {

            **_json_type_for("str"),

            "description": "Cardinality of entity_b side",
        },

        "relation_type": {

            **_json_type_for("RelationshipType"),

            "description": "Type of relationship",
        },

    },
    "required": [


        "entity_a",



        "entity_b",



        "cardinality_a",



        "cardinality_b",




    ],
}

_SCHEMA_FlowchartDiagram = {
    "type": "object",
    "description": "FlowchartDiagram",
    "properties": {


        "direction": {

            **_json_type_for("str"),

            "description": "Layout direction: TD, LR, BT, RL",
        },

        "nodes": {

            "type": "array",
            "items": _json_type_for("FlowchartNode"),

            "description": "List of nodes in the flowchart",
        },

        "edges": {

            "type": "array",
            "items": _json_type_for("FlowchartEdge"),

            "description": "List of edges/connections between nodes",
        },

    },
    "required": [







    ],
}

_SCHEMA_FlowchartEdge = {
    "type": "object",
    "description": "FlowchartEdge",
    "properties": {


        "source": {

            **_json_type_for("str"),

            "description": "Source node ID",
        },

        "target": {

            **_json_type_for("str"),

            "description": "Target node ID",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Optional edge label",
        },

        "edge_type": {

            **_json_type_for("str"),

            "description": "Edge style: solid, dotted, thick",
        },

    },
    "required": [


        "source",



        "target",






    ],
}

_SCHEMA_FlowchartNode = {
    "type": "object",
    "description": "FlowchartNode",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Node identifier",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Node display label",
        },

        "node_type": {

            **_json_type_for("NodeShape"),

            "description": "Node shape (rectangle, circle, diamond, etc.)",
        },

    },
    "required": [


        "id",



        "label",




    ],
}

_SCHEMA_GanttChart = {
    "type": "object",
    "description": "GanttChart",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Chart title",
        },

        "date_format": {

            **_json_type_for("str"),

            "description": "Date format (YYYY-MM-DD, etc.)",
        },

        "tasks": {

            "type": "array",
            "items": _json_type_for("GanttTask"),

            "description": "List of tasks",
        },

    },
    "required": [







    ],
}

_SCHEMA_GanttDependency = {
    "type": "object",
    "description": "GanttDependency",
    "properties": {


        "task_id": {

            **_json_type_for("str"),

            "description": "ID of dependent task",
        },

    },
    "required": [


        "task_id",


    ],
}

_SCHEMA_GanttTask = {
    "type": "object",
    "description": "GanttTask",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Task identifier",
        },

        "title": {

            **_json_type_for("str"),

            "description": "Task title/name",
        },

        "status": {

            **_json_type_for("TaskStatus"),

            "description": "Task status (active, done, milestone, crit, etc.)",
        },

        "start_date": {

            **_json_type_for("str"),

            "description": "Task start date",
        },

        "end_date": {

            **_json_type_for("str"),

            "description": "Task end date",
        },

        "dependencies": {

            "type": "array",
            "items": _json_type_for("GanttDependency"),

            "description": "Task dependencies",
        },

    },
    "required": [


        "id",



        "title",





        "start_date",



        "end_date",




    ],
}

_SCHEMA_GitBranch = {
    "type": "object",
    "description": "GitBranch",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Branch name",
        },

    },
    "required": [


        "name",


    ],
}

_SCHEMA_GitCommit = {
    "type": "object",
    "description": "GitCommit",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Commit identifier (hash)",
        },

        "message": {

            **_json_type_for("str"),

            "description": "Commit message",
        },

    },
    "required": [


        "id",




    ],
}

_SCHEMA_GitGraph = {
    "type": "object",
    "description": "GitGraph",
    "properties": {


        "main_branch": {

            **_json_type_for("str"),

            "description": "Main branch name",
        },

        "commits": {

            "type": "array",
            "items": _json_type_for("GitCommit"),

            "description": "List of commits",
        },

    },
    "required": [





    ],
}

_SCHEMA_KanbanCard = {
    "type": "object",
    "description": "KanbanCard",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Card title/task name",
        },

    },
    "required": [


        "title",


    ],
}

_SCHEMA_KanbanDiagram = {
    "type": "object",
    "description": "KanbanDiagram",
    "properties": {


        "sections": {

            "type": "array",
            "items": _json_type_for("KanbanSection"),

            "description": "List of Kanban sections/columns",
        },

    },
    "required": [



    ],
}

_SCHEMA_KanbanSection = {
    "type": "object",
    "description": "KanbanSection",
    "properties": {


        "name": {

            **_json_type_for("str"),

            "description": "Section name (e.g., To Do, In Progress)",
        },

        "cards": {

            "type": "array",
            "items": _json_type_for("KanbanCard"),

            "description": "Cards in this section",
        },

    },
    "required": [


        "name",




    ],
}

_SCHEMA_Mindmap = {
    "type": "object",
    "description": "Mindmap",
    "properties": {


        "root": {

            **_json_type_for("MindmapNode"),

            "description": "Root node of the mindmap tree",
        },

        "title": {

            **_json_type_for("str"),

            "description": "Optional mindmap title",
        },

    },
    "required": [


        "root",




    ],
}

_SCHEMA_MindmapNode = {
    "type": "object",
    "description": "MindmapNode",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Unique node identifier",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Node label/text",
        },

    },
    "required": [


        "id",



        "label",


    ],
}

_SCHEMA_PieChart = {
    "type": "object",
    "description": "PieChart",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Optional chart title",
        },

        "slices": {

            "type": "array",
            "items": _json_type_for("PieSlice"),

            "description": "List of pie slices",
        },

    },
    "required": [





    ],
}

_SCHEMA_PieSlice = {
    "type": "object",
    "description": "PieSlice",
    "properties": {


        "label": {

            **_json_type_for("str"),

            "description": "Slice label",
        },

        "value": {

            **_json_type_for("float"),

            "description": "Numeric value (percentage, count, or amount)",
        },

    },
    "required": [


        "label",



        "value",


    ],
}

_SCHEMA_SankeyDiagram = {
    "type": "object",
    "description": "SankeyDiagram",
    "properties": {


        "flows": {

            "type": "array",
            "items": _json_type_for("SankeyFlow"),

            "description": "List of flows in the diagram",
        },

    },
    "required": [



    ],
}

_SCHEMA_SankeyFlow = {
    "type": "object",
    "description": "SankeyFlow",
    "properties": {


        "source": {

            **_json_type_for("str"),

            "description": "Source node identifier",
        },

        "target": {

            **_json_type_for("str"),

            "description": "Target node identifier",
        },

        "value": {

            **_json_type_for("float"),

            "description": "Flow value (determines width/thickness of flow)",
        },

    },
    "required": [


        "source",



        "target",



        "value",


    ],
}

_SCHEMA_SequenceDiagram = {
    "type": "object",
    "description": "SequenceDiagram",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Optional diagram title",
        },

        "participants": {

            "type": "array",
            "items": _json_type_for("SequenceParticipant"),

            "description": "List of sequence participants",
        },

        "messages": {

            "type": "array",
            "items": _json_type_for("SequenceMessage"),

            "description": "List of messages between participants",
        },

    },
    "required": [







    ],
}

_SCHEMA_SequenceMessage = {
    "type": "object",
    "description": "SequenceMessage",
    "properties": {


        "from_id": {

            **_json_type_for("str"),

            "description": "Source participant ID",
        },

        "to_id": {

            **_json_type_for("str"),

            "description": "Target participant ID",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Message text/label",
        },

        "message_type": {

            **_json_type_for("MessageType"),

            "description": "Message type: sync, async, return, autonumber",
        },

        "sequence_number": {

            **_json_type_for("int"),

            "description": "Auto-assigned message sequence number",
        },

    },
    "required": [


        "from_id",



        "to_id",







        "sequence_number",


    ],
}

_SCHEMA_SequenceParticipant = {
    "type": "object",
    "description": "SequenceParticipant",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "Participant identifier",
        },

        "name": {

            **_json_type_for("str"),

            "description": "Participant display name",
        },

        "participant_type": {

            **_json_type_for("ParticipantType"),

            "description": "Participant type: actor, participant",
        },

    },
    "required": [


        "id",



        "name",




    ],
}

_SCHEMA_StateDiagram = {
    "type": "object",
    "description": "StateDiagram",
    "properties": {


        "initial_state": {

            **_json_type_for("str"),

            "description": "Initial state identifier",
        },

        "states": {

            "type": "array",
            "items": _json_type_for("StateNode"),

            "description": "List of states",
        },

        "transitions": {

            "type": "array",
            "items": _json_type_for("StateTransition"),

            "description": "List of transitions between states",
        },

    },
    "required": [







    ],
}

_SCHEMA_StateNode = {
    "type": "object",
    "description": "StateNode",
    "properties": {


        "id": {

            **_json_type_for("str"),

            "description": "State identifier",
        },

        "label": {

            **_json_type_for("str"),

            "description": "State display label",
        },

    },
    "required": [


        "id",




    ],
}

_SCHEMA_StateTransition = {
    "type": "object",
    "description": "StateTransition",
    "properties": {


        "source": {

            **_json_type_for("str"),

            "description": "Source state ID",
        },

        "target": {

            **_json_type_for("str"),

            "description": "Target state ID",
        },

        "label": {

            **_json_type_for("str"),

            "description": "Transition label/trigger",
        },

    },
    "required": [


        "source",



        "target",




    ],
}

_SCHEMA_TimelineDiagram = {
    "type": "object",
    "description": "TimelineDiagram",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Optional timeline title",
        },

        "events": {

            "type": "array",
            "items": _json_type_for("TimelineEvent"),

            "description": "List of timeline events",
        },

    },
    "required": [





    ],
}

_SCHEMA_TimelineEvent = {
    "type": "object",
    "description": "TimelineEvent",
    "properties": {


        "time": {

            **_json_type_for("str"),

            "description": "Event time/date (e.g., 2024-01-01, January, Q1)",
        },

        "description": {

            **_json_type_for("str"),

            "description": "Event description or label",
        },

    },
    "required": [


        "time",



        "description",


    ],
}

_SCHEMA_XYAxis = {
    "type": "object",
    "description": "XYAxis",
    "properties": {


        "label": {

            **_json_type_for("str"),

            "description": "Axis label",
        },

        "values": {

            "type": "array",
            "items": _json_type_for("float | str"),

            "description": "Axis values or tick marks",
        },

        "range_min": {

            **_json_type_for("float"),

            "description": "Minimum range (y-axis)",
        },

        "range_max": {

            **_json_type_for("float"),

            "description": "Maximum range (y-axis)",
        },

    },
    "required": [









    ],
}

_SCHEMA_XYChartDiagram = {
    "type": "object",
    "description": "XYChartDiagram",
    "properties": {


        "title": {

            **_json_type_for("str"),

            "description": "Chart title",
        },

        "x_axis": {

            **_json_type_for("XYAxis"),

            "description": "X-axis configuration",
        },

        "y_axis": {

            **_json_type_for("XYAxis"),

            "description": "Y-axis configuration",
        },

        "series": {

            "type": "array",
            "items": _json_type_for("DataSeries"),

            "description": "Data series to plot",
        },

    },
    "required": [




        "x_axis",



        "y_axis",




    ],
}


GENERATED_JSON_SCHEMAS = {




    "block": _SCHEMA_BlockDiagram,



    "c4": _SCHEMA_C4Diagram,









    "class": _SCHEMA_ClassDiagram,















    "er": _SCHEMA_ERDiagram,







    "flowchart": _SCHEMA_FlowchartDiagram,







    "gantt": _SCHEMA_GanttChart,











    "git": _SCHEMA_GitGraph,





    "kanban": _SCHEMA_KanbanDiagram,





    "mindmap": _SCHEMA_Mindmap,





    "pie": _SCHEMA_PieChart,





    "sankey": _SCHEMA_SankeyDiagram,





    "sequence": _SCHEMA_SequenceDiagram,







    "state": _SCHEMA_StateDiagram,







    "timeline": _SCHEMA_TimelineDiagram,







    "xychart": _SCHEMA_XYChartDiagram,


}
