"""
Pytest configuration and fixtures for mmdio E2E test suite.

Provides:
- Node Mermaid oracle verification fixture (`oracle_validator` / `validate_mermaid_source`).
- ggen SPARQL law gate verification fixture (`sparql_gate_verifier` / `verify_sparql_gates`).
- Sample diagram text fixtures for all 15 supported diagram types:
  flowchart, sequence, classDiagram, stateDiagram, er, gantt, pie, gitGraph,
  c4, mindmap, sankey, kanban, timeline, xychart, block.
"""

import glob
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import pytest
import rdflib

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ORACLE_SCRIPT = PROJECT_ROOT / "tests" / "oracle" / "verify_mermaid.mjs"
REGISTRY_TTL = PROJECT_ROOT / "src" / "mmdio" / "engine" / "registry.ttl"
ONTOLOGY_TTL = PROJECT_ROOT / "packs" / "mmdio-pack" / "ontology.ttl"
GATES_DIR = PROJECT_ROOT / "packs" / "mmdio-pack" / "gates"


# ============================================================================
# ORACLE HARNESS FIXTURES
# ============================================================================

def validate_mermaid_source(mmd_source: str, timeout: int = 10) -> str:
    """
    Validate a Mermaid diagram source code string against the Node.js Mermaid oracle.

    Args:
        mmd_source: Mermaid diagram source text.
        timeout: Subprocess execution timeout in seconds.

    Returns:
        The output string from Node stdout on success.

    Raises:
        AssertionError: If node executable is missing or if the oracle rejects the diagram.
    """
    if shutil.which("node") is None:
        pytest.skip("Node.js is not installed or not in PATH")

    if not ORACLE_SCRIPT.exists():
        pytest.fail(f"Oracle script missing at {ORACLE_SCRIPT}")

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".mmd",
        delete=False,
        encoding="utf-8"
    ) as f:
        f.write(mmd_source)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["node", str(ORACLE_SCRIPT), temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        assert result.returncode == 0, (
            f"Mermaid parser rejected diagram.\n"
            f"Exit Code: {result.returncode}\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}\n"
            f"Source:\n{mmd_source}"
        )
        return result.stdout.strip()
    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@pytest.fixture
def oracle_validator() -> Callable[[str], str]:
    """Fixture providing the validate_mermaid_source function."""
    return validate_mermaid_source


# ============================================================================
# SPARQL LAW GATE FIXTURES
# ============================================================================

def verify_sparql_gates(
    registry_path: Optional[Path] = None,
    ontology_path: Optional[Path] = None,
    gates_dir: Optional[Path] = None
) -> Dict[str, List[Tuple]]:
    """
    Evaluates all 10 SPARQL law gates against registry.ttl and ontology.ttl.

    Args:
        registry_path: Path to registry.ttl (default: engine/registry.ttl).
        ontology_path: Path to ontology.ttl (default: packs/mmdio-pack/ontology.ttl).
        gates_dir: Directory containing *.rq files (default: packs/mmdio-pack/gates/).

    Returns:
        Dictionary mapping gate filename to list of violation tuples.

    Raises:
        AssertionError: If any SPARQL law gate has 1 or more violations.
    """
    r_path = registry_path or REGISTRY_TTL
    o_path = ontology_path or ONTOLOGY_TTL
    g_dir = gates_dir or GATES_DIR

    graph = rdflib.Graph()
    graph.parse(str(r_path), format="turtle")
    graph.parse(str(o_path), format="turtle")

    gate_files = sorted(glob.glob(os.path.join(str(g_dir), "*.rq")))
    assert len(gate_files) == 10, f"Expected 10 SPARQL gate files in {g_dir}, found {len(gate_files)}"

    violations: Dict[str, List[Tuple]] = {}
    for gate_file in gate_files:
        gate_name = os.path.basename(gate_file)
        with open(gate_file, "r", encoding="utf-8") as f:
            query_str = f.read()
        results = list(graph.query(query_str))
        if results:
            violations[gate_name] = results

    assert not violations, (
        f"SPARQL Law Gate violations detected:\n" +
        "\n".join(f"  - {gate}: {len(results)} violation(s) ({results})" for gate, results in violations.items())
    )

    return violations


@pytest.fixture
def sparql_gate_verifier() -> Callable[[], Dict[str, List[Tuple]]]:
    """Fixture providing the verify_sparql_gates function."""
    return verify_sparql_gates


# ============================================================================
# SAMPLE DIAGRAM TEXT FIXTURES (15 Diagram Types)
# ============================================================================

@pytest.fixture
def sample_flowchart_source() -> str:
    """Sample text fixture for Flowchart diagram."""
    return (
        "flowchart TD\n"
        "    A[Start] --> B(Process)\n"
        "    B --> C{Decision}\n"
        "    C -->|Yes| D[Result 1]\n"
        "    C -->|No| E[Result 2]\n"
    )


@pytest.fixture
def sample_sequence_source() -> str:
    """Sample text fixture for Sequence diagram."""
    return (
        "sequenceDiagram\n"
        "    autonumber\n"
        "    actor Alice\n"
        "    participant Bob\n"
        "    Alice->>Bob: Hello Bob, how are you?\n"
        "    Bob-->>Alice: Great!\n"
    )


@pytest.fixture
def sample_classDiagram_source() -> str:
    """Sample text fixture for Class Diagram."""
    return (
        "classDiagram\n"
        "    class Animal {\n"
        "        +String name\n"
        "        +int age\n"
        "        +speak()\n"
        "    }\n"
        "    class Dog {\n"
        "        +bark()\n"
        "    }\n"
        "    Dog --|> Animal\n"
    )


@pytest.fixture
def sample_stateDiagram_source() -> str:
    """Sample text fixture for State Diagram."""
    return (
        "stateDiagram-v2\n"
        "    [*] --> Still\n"
        "    Still --> [*]\n"
        "    Still --> Moving\n"
        "    Moving --> Still\n"
        "    Moving --> Crash\n"
        "    Crash --> [*]\n"
    )


@pytest.fixture
def sample_er_source() -> str:
    """Sample text fixture for ER Diagram."""
    return (
        "erDiagram\n"
        "    CUSTOMER ||--o{ ORDER : places\n"
        "    ORDER ||--|{ LINE-ITEM : contains\n"
        "    CUSTOMER {\n"
        "        string name\n"
        "        string custNumber\n"
        "    }\n"
        "    ORDER {\n"
        "        int orderNumber\n"
        "        string deliveryAddress\n"
        "    }\n"
    )


@pytest.fixture
def sample_gantt_source() -> str:
    """Sample text fixture for Gantt Chart."""
    return (
        "gantt\n"
        "    title A Gantt Diagram\n"
        "    dateFormat YYYY-MM-DD\n"
        "    section Section\n"
        "    A task           :a1, 2024-01-01, 30d\n"
        "    Another task     :after a1, 20d\n"
    )


@pytest.fixture
def sample_pie_source() -> str:
    """Sample text fixture for Pie Chart."""
    return (
        "pie title Pets adopted by volunteers\n"
        '    "Dogs" : 386\n'
        '    "Cats" : 85\n'
        '    "Rats" : 15\n'
    )


@pytest.fixture
def sample_gitGraph_source() -> str:
    """Sample text fixture for Git Graph."""
    return (
        "gitGraph\n"
        '    commit id: "1"\n'
        '    commit id: "2"\n'
        "    branch feature\n"
        "    checkout feature\n"
        '    commit id: "3"\n'
        "    checkout main\n"
        "    merge feature\n"
    )


@pytest.fixture
def sample_c4_source() -> str:
    """Sample text fixture for C4 Diagram."""
    return (
        "C4Context\n"
        '    title System Context diagram for Internet Banking System\n'
        '    Person(customer, "Banking Customer", "A customer of the bank.")\n'
        '    System(banking_system, "Internet Banking System", "Allows customers to view info.")\n'
        '    Rel(customer, banking_system, "Uses")\n'
    )


@pytest.fixture
def sample_mindmap_source() -> str:
    """Sample text fixture for Mindmap."""
    return (
        "mindmap\n"
        "    root((mindmap))\n"
        "        Origins\n"
        "            Long history\n"
        "            Popularisation\n"
        "        Research\n"
        "            On organizational behavior\n"
    )


@pytest.fixture
def sample_sankey_source() -> str:
    """Sample text fixture for Sankey Diagram."""
    return (
        "sankey-beta\n"
        "Agricultural waste,Bio-energy,124.729\n"
        "Bio-energy conversion,Bio-energy,0.597\n"
        "Solid,Bio-energy,26.862\n"
    )


@pytest.fixture
def sample_kanban_source() -> str:
    """Sample text fixture for Kanban Board."""
    return (
        "kanban\n"
        "    Todo\n"
        "        [Create UI]\n"
        "        [Design Database]\n"
        "    In Progress\n"
        "        [Implement API]\n"
        "    Done\n"
        "        [Setup Repo]\n"
    )


@pytest.fixture
def sample_timeline_source() -> str:
    """Sample text fixture for Timeline."""
    return (
        "timeline\n"
        "    title History of Social Media Platform\n"
        "    2002 : LinkedIn\n"
        "    2004 : Facebook\n"
        "    2006 : Twitter\n"
    )


@pytest.fixture
def sample_xychart_source() -> str:
    """Sample text fixture for XY Chart."""
    return (
        "xychart-beta\n"
        '    title "Sales Revenue"\n'
        "    x-axis [jan, feb, mar, apr, may]\n"
        '    y-axis "Revenue (in $)" 4000 --> 11000\n'
        "    bar [5000, 6000, 7500, 8200, 9500]\n"
        "    line [4500, 5500, 7000, 8000, 9000]\n"
    )


@pytest.fixture
def sample_block_source() -> str:
    """Sample text fixture for Block Diagram."""
    return (
        "block-beta\n"
        "    columns 3\n"
        "    a:3\n"
        "    b c d\n"
    )


# Standard alias fixtures for alternate naming conventions

@pytest.fixture
def sample_flowchart(sample_flowchart_source: str) -> str:
    return sample_flowchart_source

@pytest.fixture
def sample_sequence(sample_sequence_source: str) -> str:
    return sample_sequence_source

@pytest.fixture
def sample_class(sample_classDiagram_source: str) -> str:
    return sample_classDiagram_source

@pytest.fixture
def sample_class_diagram(sample_classDiagram_source: str) -> str:
    return sample_classDiagram_source

@pytest.fixture
def sample_state(sample_stateDiagram_source: str) -> str:
    return sample_stateDiagram_source

@pytest.fixture
def sample_state_diagram(sample_stateDiagram_source: str) -> str:
    return sample_stateDiagram_source

@pytest.fixture
def sample_er(sample_er_source: str) -> str:
    return sample_er_source

@pytest.fixture
def sample_gantt(sample_gantt_source: str) -> str:
    return sample_gantt_source

@pytest.fixture
def sample_pie(sample_pie_source: str) -> str:
    return sample_pie_source

@pytest.fixture
def sample_git(sample_gitGraph_source: str) -> str:
    return sample_gitGraph_source

@pytest.fixture
def sample_git_graph(sample_gitGraph_source: str) -> str:
    return sample_gitGraph_source

@pytest.fixture
def sample_c4(sample_c4_source: str) -> str:
    return sample_c4_source

@pytest.fixture
def sample_mindmap(sample_mindmap_source: str) -> str:
    return sample_mindmap_source

@pytest.fixture
def sample_sankey(sample_sankey_source: str) -> str:
    return sample_sankey_source

@pytest.fixture
def sample_kanban(sample_kanban_source: str) -> str:
    return sample_kanban_source

@pytest.fixture
def sample_timeline(sample_timeline_source: str) -> str:
    return sample_timeline_source

@pytest.fixture
def sample_xychart(sample_xychart_source: str) -> str:
    return sample_xychart_source

@pytest.fixture
def sample_block(sample_block_source: str) -> str:
    return sample_block_source


@pytest.fixture
def all_sample_diagram_sources(
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
) -> Dict[str, str]:
    """Dictionary mapping each of the 15 diagram types to its sample source string."""
    return {
        "flowchart": sample_flowchart_source,
        "sequence": sample_sequence_source,
        "classDiagram": sample_classDiagram_source,
        "stateDiagram": sample_stateDiagram_source,
        "er": sample_er_source,
        "gantt": sample_gantt_source,
        "pie": sample_pie_source,
        "gitGraph": sample_gitGraph_source,
        "c4": sample_c4_source,
        "mindmap": sample_mindmap_source,
        "sankey": sample_sankey_source,
        "kanban": sample_kanban_source,
        "timeline": sample_timeline_source,
        "xychart": sample_xychart_source,
        "block": sample_block_source,
    }
