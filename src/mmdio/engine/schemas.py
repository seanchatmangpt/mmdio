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


GENERATED_JSON_SCHEMAS = {




    "block": _SCHEMA_BlockDiagram,







    "kanban": _SCHEMA_KanbanDiagram,





    "pie": _SCHEMA_PieChart,





    "sankey": _SCHEMA_SankeyDiagram,





    "timeline": _SCHEMA_TimelineDiagram,




}
