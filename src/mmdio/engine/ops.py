"""
Mermaid diagram algebra: merge, diff, and topology validation.

Operations on typed Pydantic AST models. All operations work on same-type only
(merging a flowchart into a flowchart, etc.). Cross-type composition is a
future stretch goal.
"""

from __future__ import annotations

from typing import TypeVar

from mmdio.engine import models


T = TypeVar("T", bound=models.MermaidDiagram)


def merge(
    diagram1: models.FlowchartDiagram | models.SequenceDiagram,
    diagram2: models.FlowchartDiagram | models.SequenceDiagram,
) -> models.FlowchartDiagram | models.SequenceDiagram:
    """
    Merge two diagrams of the same type.

    For flowchart: union of nodes and edges (by id/source-target, no duplicates).
    For sequence: append messages (preserving/renumbering sequence numbers).
    Other types: raise NotImplementedError.
    """
    if type(diagram1) != type(diagram2):
        raise ValueError(
            f"Cannot merge {type(diagram1).__name__} with {type(diagram2).__name__}"
        )

    if isinstance(diagram1, models.FlowchartDiagram):
        assert isinstance(diagram2, models.FlowchartDiagram)
        merged_nodes = {n.id: n for n in diagram1.nodes}
        for n in diagram2.nodes:
            merged_nodes[n.id] = n
        merged_edges = {(e.source, e.target): e for e in diagram1.edges}
        for e in diagram2.edges:
            merged_edges[(e.source, e.target)] = e
        return models.FlowchartDiagram(
            direction=diagram1.direction,
            nodes=list(merged_nodes.values()),
            edges=list(merged_edges.values()),
        )

    if isinstance(diagram1, models.SequenceDiagram):
        assert isinstance(diagram2, models.SequenceDiagram)
        merged_participants = {p.id: p for p in diagram1.participants}
        for p in diagram2.participants:
            merged_participants[p.id] = p
        merged_messages = diagram1.messages + diagram2.messages
        for i, msg in enumerate(merged_messages, start=1):
            msg.sequence_number = i
        return models.SequenceDiagram(
            title=diagram1.title or diagram2.title,
            participants=list(merged_participants.values()),
            messages=merged_messages,
        )

    raise NotImplementedError(
        f"Merge not implemented for {type(diagram1).__name__}"
    )


def diff(
    diagram1: models.FlowchartDiagram | models.SequenceDiagram,
    diagram2: models.FlowchartDiagram | models.SequenceDiagram,
) -> dict:
    """
    Compute diff between two diagrams of the same type.

    Returns a dict with 'added', 'removed', 'changed' keys listing items
    that differ between the two diagrams.
    """
    if type(diagram1) != type(diagram2):
        raise ValueError(
            f"Cannot diff {type(diagram1).__name__} with {type(diagram2).__name__}"
        )

    result = {"added": [], "removed": [], "changed": []}

    if isinstance(diagram1, models.FlowchartDiagram):
        assert isinstance(diagram2, models.FlowchartDiagram)

        nodes1 = {n.id: n for n in diagram1.nodes}
        nodes2 = {n.id: n for n in diagram2.nodes}

        for node_id in set(nodes2.keys()) - set(nodes1.keys()):
            result["added"].append(("node", node_id, nodes2[node_id]))

        for node_id in set(nodes1.keys()) - set(nodes2.keys()):
            result["removed"].append(("node", node_id, nodes1[node_id]))

        for node_id in set(nodes1.keys()) & set(nodes2.keys()):
            if nodes1[node_id] != nodes2[node_id]:
                result["changed"].append(
                    ("node", node_id, nodes1[node_id], nodes2[node_id])
                )

        edges1 = {(e.source, e.target): e for e in diagram1.edges}
        edges2 = {(e.source, e.target): e for e in diagram2.edges}

        for edge_key in set(edges2.keys()) - set(edges1.keys()):
            result["added"].append(("edge", edge_key, edges2[edge_key]))

        for edge_key in set(edges1.keys()) - set(edges2.keys()):
            result["removed"].append(("edge", edge_key, edges1[edge_key]))

        for edge_key in set(edges1.keys()) & set(edges2.keys()):
            if edges1[edge_key] != edges2[edge_key]:
                result["changed"].append(
                    ("edge", edge_key, edges1[edge_key], edges2[edge_key])
                )

        return result

    if isinstance(diagram1, models.SequenceDiagram):
        assert isinstance(diagram2, models.SequenceDiagram)

        participants1 = {p.id: p for p in diagram1.participants}
        participants2 = {p.id: p for p in diagram2.participants}

        for pid in set(participants2.keys()) - set(participants1.keys()):
            result["added"].append(("participant", pid, participants2[pid]))

        for pid in set(participants1.keys()) - set(participants2.keys()):
            result["removed"].append(("participant", pid, participants1[pid]))

        msg1_count = len(diagram1.messages)
        msg2_count = len(diagram2.messages)

        if msg1_count != msg2_count:
            result["changed"].append(
                ("message_count", msg1_count, msg2_count)
            )

        for i, (m1, m2) in enumerate(zip(diagram1.messages, diagram2.messages)):
            if m1 != m2:
                result["changed"].append(("message", i, m1, m2))

        return result

    raise NotImplementedError(f"Diff not implemented for {type(diagram1).__name__}")


def validate_topology(diagram: models.MermaidDiagram) -> list[str]:
    """
    Validate diagram topology, returning list of issues found (empty = valid).

    Checks depend on diagram type:
    - Flowchart: dangling edge references, cycles (if acyclic is intended)
    - Sequence: missing participants in messages
    - State: unreachable states, missing initial/final
    - Others: type-specific or no checks (valid by construction)
    """
    issues = []

    if isinstance(diagram, models.FlowchartDiagram):
        node_ids = {n.id for n in diagram.nodes}
        for edge in diagram.edges:
            if edge.source not in node_ids:
                issues.append(f"Edge source '{edge.source}' not in nodes")
            if edge.target not in node_ids:
                issues.append(f"Edge target '{edge.target}' not in nodes")

        if diagram.nodes:
            graph = {n.id: [] for n in diagram.nodes}
            for edge in diagram.edges:
                if edge.source in graph and edge.target in graph:
                    graph[edge.source].append(edge.target)

            visited = set()
            rec_stack = set()

            def has_cycle(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                rec_stack.discard(node)
                return False

            for node_id in graph:
                if node_id not in visited and has_cycle(node_id):
                    issues.append(f"Cycle detected in flowchart")
                    break

    elif isinstance(diagram, models.SequenceDiagram):
        participant_ids = {p.id for p in diagram.participants}
        for msg in diagram.messages:
            if msg.from_id not in participant_ids:
                issues.append(
                    f"Message from '{msg.from_id}' not in participants"
                )
            if msg.to_id not in participant_ids:
                issues.append(f"Message to '{msg.to_id}' not in participants")

    elif isinstance(diagram, models.StateDiagram):
        state_ids = {s.id for s in diagram.states}
        initial_count = sum(1 for s in diagram.states if s.is_initial)
        final_count = sum(1 for s in diagram.states if s.is_final)

        if initial_count == 0:
            issues.append("No initial state marked")
        if initial_count > 1:
            issues.append(f"{initial_count} initial states (expected 1)")
        if final_count == 0:
            issues.append("No final state marked")

        for trans in diagram.transitions:
            if trans.from_state not in state_ids:
                issues.append(
                    f"Transition from '{trans.from_state}' not in states"
                )
            if trans.to_state not in state_ids:
                issues.append(
                    f"Transition to '{trans.to_state}' not in states"
                )

        if state_ids and diagram.transitions:
            graph = {s.id: [] for s in diagram.states}
            for trans in diagram.transitions:
                if trans.from_state in graph and trans.to_state in graph:
                    graph[trans.from_state].append(trans.to_state)

            visited = set()

            def dfs(node: str) -> None:
                visited.add(node)
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        dfs(neighbor)

            initial_states = {s.id for s in diagram.states if s.is_initial}
            for initial_id in initial_states:
                dfs(initial_id)

            unreachable = state_ids - visited
            for unreachable_id in unreachable:
                issues.append(f"State '{unreachable_id}' unreachable from initial")

    elif isinstance(diagram, models.ERDiagram):
        entity_names = {e.name for e in diagram.entities}
        for rel in diagram.relationships:
            if rel.from_entity not in entity_names:
                issues.append(
                    f"Relationship from '{rel.from_entity}' not in entities"
                )
            if rel.to_entity not in entity_names:
                issues.append(
                    f"Relationship to '{rel.to_entity}' not in entities"
                )

    return issues
