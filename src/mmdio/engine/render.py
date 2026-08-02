"""Specialized Mermaid renderers.

Models and dispatch metadata are generated from RDF. Rendering remains specialized
because Mermaid syntax requires conditional branches, enum-to-token maps, escaping,
and recursion that a fixed row-format template cannot lawfully reproduce.
"""
from __future__ import annotations
from mmdio.engine.models import *  # noqa: F401,F403


def _q(value: str) -> str:
    return value.replace('"', '\\"')


def render_flowchart(d: FlowchartDiagram) -> str:
    lines=[f"graph {d.direction}"]
    markers={NodeShape.RECTANGLE:("[","]"),NodeShape.CIRCLE:("((","))"),NodeShape.ELLIPSE:("(",")"),NodeShape.DIAMOND:("{","}"),NodeShape.HEXAGON:("{{","}}"),NodeShape.TRAPEZOID:("[/","/]"),NodeShape.PARALLELOGRAM:("[\\","\\]"),NodeShape.DOCUMENT:("[\\","\\]"),NodeShape.CYLINDER:("[(",")]"),NodeShape.SUBROUTINE:("[[","]]"),}
    arrows={"solid":"-->","dotted":"-.->","thick":"==>"}
    for n in d.nodes:
        op,cl=markers.get(n.shape,("[","]")); lines.append(f'{n.id}{op}{_q(n.label)}{cl}')
    for e in d.edges:
        arrow=arrows.get(e.style or "solid","-->")
        lines.append(f'{e.source} {arrow}|{_q(e.label)}| {e.target}' if e.label else f'{e.source} {arrow} {e.target}')
    return "\n".join(lines)


def render_sequence(d: SequenceDiagram) -> str:
    lines=["sequenceDiagram"]
    if d.title: lines.append(f"    title {d.title}")
    for p in d.participants: lines.append(f"    {p.type} {p.id} as {p.name}")
    arrows={MessageType.SYNC:"->>",MessageType.ASYNC:"-->>",MessageType.RETURN:"-->>",MessageType.AUTONUMBER:"->>"}
    for msg in sorted(d.messages,key=lambda x:x.sequence_number or 0): lines.append(f"    {msg.from_participant}{arrows.get(msg.type,'->>')}{msg.to_participant}: {_q(msg.label)}")
    return "\n".join(lines)


def render_class(d: ClassDiagram) -> str:
    lines=["classDiagram"]
    for c in d.classes:
        lines.append(f"    class {c.name} {{")
        for a in c.members: lines.append(f"        {a.visibility}{(a.type+' ') if a.type else ''}{a.name}")
        for op in c.methods:
            sig=op.signature or f"{op.name}()"; suffix=f" {op.return_type}" if op.return_type else ""
            lines.append(f"        {op.visibility}{sig}{suffix}")
        lines.append("    }")
    arrows={RelationshipType.INHERITANCE:"<|--",RelationshipType.REALIZATION:"--|>",RelationshipType.COMPOSITION:"*--",RelationshipType.AGGREGATION:"o--",RelationshipType.ASSOCIATION:"-->",RelationshipType.DEPENDENCY:"..>",RelationshipType.LINK:"--"}
    for r in d.relationships:
        arrow=arrows.get(r.type,"-->"); lines.append(f"    {r.from_class} {arrow}|{_q(r.label)}| {r.to_class}" if r.label else f"    {r.from_class} {arrow} {r.to_class}")
    return "\n".join(lines)


def render_state(d: StateDiagram) -> str:
    lines=["stateDiagram-v2"]; sm={s.id:s for s in d.states}
    for s in d.states:
        if s.label != s.id: lines.append(f"    state \"{_q(s.label)}\" as {s.id}")
    for tr in d.transitions:
        src="[*]" if sm.get(tr.from_state) and sm[tr.from_state].is_initial else tr.from_state
        dst="[*]" if sm.get(tr.to_state) and sm[tr.to_state].is_final else tr.to_state
        bits=[]
        if tr.event: bits.append(tr.event)
        if tr.guard: bits.append(f"[{tr.guard}]")
        if tr.action: bits.append(f"/ {tr.action}")
        lines.append(f"    {src} --> {dst}" + (f" : {' '.join(bits)}" if bits else ""))
    return "\n".join(lines)


def render_er(d: ERDiagram) -> str:
    lines=["erDiagram"]
    cards={CardinityType.ONE_TO_ONE:"||--||",CardinityType.ONE_TO_MANY:"||--o{",CardinityType.MANY_TO_ONE:"}o--||",CardinityType.MANY_TO_MANY:"}o--o{",CardinityType.MANY_TO_MANY_MARKED:"}|--{|",CardinityType.ZERO_OR_ONE:"|o--o|",CardinityType.ONE:"||--||",CardinityType.ZERO_OR_MANY:"||--o{",CardinityType.MANY:"}o--o{"}
    for r in d.relationships: lines.append(f"    {r.from_entity} {cards.get(r.cardinality,'||--||')} {r.to_entity}" + (f" : {r.label}" if r.label else ""))
    for e in d.entities:
        lines.append(f"    {e.name} {{")
        for a in e.attributes: lines.append(f"        {a.type or 'string'} {a.name}" + (" PK" if a.is_key else ""))
        lines.append("    }")
    return "\n".join(lines)


def render_gantt(d: GanttChart) -> str:
    lines=["gantt"]
    if d.title: lines.append(f"    title {d.title}")
    lines.append("    dateFormat YYYY-MM-DD")
    for t in d.tasks:
        status="milestone" if t.milestone else str(t.status)
        parts=[status]
        if t.dependencies: parts.append("after "+" ".join(t.dependencies))
        parts.extend([t.start_date,t.end_date]); lines.append(f"    {t.title} :{t.id}, "+", ".join(parts))
    return "\n".join(lines)


def render_pie(d: PieChart) -> str:
    lines=[f"pie title {d.title}" if d.title else "pie"]
    lines.extend(f'    "{_q(s.label)}" : {s.value}' for s in d.slices)
    return "\n".join(lines)


def render_git(d: GitGraph) -> str:
    lines=["gitGraph"]; cm={c.id:c for c in d.commits}
    branches=d.branches or [GitBranch(name="main",commit_ids=[c.id for c in d.commits],is_main=True)]
    for b in branches:
        if not b.is_main and b.name!="main": lines.append(f"    branch {b.name}")
        for cid in b.commit_ids:
            if cid not in cm: continue
            c=cm[cid]; line=f'    commit id: "{_q(c.id)}" message: "{_q(c.message)}"'
            if c.tag: line += f' tag: "{_q(c.tag)}"'
            lines.append(line)
        if not b.is_main and b.name!="main": lines.append("    checkout main")
    return "\n".join(lines)


def render_c4(d: C4Diagram) -> str:
    lines=["C4Context"]
    if d.title: lines.append(f"    title {d.title}")
    funcs={C4Level.C1:"System",C4Level.C2:"Container",C4Level.C3:"Component",C4Level.C4:"System"}
    for e in d.elements:
        fn=funcs.get(e.level,"System"); args=[e.id,f'"{_q(e.name)}"']
        if e.technology: args.append(f'"{_q(e.technology)}"')
        if e.description: args.append(f'"{_q(e.description)}"')
        lines.append(f"    {fn}({', '.join(args)})")
    for r in d.relationships:
        args=[r.from_element,r.to_element,f'"{_q(r.description)}"']
        if r.technology: args.append(f'"{_q(r.technology)}"')
        lines.append(f"    Rel({', '.join(args)})")
    return "\n".join(lines)


def render_mindmap(d: Mindmap) -> str:
    lines=["mindmap"]
    if d.title: lines.append(f"    title {d.title}")
    def walk(n: MindmapNode,depth:int):
        lines.append("    "*(depth+1)+_q(n.label))
        for child in n.children: walk(child,depth+1)
    walk(d.root,0); return "\n".join(lines)


def render_sankey(d: SankeyDiagram) -> str:
    lines=["sankey-beta"]
    for x in d.flows: lines.append(f"    {x.source.replace(',','')},{x.target.replace(',','')},{x.value}")
    return "\n".join(lines)
