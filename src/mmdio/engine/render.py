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




def render_c4(d) -> str:
    """Render C4Diagram to Mermaid syntax."""
    lines = ["C4Context"]







    for _r1 in d.elements:
        lines.append(f'  {_r1.type}({_r1.id}, "{_r1.name}", "{_r1.description}")')













    for _r1 in d.relationships:
        lines.append(f'  Rel({_r1.source}, {_r1.target}, "{_r1.label}")')










    return "\n".join(lines)










def render_class(d) -> str:
    """Render ClassDiagram to Mermaid syntax."""
    lines = ["classDiagram"]



    for _r1 in d.classes:
        lines.append(f'  class {_r1.name}')





        for _r2 in _r1.members:
            lines.append(f'    {_r2.name} {_r2.type}')



        for _r2 in _r1.methods:
            lines.append(f'    {_r2.name}()')





    for _r1 in d.relationships:
        lines.append(f'  {_r1.from_class} -- {_r1.to_class}')












    return "\n".join(lines)
















def render_er(d) -> str:
    """Render ERDiagram to Mermaid syntax."""
    lines = ["erDiagram"]



    for _r1 in d.entities:
        lines.append(f'  {_r1.name}')





        for _r2 in _r1.attributes:
            lines.append(f'    {_r2.name} {_r2.attr_type}')





    for _r1 in d.relationships:
        lines.append(f'  {_r1.entity_a} {_r1.cardinality_a}--{_r1.cardinality_b} {_r1.entity_b} : {_r1.relation_type}')














    return "\n".join(lines)








def render_flowchart(d) -> str:
    """Render FlowchartDiagram to Mermaid syntax."""
    lines = ["flowchart"]





    for _r1 in d.nodes:
        lines.append(f'  {_r1.id}["{_r1.label}"]')











    for _r1 in d.edges:
        lines.append(f'  {_r1.source} --> {_r1.target}')












    return "\n".join(lines)








def render_gantt(d) -> str:
    """Render GanttChart to Mermaid syntax."""
    lines = ["gantt"]







    for _r1 in d.tasks:
        lines.append(f'  {_r1.id} : {_r1.status} , {_r1.start_date}, {_r1.end_date}')













        for _r2 in _r1.dependencies:
            lines.append(f'  ')




    return "\n".join(lines)












def render_git(d) -> str:
    """Render GitGraph to Mermaid syntax."""
    lines = ["gitGraph"]





    for _r1 in d.commits:
        lines.append(f'  commit id: "{_r1.id}"')








    return "\n".join(lines)






def render_kanban(d) -> str:
    """Render KanbanDiagram to Mermaid syntax."""
    lines = ["kanban"]



    for _r1 in d.sections:
        lines.append(f'  section {_r1.name}')





        for _r2 in _r1.cards:
            lines.append(f'    {_r2.title}')




    return "\n".join(lines)






def render_mindmap(d) -> str:
    """Render Mindmap to Mermaid syntax."""
    lines = ["mindmap"]



    lines.append(f'  {d.root.id}(({d.root.label}))')




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






def render_sequence(d) -> str:
    """Render SequenceDiagram to Mermaid syntax."""
    lines = ["sequenceDiagram"]





    for _r1 in d.participants:
        lines.append(f'  participant {_r1.id} as {_r1.name}')











    for _r1 in d.messages:
        lines.append(f'  {_r1.from_id}-{_r1.message_type}->{_r1.to_id}: {_r1.label}')














    return "\n".join(lines)








def render_state(d) -> str:
    """Render StateDiagram to Mermaid syntax."""
    lines = ["stateDiagram-v2"]





    for _r1 in d.states:
        lines.append(f'  {_r1.id}')









    for _r1 in d.transitions:
        lines.append(f'  {_r1.source} --> {_r1.target} : {_r1.label}')










    return "\n".join(lines)








def render_timeline(d) -> str:
    """Render TimelineDiagram to Mermaid syntax."""
    lines = ["timeline"]



    if d.title is not None:
        lines.append(f'    title {d.title}')



    for _r1 in d.events:
        lines.append(f'    {_r1.time} : {_r1.description}')








    return "\n".join(lines)








def render_xychart(d) -> str:
    """Render XYChartDiagram to Mermaid syntax."""
    lines = ["xychart-beta"]









    for _r1 in d.series:
        lines.append(f'  {_r1.series_type} {_r1.values}')








    return "\n".join(lines)




def render_diagram(d) -> str:
    """Render any MermaidDiagram model instance to Mermaid syntax string."""
    from mmdio.engine.render_dispatch import GENERATED_RENDER_DISPATCH
    renderer = GENERATED_RENDER_DISPATCH.get(type(d))
    if not renderer:
        raise ValueError(f"Unsupported or unregistered diagram model type: {type(d)}")
    return renderer(d)

