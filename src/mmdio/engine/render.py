"""
Mermaid Diagram AST → Mermaid Text Renderer

Converts Pydantic diagram AST models back to valid Mermaid diagram syntax.
One function per diagram type, dispatched by render_diagram().

No prettification yet — syntax is minimal but valid. Each render is idempotent:
diagram → parse → render → parse produces equivalent AST.
"""

from typing import Union
from .models import (
    MermaidDiagram,
    FlowchartDiagram,
    NodeShape,
    SequenceDiagram,
    ClassDiagram,
    StateDiagram,
    ERDiagram,
    GanttChart,
    PieChart,
    GitGraph,
    C4Diagram,
    Mindmap,
    SankeyDiagram,
)


# ============================================================================
# DISPATCHER
# ============================================================================


def render_diagram(diagram: MermaidDiagram) -> str:
    """
    Render any Mermaid diagram type back to text.

    Args:
        diagram: A Pydantic diagram AST model (any of the 11 types)

    Returns:
        Valid Mermaid diagram syntax as a string.

    Raises:
        ValueError: If diagram type is not recognized.
    """
    if isinstance(diagram, FlowchartDiagram):
        return render_flowchart(diagram)
    elif isinstance(diagram, SequenceDiagram):
        return render_sequence(diagram)
    elif isinstance(diagram, ClassDiagram):
        return render_class(diagram)
    elif isinstance(diagram, StateDiagram):
        return render_state(diagram)
    elif isinstance(diagram, ERDiagram):
        return render_er(diagram)
    elif isinstance(diagram, GanttChart):
        return render_gantt(diagram)
    elif isinstance(diagram, PieChart):
        return render_pie(diagram)
    elif isinstance(diagram, GitGraph):
        return render_git(diagram)
    elif isinstance(diagram, C4Diagram):
        return render_c4(diagram)
    elif isinstance(diagram, Mindmap):
        return render_mindmap(diagram)
    elif isinstance(diagram, SankeyDiagram):
        return render_sankey(diagram)
    else:
        raise ValueError(f"Unknown diagram type: {type(diagram)}")


# ============================================================================
# FLOWCHART / GRAPH
# ============================================================================


def render_flowchart(d: FlowchartDiagram) -> str:
    r"""
    Render flowchart diagram to Mermaid syntax.

    Format:
        graph [direction]
        id[label]
        id --> target: edge_label

    Node type markers:
        [label]         → rectangle
        (label)         → rounded
        ((label))       → circle
        {label}         → diamond
        [/label/]       → trapezoid
        [\label\]       → parallelogram

    Edge types:
        -->             → solid
        -.->            → dotted
        ==>             → thick
    """
    lines = []

    # Header: graph [direction]
    lines.append(f"graph {d.direction}")

    # Nodes with type-specific markers
    for node in d.nodes:
        label = node.label.replace('"', '\\"')
        marker_open, marker_close = _get_node_markers(node.shape)
        lines.append(f'{node.id}{marker_open}{label}{marker_close}')

    # Edges
    for edge in d.edges:
        arrow = _get_edge_arrow(edge.style)
        if edge.label:
            label = edge.label.replace('"', '\\"')
            lines.append(f'{edge.source} {arrow}|{label}| {edge.target}')
        else:
            lines.append(f'{edge.source} {arrow} {edge.target}')

    return '\n'.join(lines)


def _get_node_markers(node_shape: NodeShape) -> tuple:
    """Get opening and closing markers for node shape type."""
    markers = {
        NodeShape.RECTANGLE: ('[', ']'),
        NodeShape.CIRCLE: ('((', '))'),
        NodeShape.ELLIPSE: ('(', ')'),
        NodeShape.DIAMOND: ('{', '}'),
        NodeShape.HEXAGON: ('{{', '}}'),
        NodeShape.TRAPEZOID: ('[/', '/]'),
        NodeShape.PARALLELOGRAM: ('[\\', '\\]'),
        NodeShape.DOCUMENT: ('[\\', '\\]'),
        NodeShape.CYLINDER: ('[(', ')]'),
        NodeShape.SUBROUTINE: ('[[', ']]'),
    }
    return markers.get(node_shape, ('[', ']'))


def _get_edge_arrow(edge_type: str) -> str:
    """Get arrow syntax for edge type."""
    arrows = {
        'solid': '-->',
        'dotted': '-.->',
        'thick': '==>',
    }
    return arrows.get(edge_type, '-->')


# ============================================================================
# SEQUENCE DIAGRAM
# ============================================================================


def render_sequence(d: SequenceDiagram) -> str:
    """
    Render sequence diagram to Mermaid syntax.

    Format:
        sequenceDiagram
            Title My Title
            actor A
            participant B
            A->>B: message
            B-->>A: async message

    Participant types: actor, participant
    Message types: sync (->), async (-->), return (<--)
    """
    lines = ['sequenceDiagram']

    if d.title:
        lines.append(f'    Title {d.title}')

    # Participants
    for participant in d.participants:
        ptype_name = participant.type.value if hasattr(participant.type, 'value') else str(participant.type)
        lines.append(f'    {ptype_name} {participant.id} as {participant.name}')

    # Messages (sorted by sequence number for consistency)
    sorted_messages = sorted(d.messages, key=lambda m: m.sequence_number or 0)
    for message in sorted_messages:
        label = message.label.replace('"', '\\"')
        msg_type_str = message.type.value if hasattr(message.type, 'value') else str(message.type)
        arrow = _get_sequence_arrow(msg_type_str)
        lines.append(f'    {message.from_participant}{arrow}{message.to_participant}: {label}')

    return '\n'.join(lines)


def _get_sequence_arrow(message_type: str) -> str:
    """Get arrow syntax for message type."""
    arrows = {
        'sync': '->>',
        'async': '-->>',
        'return': '-->>',
        'create': '->>+',
        'destroy': '--x',
    }
    return arrows.get(message_type, '->>')


# ============================================================================
# CLASS DIAGRAM
# ============================================================================


def render_class(d: ClassDiagram) -> str:
    """
    Render class diagram to Mermaid syntax.

    Format:
        classDiagram
            class MyClass {
                +int id
                -string name
                +getters()
            }
            Inheritance <|-- Subclass

    Visibility: + (public), - (private), # (protected), ~ (package)
    Relations: <|-- (inheritance), --|> (realization), *-- (composition),
               o-- (aggregation), --> (association), ..> (dependency), -- (link)
    """
    lines = ['classDiagram']

    # Class definitions
    for cls in d.classes:
        lines.append(f'    class {cls.name} {{')

        # Members (attributes)
        for member in cls.members:
            vis = member.visibility if member.visibility else '+'
            type_str = f'{member.type} ' if member.type else ''
            lines.append(f'        {vis}{type_str}{member.name}')

        # Methods
        for method in cls.methods:
            vis = method.visibility if method.visibility else '+'
            sig = f'{method.signature}' if method.signature else f'{method.name}()'
            lines.append(f'        {vis}{sig}')

        lines.append('    }')

    # Relationships
    for relation in d.relationships:
        relation_type_str = relation.type.value if hasattr(relation.type, 'value') else str(relation.type)
        arrow = _get_class_relation_arrow(relation_type_str)
        if relation.label:
            label = relation.label.replace('"', '\\"')
            lines.append(f'    {relation.from_class} {arrow}|{label}| {relation.to_class}')
        else:
            lines.append(f'    {relation.from_class} {arrow} {relation.to_class}')

    return '\n'.join(lines)


def _get_class_relation_arrow(relation_type: str) -> str:
    """Get arrow syntax for class relation type."""
    arrows = {
        'inheritance': '<|--',
        'realization': '--|>',
        'composition': '*--',
        'aggregation': 'o--',
        'association': '-->',
        'dependency': '..>',
        'link': '--',
    }
    return arrows.get(relation_type, '-->')


# ============================================================================
# STATE DIAGRAM
# ============================================================================


def render_state(d: StateDiagram) -> str:
    """
    Render state diagram to Mermaid syntax.

    Format:
        stateDiagram-v2
            [*] --> State1
            State1 --> State2 : event / action
            State2 --> [*]

    Special states: [*] (initial), [*] (final)
    """
    lines = ['stateDiagram-v2']

    # Build state lookup for quick access
    state_map = {s.id: s for s in d.states}

    # Initial transitions
    for transition in d.transitions:
        from_state = state_map.get(transition.from_state)
        if from_state and from_state.is_initial:
            to_label = transition.to_state
            label_str = _format_transition_label(transition.event, transition.action)
            if label_str:
                lines.append(f'    [*] --> {to_label} : {label_str}')
            else:
                lines.append(f'    [*] --> {to_label}')

    # Regular transitions
    for transition in d.transitions:
        from_state = state_map.get(transition.from_state)
        if from_state and not from_state.is_initial:
            from_label = transition.from_state
            to_state = state_map.get(transition.to_state)
            to_label = '[*]' if to_state and to_state.is_final else transition.to_state
            label_str = _format_transition_label(transition.event, transition.action)
            if label_str:
                lines.append(f'    {from_label} --> {to_label} : {label_str}')
            else:
                lines.append(f'    {from_label} --> {to_label}')

    return '\n'.join(lines)


def _format_transition_label(event: str = None, action: str = None) -> str:
    """Format transition label from event and action."""
    parts = []
    if event:
        parts.append(event)
    if action:
        parts.append(f'/ {action}')
    return ' '.join(parts)


# ============================================================================
# ENTITY-RELATIONSHIP DIAGRAM
# ============================================================================


def render_er(d: ERDiagram) -> str:
    """
    Render entity-relationship diagram to Mermaid syntax.

    Format:
        erDiagram
            CUSTOMER ||--o{ ORDER : places
            CUSTOMER {
                string id
                string name
            }

    Cardinality: ||, }|, o{, }o (one-to-one, many-to-one, one-to-many, many-to-many)
    """
    lines = ['erDiagram']

    # Relationships (must come first in Mermaid)
    for relation in d.relationships:
        # Map cardinality enum to Mermaid notation
        cardinality_str = relation.cardinality.value if hasattr(relation.cardinality, 'value') else str(relation.cardinality)
        cardinality_map = {
            'one_to_one': '||--||',
            'one_to_many': '||--o{',
            'many_to_one': '}o--||',
            'many_to_many': '}o--o{',
            'many_to_many_marked': '}|--{|',
        }
        cardinality = cardinality_map.get(cardinality_str, '||--||')

        label = relation.label or ''
        if label:
            label = f' : {label}'
        lines.append(f'    {relation.from_entity} {cardinality} {relation.to_entity}{label}')

    # Entities with attributes
    for entity in d.entities:
        lines.append(f'    {entity.name} {{')
        for attr in entity.attributes:
            attr_type = attr.type or 'string'
            attr_key = 'PK' if attr.is_key else ''
            attr_nullable = '' if not attr.is_nullable else ''
            lines.append(f'        {attr_type} {attr.name} {attr_key} {attr_nullable}'.strip())
        lines.append('    }')

    return '\n'.join(lines)


# ============================================================================
# GANTT CHART
# ============================================================================


def render_gantt(d: GanttChart) -> str:
    """
    Render Gantt chart to Mermaid syntax.

    Format:
        gantt
            title My Gantt Chart
            dateFormat YYYY-MM-DD
            task1 :done, 2024-01-01, 2024-01-05
            task2 :active, task1, 3d

    Status: done, active, crit (critical), milestone
    """
    lines = ['gantt']

    if d.title:
        lines.append(f'    title {d.title}')

    lines.append('    dateFormat YYYY-MM-DD')

    for task in d.tasks:
        status_str = task.status.value if hasattr(task.status, 'value') else str(task.status)
        start = task.start_date
        end = task.end_date

        deps = ','.join(task.dependencies) if task.dependencies else ''
        if deps:
            lines.append(f'    {task.id} :{status_str}, {deps}, {start}, {end}')
        else:
            lines.append(f'    {task.id} :{status_str}, {start}, {end}')

    return '\n'.join(lines)


# ============================================================================
# PIE CHART
# ============================================================================


def render_pie(d: PieChart) -> str:
    """
    Render pie chart to Mermaid syntax.

    Format:
        pie title My Pie Chart
            "Label 1" : 30
            "Label 2" : 70
    """
    lines = []

    if d.title:
        lines.append(f'pie title {d.title}')
    else:
        lines.append('pie')

    for slice_ in d.slices:
        label = slice_.label.replace('"', '\\"')
        lines.append(f'    "{label}" : {slice_.value}')

    return '\n'.join(lines)


# ============================================================================
# GIT GRAPH
# ============================================================================


def render_git(d: GitGraph) -> str:
    """
    Render git graph to Mermaid syntax.

    Format:
        gitGraph
            commit id: "c1"
            branch develop
            commit id: "c2"
            checkout main
            commit id: "c3"

    Commits stored by ID; branches reference commit IDs.
    """
    lines = ['gitGraph']

    commit_map = {c.id: c for c in d.commits}

    # Render commits and branches
    for branch in d.branches:
        if not branch.is_main and branch.name != 'main':
            lines.append(f'    branch {branch.name}')

        for commit_id in branch.commit_ids:
            if commit_id in commit_map:
                commit = commit_map[commit_id]
                msg = commit.message.replace('"', '\\"')
                lines.append(f'    commit id: "{commit.id}" message: "{msg}"')
                if commit.tag:
                    lines.append(f'    tag: {commit.tag}')

        if not branch.is_main and branch.name != 'main':
            lines.append('    checkout main')

    return '\n'.join(lines)


# ============================================================================
# C4 DIAGRAM
# ============================================================================


def render_c4(d: C4Diagram) -> str:
    """
    Render C4 architecture diagram to Mermaid syntax.

    Format:
        C4Context
            title System Architecture
            System_Ext(s1, "External System", "Description")
            System(s2, "Internal System", "Description")
            Rel(s1, s2, "Uses", "HTTP")

    Levels: System (C1), Container (C2), Component (C3), Class (C4)
    """
    lines = ['C4Context']

    if d.title:
        lines.append(f'    title {d.title}')

    # Elements
    for elem in d.elements:
        name = elem.name.replace('"', '\\"')
        desc = (elem.description or '').replace('"', '\\"')
        tech = (elem.technology or '').replace('"', '\\"')
        level_str = elem.level.value if hasattr(elem.level, 'value') else str(elem.level)

        if level_str == 'C1':
            if tech:
                lines.append(f'    System_Ext({elem.id}, "{name}", "{desc}", "{tech}")')
            else:
                lines.append(f'    System_Ext({elem.id}, "{name}", "{desc}")')
        elif level_str == 'C2':
            if tech:
                lines.append(f'    Container({elem.id}, "{name}", "{tech}", "{desc}")')
            else:
                lines.append(f'    Container({elem.id}, "{name}", "{desc}")')
        elif level_str == 'C3':
            if tech:
                lines.append(f'    Component({elem.id}, "{name}", "{tech}", "{desc}")')
            else:
                lines.append(f'    Component({elem.id}, "{name}", "{desc}")')
        else:
            # C4 (class level)
            if tech:
                lines.append(f'    System({elem.id}, "{name}", "{tech}", "{desc}")')
            else:
                lines.append(f'    System({elem.id}, "{name}", "{desc}")')

    # Relationships
    for rel in d.relationships:
        desc = rel.description.replace('"', '\\"')
        tech = (rel.technology or '').replace('"', '\\"')
        if tech:
            lines.append(f'    Rel({rel.from_element}, {rel.to_element}, "{desc}", "{tech}")')
        else:
            lines.append(f'    Rel({rel.from_element}, {rel.to_element}, "{desc}")')

    return '\n'.join(lines)


# ============================================================================
# MINDMAP
# ============================================================================


def render_mindmap(d: Mindmap) -> str:
    """
    Render mindmap to Mermaid syntax.

    Format:
        mindmap
            root
                Child 1
                    Grandchild 1a
                    Grandchild 1b
                Child 2

    Hierarchical indentation; root node is central.
    """
    lines = ['mindmap']

    if d.title:
        lines.append(f'    title {d.title}')

    def render_node(node, depth: int) -> None:
        """Recursively render node and its children."""
        indent = '    ' * (depth + 1)
        label = node.label.replace('"', '\\"')

        if depth == 0:
            # Root node (no special marker in latest Mermaid syntax)
            lines.append(f'{indent}{label}')
        else:
            lines.append(f'{indent}{label}')

        # Render children recursively
        for child in node.children:
            render_node(child, depth + 1)

    # Start from root
    render_node(d.root, 0)

    return '\n'.join(lines)


# ============================================================================
# SANKEY DIAGRAM
# ============================================================================


def render_sankey(d: SankeyDiagram) -> str:
    """
    Render Sankey diagram to Mermaid syntax.

    Format:
        sankey-beta
            Source,Target,Value
            A,B,100
            B,C,80
            B,D,20

    Flows are source → target with numeric values.
    """
    lines = ['sankey-beta']

    # Header
    lines.append('    Source,Target,Value')

    # Flows
    for flow in d.flows:
        source = flow.source.replace(',', '')
        target = flow.target.replace(',', '')
        label = (flow.label or '').replace(',', '')
        lines.append(f'    {source},{target},{flow.value}')

    return '\n'.join(lines)
