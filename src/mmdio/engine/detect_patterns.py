"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_detect_patterns.py.tmpl

Flowchart is deliberately excluded here: it is the documented default when
no other pattern matches, and mmdio.detect appends its own literal
graph/flowchart fallback patterns after this list. Keeping the "no real
signal, this is the default" case out of RDF-driven data avoids a type
whose ontology entry exists only to encode "I am the fallback."
"""

GENERATED_DETECT_PATTERNS = [
    (r"^\s*C4(?:Context|Container|Component|Dynamic|Deployment|Diagram)\b", "c4"),
    (r"^\s*classDiagram(?:-v2)?\b", "class"),
    (r"^\s*erDiagram\b", "er"),
    (r"^\s*gantt\b", "gantt"),
    (r"^\s*gitGraph\b", "git"),
    (r"^\s*mindmap\b", "mindmap"),
    (r"^\s*pie\b", "pie"),
    (r"^\s*sankey-beta\b", "sankey"),
    (r"^\s*sequenceDiagram\b", "sequence"),
    (r"^\s*stateDiagram(?:-v2)?\b", "state"),

]
