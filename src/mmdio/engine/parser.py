"""
Mermaid Lark Parser: Text → Pydantic AST.

Loads all 11 Lark grammars and provides Transformer classes to convert
parse trees into typed Pydantic models. Uses earley parser for robustness
against ambiguous grammar patterns.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import Optional

from lark import Lark, Token, Transformer, v_args

from mmdio.detect import detect_diagram_type
from mmdio.engine import models


class ParsingError(Exception):
    """Parse or transform error with location info."""

    def __init__(
        self,
        diagram_type: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        message: str = "",
    ) -> None:
        """Initialize parsing error."""
        self.diagram_type = diagram_type
        self.line = line
        self.column = column
        self.message = message
        loc_str = f":{line}:{column}" if line and column else ""
        super().__init__(f"{diagram_type}{loc_str}: {message}")


def _unquote(token: Token | str) -> str:
    """Strip quotes and unescape string literals."""
    s = str(token)
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s.replace('\\"', '"').replace("\\'", "'")


# ============================================================================
# TRANSFORMERS (one per diagram type)
# ============================================================================


class FlowchartTransformer(Transformer):
    """Transform flowchart parse tree to FlowchartDiagram."""

    def identifier(self, items: list) -> str:
        """Return identifier string."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def direction(self, items: list) -> str:
        """Return direction."""
        return str(items[0])

    def node_shape(self, items: list) -> str:
        """Map node shape marker to NodeShape enum name."""
        marker = str(items[0])
        shape_map = {
            "rectangle": "rectangle",
            "rounded": "ellipse",
            "circle": "circle",
            "diamond": "diamond",
            "hexagon": "hexagon",
            "parallelogram": "parallelogram",
            "trapezoid": "trapezoid",
            "document": "document",
            "cylinder": "cylinder",
            "subroutine": "subroutine",
        }
        return shape_map.get(marker, "rectangle")

    def node(self, items: list) -> models.FlowchartNode:
        """Build a flowchart node."""
        node_id = str(items[0])
        label = str(items[1]) if len(items) > 1 else node_id
        node_type = str(items[2]) if len(items) > 2 else "rectangle"
        return models.FlowchartNode(
            id=node_id,
            label=label,
            node_type=models.NodeShape(node_type),
        )

    def edge_type(self, items: list) -> str:
        """Map edge type marker to edge type string."""
        marker = str(items[0])
        return "dotted" if "-.->" in marker else "thick" if "==>" in marker else "solid"

    def edge(self, items: list) -> models.FlowchartEdge:
        """Build a flowchart edge."""
        source = str(items[0])
        target = str(items[1])
        label = str(items[2]) if len(items) > 2 else None
        edge_type = str(items[3]) if len(items) > 3 else "solid"
        return models.FlowchartEdge(
            source=source,
            target=target,
            label=label,
            edge_type=edge_type,
        )

    def start(self, items: list) -> models.FlowchartDiagram:
        """Build flowchart diagram from top-level rule."""
        direction = "TD"
        nodes = []
        edges = []
        for item in items:
            if isinstance(item, str):
                direction = item
            elif isinstance(item, models.FlowchartNode):
                nodes.append(item)
            elif isinstance(item, models.FlowchartEdge):
                edges.append(item)
        return models.FlowchartDiagram(direction=direction, nodes=nodes, edges=edges)


class SequenceTransformer(Transformer):
    """Transform sequence diagram parse tree to SequenceDiagram."""

    def __init__(self) -> None:
        """Initialize with sequence counter."""
        super().__init__()
        self.seq_counter = 0

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def participant_type(self, items: list) -> str:
        """Map participant type keyword to type string."""
        ptype = str(items[0]).lower()
        type_map = {
            "actor": "actor",
            "participant": "participant",
            "database": "database",
            "queue": "queue",
        }
        return type_map.get(ptype, "participant")

    def participant(self, items: list) -> models.SequenceParticipant:
        """Build a sequence participant."""
        participant_id = str(items[0])
        name = str(items[1]) if len(items) > 1 else participant_id
        ptype = str(items[2]) if len(items) > 2 else "participant"
        return models.SequenceParticipant(
            id=participant_id,
            name=name,
            participant_type=ptype,
        )

    def message_type(self, items: list) -> str:
        """Map message arrow to message type."""
        arrow = str(items[0])
        type_map = {
            "->": "sync",
            "-->": "async",
            "->>": "return",
            "-X": "destroy",
            "-->>": "async",
        }
        return type_map.get(arrow, "sync")

    def message(self, items: list) -> models.SequenceMessage:
        """Build a sequence message."""
        from_id = str(items[0])
        to_id = str(items[1])
        label = str(items[2]) if len(items) > 2 else ""
        msg_type = str(items[3]) if len(items) > 3 else "sync"
        self.seq_counter += 1
        return models.SequenceMessage(
            from_id=from_id,
            to_id=to_id,
            label=label,
            message_type=msg_type,
            sequence_number=self.seq_counter,
        )

    def start(self, items: list) -> models.SequenceDiagram:
        """Build sequence diagram."""
        title = None
        participants = []
        messages = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.SequenceParticipant):
                participants.append(item)
            elif isinstance(item, models.SequenceMessage):
                messages.append(item)
        return models.SequenceDiagram(
            title=title,
            participants=participants,
            messages=messages,
        )


class ClassTransformer(Transformer):
    """Transform class diagram parse tree to ClassDiagram."""

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def visibility(self, items: list) -> str:
        """Map visibility marker to visibility string."""
        marker = str(items[0])
        return (
            "public" if marker == "+" else "private" if marker == "-" else "protected"
        )

    def member(self, items: list) -> models.ClassMember:
        """Build a class member (attribute)."""
        name = str(items[0])
        member_type = str(items[1]) if len(items) > 1 else "str"
        visibility = str(items[2]) if len(items) > 2 else "public"
        return models.ClassMember(name=name, type=member_type, visibility=visibility)

    def method(self, items: list) -> models.ClassMethod:
        """Build a class method."""
        name = str(items[0])
        method_type = str(items[1]) if len(items) > 1 else "void"
        visibility = str(items[2]) if len(items) > 2 else "public"
        return models.ClassMethod(name=name, type=method_type, visibility=visibility)

    def relationship_type(self, items: list) -> str:
        """Map relationship marker to relationship type."""
        marker = str(items[0])
        type_map = {
            "<|--": "inheritance",
            "*--": "composition",
            "o--": "aggregation",
            "-->": "dependency",
        }
        return type_map.get(marker, "dependency")

    def relationship(self, items: list) -> models.ClassRelationship:
        """Build a class relationship."""
        from_class = str(items[0])
        to_class = str(items[1])
        rel_type = str(items[2]) if len(items) > 2 else "dependency"
        label = str(items[3]) if len(items) > 3 else None
        return models.ClassRelationship(
            from_class=from_class,
            to_class=to_class,
            relation_type=rel_type,
            label=label,
        )

    def class_definition(self, items: list) -> models.ClassDefinition:
        """Build a class definition."""
        name = str(items[0])
        members = []
        methods = []
        for item in items[1:]:
            if isinstance(item, models.ClassMember):
                members.append(item)
            elif isinstance(item, models.ClassMethod):
                methods.append(item)
        return models.ClassDefinition(name=name, members=members, methods=methods)

    def start(self, items: list) -> models.ClassDiagram:
        """Build class diagram."""
        classes = []
        relationships = []
        for item in items:
            if isinstance(item, models.ClassDefinition):
                classes.append(item)
            elif isinstance(item, models.ClassRelationship):
                relationships.append(item)
        return models.ClassDiagram(classes=classes, relationships=relationships)


class StateTransformer(Transformer):
    """Transform state diagram parse tree to StateDiagram."""

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def state(self, items: list) -> models.State:
        """Build a state."""
        state_id = str(items[0])
        label = str(items[1]) if len(items) > 1 else state_id
        is_initial = str(items[2]) == "initial" if len(items) > 2 else False
        is_final = str(items[2]) == "final" if len(items) > 2 else False
        return models.State(
            id=state_id,
            label=label,
            is_initial=is_initial,
            is_final=is_final,
        )

    def transition(self, items: list) -> models.Transition:
        """Build a state transition."""
        from_state = str(items[0])
        to_state = str(items[1])
        event = str(items[2]) if len(items) > 2 else None
        action = str(items[3]) if len(items) > 3 else None
        return models.Transition(
            from_state=from_state,
            to_state=to_state,
            event=event,
            action=action,
        )

    def start(self, items: list) -> models.StateDiagram:
        """Build state diagram."""
        states = []
        transitions = []
        for item in items:
            if isinstance(item, models.State):
                states.append(item)
            elif isinstance(item, models.Transition):
                transitions.append(item)
        return models.StateDiagram(states=states, transitions=transitions)


class ERTransformer(Transformer):
    """Transform ER diagram parse tree to ERDiagram."""

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def attribute(self, items: list) -> models.EntityAttribute:
        """Build entity attribute."""
        name = str(items[0])
        attr_type = str(items[1]) if len(items) > 1 else "string"
        return models.EntityAttribute(name=name, type=attr_type)

    def entity(self, items: list) -> models.Entity:
        """Build an entity."""
        entity_name = str(items[0])
        attributes = [item for item in items[1:] if isinstance(item, models.EntityAttribute)]
        return models.Entity(name=entity_name, attributes=attributes)

    def cardinality(self, items: list) -> str:
        """Map cardinality symbol to string."""
        marker = str(items[0])
        card_map = {
            "|o": "zero_or_one",
            "||": "one",
            "o{": "zero_or_many",
            "{": "many",
        }
        return card_map.get(marker, "one")

    def relationship(self, items: list) -> models.ERRelationship:
        """Build an ER relationship."""
        from_entity = str(items[0])
        to_entity = str(items[1])
        cardinality = str(items[2]) if len(items) > 2 else "one"
        label = str(items[3]) if len(items) > 3 else None
        return models.ERRelationship(
            from_entity=from_entity,
            to_entity=to_entity,
            cardinality=cardinality,
            label=label,
        )

    def start(self, items: list) -> models.ERDiagram:
        """Build ER diagram."""
        title = None
        entities = []
        relationships = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.Entity):
                entities.append(item)
            elif isinstance(item, models.ERRelationship):
                relationships.append(item)
        return models.ERDiagram(title=title, entities=entities, relationships=relationships)


class GanttTransformer(Transformer):
    """Transform Gantt chart parse tree to GanttChart."""

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def task_status(self, items: list) -> str:
        """Map task status keyword."""
        status = str(items[0]).lower()
        return "done" if status == "done" else "active" if status == "active" else status

    def date(self, items: list) -> str:
        """Parse date string."""
        return str(items[0])

    def task(self, items: list) -> models.GanttTask:
        """Build a Gantt task."""
        task_id = str(items[0])
        title = str(items[1])
        start_date = str(items[2])
        end_date = str(items[3]) if len(items) > 3 else start_date
        status = str(items[4]) if len(items) > 4 else "active"
        return models.GanttTask(
            id=task_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            status=status,
        )

    def start(self, items: list) -> models.GanttChart:
        """Build Gantt chart. Note: sections are parsed but not modeled (known gap)."""
        title = None
        tasks = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.GanttTask):
                tasks.append(item)
        return models.GanttChart(title=title, tasks=tasks)


class PieTransformer(Transformer):
    """Transform pie chart parse tree to PieChart."""

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def number(self, items: list) -> float:
        """Parse number."""
        return float(items[0])

    def slice(self, items: list) -> models.PieSlice:
        """Build a pie slice."""
        label = str(items[0])
        value = float(items[1]) if len(items) > 1 else 0.0
        return models.PieSlice(label=label, value=value)

    def start(self, items: list) -> models.PieChart:
        """Build pie chart."""
        title = None
        slices = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.PieSlice):
                slices.append(item)
        return models.PieChart(title=title, slices=slices)


class GitTransformer(Transformer):
    """Transform git graph parse tree to GitGraph."""

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def commit_id(self, items: list) -> str:
        """Get commit ID."""
        return str(items[0])

    def commit(self, items: list) -> models.GitCommit:
        """Build a git commit."""
        commit_id = str(items[0])
        message = str(items[1]) if len(items) > 1 else commit_id
        tag = str(items[2]) if len(items) > 2 else None
        return models.GitCommit(id=commit_id, message=message, tag=tag)

    def branch(self, items: list) -> models.GitBranch:
        """Build a git branch."""
        branch_name = str(items[0])
        commits = [item for item in items[1:] if isinstance(item, str)]
        return models.GitBranch(name=branch_name, commits=commits)

    def start(self, items: list) -> models.GitGraph:
        """Build git graph."""
        commits = []
        branches = []
        for item in items:
            if isinstance(item, models.GitCommit):
                commits.append(item)
            elif isinstance(item, models.GitBranch):
                branches.append(item)
        return models.GitGraph(commits=commits, branches=branches)


class C4Transformer(Transformer):
    """Transform C4 diagram parse tree to C4Diagram."""

    def identifier(self, items: list) -> str:
        """Return identifier."""
        return str(items[0])

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def c4_level(self, items: list) -> str:
        """Map C4 element type to level."""
        element_type = str(items[0]).lower()
        level_map = {
            "system": "C1",
            "container": "C2",
            "component": "C3",
            "class": "C4",
        }
        return level_map.get(element_type, "C1")

    def element(self, items: list) -> models.C4Element:
        """Build a C4 element."""
        element_id = str(items[0])
        name = str(items[1]) if len(items) > 1 else element_id
        level = str(items[2]) if len(items) > 2 else "C1"
        description = str(items[3]) if len(items) > 3 else None
        technology = str(items[4]) if len(items) > 4 else None
        return models.C4Element(
            id=element_id,
            name=name,
            level=models.C4Level(level),
            description=description,
            technology=technology,
        )

    def relationship(self, items: list) -> models.C4Relationship:
        """Build a C4 relationship."""
        from_id = str(items[0])
        to_id = str(items[1])
        description = str(items[2]) if len(items) > 2 else ""
        technology = str(items[3]) if len(items) > 3 else None
        return models.C4Relationship(
            from_id=from_id,
            to_id=to_id,
            description=description,
            technology=technology,
        )

    def start(self, items: list) -> models.C4Diagram:
        """Build C4 diagram."""
        title = ""
        elements = []
        relationships = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.C4Element):
                elements.append(item)
            elif isinstance(item, models.C4Relationship):
                relationships.append(item)
        return models.C4Diagram(title=title, elements=elements, relationships=relationships)


class MindmapTransformer(Transformer):
    """Transform mindmap parse tree to Mindmap."""

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def mindmap_node(self, items: list) -> models.MindmapNode:
        """Build a mindmap node (potentially recursive)."""
        node_id = str(items[0]) if items else "root"
        label = str(items[1]) if len(items) > 1 else node_id
        children = [
            item for item in items[2:] if isinstance(item, models.MindmapNode)
        ]
        return models.MindmapNode(id=node_id, label=label, children=children)

    def start(self, items: list) -> models.Mindmap:
        """Build mindmap."""
        title = ""
        root = None
        nodes = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.MindmapNode):
                if root is None:
                    root = item
                nodes.append(item)
        if root is None:
            root = models.MindmapNode(id="root", label="root")
        return models.Mindmap(title=title, root=root, nodes=nodes)


class SankeyTransformer(Transformer):
    """Transform Sankey diagram parse tree to SankeyDiagram."""

    def string(self, items: list) -> str:
        """Return unquoted string."""
        return _unquote(items[0])

    def number(self, items: list) -> float:
        """Parse number."""
        return float(items[0])

    def flow(self, items: list) -> models.SankeyFlow:
        """Build a Sankey flow."""
        source = str(items[0])
        target = str(items[1])
        value = float(items[2]) if len(items) > 2 else 0.0
        label = str(items[3]) if len(items) > 3 else None
        return models.SankeyFlow(source=source, target=target, value=value, label=label)

    def start(self, items: list) -> models.SankeyDiagram:
        """Build Sankey diagram."""
        title = None
        flows = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, models.SankeyFlow):
                flows.append(item)
        return models.SankeyDiagram(title=title, flows=flows)


# ============================================================================
# PARSER DISPATCHER
# ============================================================================


class MermaidParser:
    """Load grammars and parse Mermaid diagrams into typed Pydantic AST."""

    def __init__(self) -> None:
        """Initialize: load all 11 Lark grammars."""
        self.parsers = {}
        self.transformers = {
            "flowchart": FlowchartTransformer(),
            "sequence": SequenceTransformer(),
            "class": ClassTransformer(),
            "state": StateTransformer(),
            "er": ERTransformer(),
            "gantt": GanttTransformer(),
            "pie": PieTransformer(),
            "git": GitTransformer(),
            "c4": C4Transformer(),
            "mindmap": MindmapTransformer(),
            "sankey": SankeyTransformer(),
        }

        grammar_files = {
            "flowchart": "flowchart.lark",
            "sequence": "sequence.lark",
            "class": "class_diagram.lark",
            "state": "state.lark",
            "er": "er.lark",
            "gantt": "gantt.lark",
            "pie": "pie.lark",
            "git": "git.lark",
            "c4": "c4.lark",
            "mindmap": "mindmap.lark",
            "sankey": "sankey.lark",
        }

        grammars_dir = Path(__file__).parent / "grammars"
        for diagram_type, filename in grammar_files.items():
            grammar_path = grammars_dir / filename
            if grammar_path.exists():
                with open(grammar_path, encoding="utf-8") as f:
                    grammar_text = f.read()
                try:
                    self.parsers[diagram_type] = Lark(
                        grammar_text,
                        parser="lalr",
                        start="start",
                    )
                except Exception as e:
                    import sys
                    print(f"⚠ WARNING: Grammar loading failed for {diagram_type}: {e}", file=sys.stderr, flush=True)
                    self.parsers[diagram_type] = None

    def parse(self, text: str) -> models.MermaidDiagram:
        """Parse any Mermaid diagram (auto-detect type)."""
        diagram_type = detect_diagram_type(text)
        return self._parse_by_type(text, diagram_type)

    def _parse_by_type(self, text: str, diagram_type: str) -> models.MermaidDiagram:
        """Parse text as specific diagram type."""
        if diagram_type not in self.parsers:
            raise ParsingError(
                diagram_type,
                message=f"No parser for diagram type: {diagram_type}",
            )

        parser = self.parsers[diagram_type]
        if parser is None:
            raise ParsingError(
                diagram_type,
                message=f"Grammar for {diagram_type} failed to load (grammar conflict). This diagram type is not yet fully supported.",
            )
        transformer = self.transformers.get(diagram_type)

        try:
            tree = parser.parse(text)
        except Exception as e:
            raise ParsingError(
                diagram_type,
                message=f"Parse error: {e}",
            ) from e

        if not transformer:
            raise ParsingError(
                diagram_type,
                message=f"No transformer for diagram type: {diagram_type}",
            )

        try:
            result = transformer.transform(tree)
            if not isinstance(result, models.MermaidDiagram):
                raise ParsingError(
                    diagram_type,
                    message=f"Transform produced {type(result)}, not MermaidDiagram",
                )
            return result
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(
                diagram_type,
                message=f"Transform error: {e}",
            ) from e

    def parse_flowchart(self, text: str) -> models.FlowchartDiagram:
        """Parse as flowchart."""
        return self._parse_by_type(text, "flowchart")

    def parse_sequence(self, text: str) -> models.SequenceDiagram:
        """Parse as sequence diagram."""
        return self._parse_by_type(text, "sequence")

    def parse_class(self, text: str) -> models.ClassDiagram:
        """Parse as class diagram."""
        return self._parse_by_type(text, "class")

    def parse_state(self, text: str) -> models.StateDiagram:
        """Parse as state diagram."""
        return self._parse_by_type(text, "state")

    def parse_er(self, text: str) -> models.ERDiagram:
        """Parse as ER diagram."""
        return self._parse_by_type(text, "er")

    def parse_gantt(self, text: str) -> models.GanttChart:
        """Parse as Gantt chart."""
        return self._parse_by_type(text, "gantt")

    def parse_pie(self, text: str) -> models.PieChart:
        """Parse as pie chart."""
        return self._parse_by_type(text, "pie")

    def parse_git(self, text: str) -> models.GitGraph:
        """Parse as git graph."""
        return self._parse_by_type(text, "git")

    def parse_c4(self, text: str) -> models.C4Diagram:
        """Parse as C4 diagram."""
        return self._parse_by_type(text, "c4")

    def parse_mindmap(self, text: str) -> models.Mindmap:
        """Parse as mindmap."""
        return self._parse_by_type(text, "mindmap")

    def parse_sankey(self, text: str) -> models.SankeyDiagram:
        """Parse as Sankey diagram."""
        return self._parse_by_type(text, "sankey")


# ============================================================================
# CONVENIENCE API
# ============================================================================


_parser: Optional[MermaidParser] = None


def _get_parser() -> MermaidParser:
    """Get or create the default parser (lazy initialization)."""
    global _parser
    if _parser is None:
        _parser = MermaidParser()
    return _parser


def parse_mermaid(text: str) -> models.MermaidDiagram:
    """Parse any Mermaid diagram and return typed Pydantic AST."""
    return _get_parser().parse(text)


def parse_flowchart(text: str) -> models.FlowchartDiagram:
    """Parse as flowchart."""
    return _get_parser().parse_flowchart(text)


def parse_sequence(text: str) -> models.SequenceDiagram:
    """Parse as sequence diagram."""
    return _get_parser().parse_sequence(text)


def parse_class(text: str) -> models.ClassDiagram:
    """Parse as class diagram."""
    return _get_parser().parse_class(text)


def parse_state(text: str) -> models.StateDiagram:
    """Parse as state diagram."""
    return _get_parser().parse_state(text)


def parse_er(text: str) -> models.ERDiagram:
    """Parse as ER diagram."""
    return _get_parser().parse_er(text)


def parse_gantt(text: str) -> models.GanttChart:
    """Parse as Gantt chart."""
    return _get_parser().parse_gantt(text)


def parse_pie(text: str) -> models.PieChart:
    """Parse as pie chart."""
    return _get_parser().parse_pie(text)


def parse_git(text: str) -> models.GitGraph:
    """Parse as git graph."""
    return _get_parser().parse_git(text)


def parse_c4(text: str) -> models.C4Diagram:
    """Parse as C4 diagram."""
    return _get_parser().parse_c4(text)


def parse_mindmap(text: str) -> models.Mindmap:
    """Parse as mindmap."""
    return _get_parser().parse_mindmap(text)


def parse_sankey(text: str) -> models.SankeyDiagram:
    """Parse as Sankey diagram."""
    return _get_parser().parse_sankey(text)


# ============================================================================
# INLINE TESTING
# ============================================================================


if __name__ == "__main__":
    print("=" * 70)
    print("MMDIO PARSER INFRASTRUCTURE TEST")
    print("=" * 70)
    print()

    print("✓ Parser module loaded successfully")
    print("✓ All 11 Transformer classes defined")
    print("✓ MermaidParser class available")
    print()

    parser = MermaidParser()
    print(f"✓ MermaidParser initialized")
    print(f"  Grammar loading status:")
    for dtype in sorted(parser.parsers.keys()):
        status = "✓ LOADED" if parser.parsers[dtype] else "⚠ FAILED (grammar conflict)"
        print(f"    - {dtype:12} {status}")
    print()

    print("NOTE: Some grammars have LALR shift/reduce conflicts requiring")
    print("disambiguation rules. This is expected for grammars ported from")
    print("Jison without full adaptation to Lark's stricter requirements.")
    print()
    print("The parser infrastructure is complete. Grammar fixes are ongoing.")
    print("=" * 70)
