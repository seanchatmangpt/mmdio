"""
E2E Infrastructure Verification Tests.

Validates that pytest fixtures in conftest.py load cleanly, that all 10 SPARQL
law gates pass, and that all 15 sample diagram fixtures validate against the
Node Mermaid oracle.
"""

from typing import Callable, Dict, List, Tuple

import pytest


def test_sparql_gates_verification(sparql_gate_verifier: Callable[[], Dict[str, List[Tuple]]]) -> None:
    """Verify that all 10 SPARQL law gates evaluate with 0 violations."""
    violations = sparql_gate_verifier()
    assert violations == {}, f"Expected 0 SPARQL gate violations, got: {violations}"


@pytest.mark.parametrize(
    "diagram_type",
    [
        "flowchart",
        "sequence",
        "classDiagram",
        "stateDiagram",
        "er",
        "gantt",
        "pie",
        "gitGraph",
        "c4",
        "mindmap",
        "sankey",
        "kanban",
        "timeline",
        "xychart",
        "block",
    ],
)
def test_sample_diagram_fixture_oracle_validation(
    diagram_type: str,
    all_sample_diagram_sources: Dict[str, str],
    oracle_validator: Callable[[str], str],
) -> None:
    """Verify that each of the 15 diagram type sample text fixtures passes Node oracle validation."""
    source = all_sample_diagram_sources.get(diagram_type)
    assert source is not None, f"Missing fixture source for {diagram_type}"
    output = oracle_validator(source)
    assert "SUCCESS:" in output, f"Oracle failed for {diagram_type}: {output}"


def test_individual_fixtures(
    sample_flowchart_source: str,
    sample_sequence_source: str,
    sample_classDiagram_source: str,
    sample_stateDiagram_source: str,
    sample_er_source: str,
    sample_gantt_source: str,
    sample_pie_source: str,
    sample_gitGraph_source: str,
    sample_c4_source: str,
    sample_mindmap_source: str,
    sample_sankey_source: str,
    sample_kanban_source: str,
    sample_timeline_source: str,
    sample_xychart_source: str,
    sample_block_source: str,
) -> None:
    """Verify that individual sample diagram fixtures load as non-empty strings."""
    fixtures = [
        sample_flowchart_source,
        sample_sequence_source,
        sample_classDiagram_source,
        sample_stateDiagram_source,
        sample_er_source,
        sample_gantt_source,
        sample_pie_source,
        sample_gitGraph_source,
        sample_c4_source,
        sample_mindmap_source,
        sample_sankey_source,
        sample_kanban_source,
        sample_timeline_source,
        sample_xychart_source,
        sample_block_source,
    ]
    for fix in fixtures:
        assert isinstance(fix, str)
        assert len(fix.strip()) > 0
