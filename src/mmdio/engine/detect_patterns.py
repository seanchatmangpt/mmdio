"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_detect_patterns.py.tmpl

Flowchart is deliberately excluded here: it is the documented default when
no other pattern matches, and mmdio.detect appends its own literal
graph/flowchart fallback patterns after this list. Keeping the "no real
signal, this is the default" case out of RDF-driven data avoids a type
whose ontology entry exists only to encode "I am the fallback."
"""

GENERATED_DETECT_PATTERNS = [
    (r"^\s*block(-beta)?\b", "block"),
    (r"^\s*c4(context|diagram)\b", "c4"),
    (r"^\s*classdiagram\b", "class"),
    (r"^\s*erdiagram\b", "er"),
    (r"^\s*gantt\b", "gantt"),
    (r"^\s*gitgraph\b", "git"),
    (r"^\s*kanban\b", "kanban"),
    (r"^\s*mindmap\b", "mindmap"),
    (r"^\s*pie\s+", "pie"),
    (r"^\s*sankey-beta\b", "sankey"),
    (r"^\s*sequencediagram\b", "sequence"),
    (r"^\s*statediagram(-v2)?\b", "state"),
    (r"^\s*timeline\b", "timeline"),
    (r"^\s*xychart(-beta)?\b", "xychart"),

]
