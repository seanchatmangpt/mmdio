"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_render_bodies.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonModel / mer:PythonField)

Two-level nesting only: a top-level *Diagram model's list-kind fields
(loop variable `_r1`), and each referenced element model's own list-kind
fields (loop variable `_r2`). A type needing a third level is not
representable by this template — gates/060_render_nesting_depth_limit.rq
refuses it explicitly rather than emitting a silently-wrong render body.

A top-level scalar-optional field with a fieldRenderFormat (e.g. `title`)
becomes a conditional single-line append, emitted in fieldOrder alongside
the list-field loops — matching the common "optional header line before
the items" shape (timeline's `title`, block's `columns`). A top-level
scalar field with NO fieldRenderFormat is silently skipped here: it still
exists on the Pydantic model (for parsing/round-trip) but doesn't
contribute to render output, which is the correct behavior for fields
that are structural-only. Not every field needs a render projection.
"""





def render_block(d) -> str:
    """Render BlockDiagram to Mermaid syntax."""
    lines = ["block-beta"]



    if d.columns is not None:
        lines.append(f'  columns {d.columns}')



    for _r1 in d.blocks:
        lines.append(f'  {_r1.id}["{_r1.label}"]')









    for _r1 in d.connections:
        lines.append(f'  {_r1.source} {_r1.arrow_type} {_r1.target}')












    return "\n".join(lines)








def render_kanban(d) -> str:
    """Render KanbanDiagram to Mermaid syntax."""
    lines = ["kanban"]



    for _r1 in d.sections:
        lines.append(f'  section {_r1.name}')





        for _r2 in _r1.cards:
            lines.append(f'    {_r2.title}')




    return "\n".join(lines)






def render_pie(d) -> str:
    """Render PieChart to Mermaid syntax."""
    lines = ["pie"]



    if d.title is not None:
        lines.append(f'title {d.title}')



    for _r1 in d.slices:
        lines.append(f'    "{_r1.label}" : {_r1.value}')








    return "\n".join(lines)






def render_sankey(d) -> str:
    """Render SankeyDiagram to Mermaid syntax."""
    lines = ["sankey-beta"]



    for _r1 in d.flows:
        lines.append(f'    {_r1.source},{_r1.target},{_r1.value}')










    return "\n".join(lines)






def render_timeline(d) -> str:
    """Render TimelineDiagram to Mermaid syntax."""
    lines = ["timeline"]



    if d.title is not None:
        lines.append(f'    title {d.title}')



    for _r1 in d.events:
        lines.append(f'    {_r1.time} : {_r1.description}')








    return "\n".join(lines)





