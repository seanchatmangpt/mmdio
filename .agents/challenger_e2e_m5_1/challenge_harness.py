"""
Empirical Challenge Harness for E2E Test Suite verification.
Runs adversarial tests against validate_mermaid_source, verify_sparql_gates, and mmdio parsers/renderers.
"""

import concurrent.futures
import os
import glob
import tempfile
import sys
from pathlib import Path
import pytest
import rdflib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tests.e2e.conftest import validate_mermaid_source, verify_sparql_gates
from mmdio.engine.parser import MermaidParser, ParsingError
from mmdio.engine.render import render_diagram


def test_challenge_oracle_rejects_corrupted_diagrams():
    """Verify validate_mermaid_source raises AssertionError on invalid Mermaid text."""
    corrupted_inputs = [
        "INVALID_HEADER_XYZ",
        "flowchart TD\n  A --->>> B",
        "sequenceDiagram\n  participant A\n  A -> -> ->",
        "pie title Bad\n  \"Slice 1\" : not_a_number",
        "erDiagram\n  A ||--|| B :: bad syntax",
        "c4Context\n  Person(a, b, c, d, e, f, g)",
        "gantt\n  dateFormat INVALID_DATE\n  task : 2026-99-99, 10d",
        "block-beta\n  columns -5",
    ]

    rejected_count = 0
    for idx, invalid_src in enumerate(corrupted_inputs):
        try:
            validate_mermaid_source(invalid_src)
            print(f"FAILED: Oracle unexpectedly accepted invalid diagram #{idx}: {invalid_src!r}")
        except AssertionError as e:
            rejected_count += 1
            # Verify failure message contains PARSE_ERROR or rejected text
            assert "rejected diagram" in str(e) or "Exit Code" in str(e)

    print(f"Oracle rejected {rejected_count}/{len(corrupted_inputs)} corrupted diagrams.")
    assert rejected_count == len(corrupted_inputs), f"Expected {len(corrupted_inputs)} rejections, got {rejected_count}"


def test_challenge_parser_rejects_corrupted_diagrams():
    """Verify MermaidParser raises ParsingError or ValueError on invalid inputs."""
    parser = MermaidParser()
    corrupted_inputs = [
        "flowchart TD\n  A[Unclosed bracket",
        "sequenceDiagram\n  A->",
        "pie title\n  \"Dogs\"",
    ]

    rejected_count = 0
    for invalid_src in corrupted_inputs:
        try:
            parser.parse(invalid_src)
            print(f"FAILED: Parser accepted invalid input: {invalid_src!r}")
        except (ParsingError, ValueError, Exception) as e:
            rejected_count += 1

    assert rejected_count == len(corrupted_inputs), f"Expected parser to reject all corrupted inputs, rejected {rejected_count}"


def test_challenge_temp_file_cleanup():
    """Verify validate_mermaid_source leaves no orphan .mmd files in temp directory."""
    temp_dir = tempfile.gettempdir()
    initial_mmd_files = set(glob.glob(os.path.join(temp_dir, "*.mmd")))

    # Run 10 oracle calls (5 valid, 5 invalid)
    valid_src = "flowchart TD\n  A --> B"
    invalid_src = "INVALID_DIAGRAM_TEXT"

    for _ in range(5):
        try:
            validate_mermaid_source(valid_src)
        except Exception:
            pass
        try:
            validate_mermaid_source(invalid_src)
        except Exception:
            pass

    after_mmd_files = set(glob.glob(os.path.join(temp_dir, "*.mmd")))
    leaked = after_mmd_files - initial_mmd_files
    print(f"Leaked temp .mmd files count: {len(leaked)}")
    assert len(leaked) == 0, f"Leaked temporary .mmd files: {leaked}"


def test_challenge_oracle_concurrency():
    """Verify validate_mermaid_source under high concurrent thread load."""
    valid_src = "flowchart TD\n  A --> B\n  B --> C"

    def worker(i):
        res = validate_mermaid_source(valid_src)
        assert "SUCCESS" in res
        return i

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 20
    print("Concurrent oracle validation completed successfully (20 requests across 8 threads).")


def test_challenge_sparql_gate_fault_injection():
    """Inject faults into rdflib graph and verify gates detect them."""
    MER = rdflib.Namespace("https://seanchatmangpt.github.io/ontology/mermaid#")
    gate_path = PROJECT_ROOT / "packs/mmdio-pack/gates/020_no_duplicate_internal_id.rq"
    query_text = gate_path.read_text(encoding="utf-8")

    g = rdflib.Graph()
    t1 = MER["Type1"]
    t2 = MER["Type2"]

    g.add((t1, rdflib.RDF.type, MER.DiagramType))
    g.add((t1, MER.pythonSupport, rdflib.Literal(True)))
    g.add((t1, MER.pythonInternalId, rdflib.Literal("duplicate_id")))

    g.add((t2, rdflib.RDF.type, MER.DiagramType))
    g.add((t2, MER.pythonSupport, rdflib.Literal(True)))
    g.add((t2, MER.pythonInternalId, rdflib.Literal("duplicate_id")))

    res = list(g.query(query_text))
    assert len(res) == 1
    assert str(res[0][0]) == "duplicate_id"
    print("SPARQL Law Gate 020 correctly detected injected duplicate internal ID.")


if __name__ == "__main__":
    print("=== Running Empirical Challenge Harness ===")
    test_challenge_oracle_rejects_corrupted_diagrams()
    test_challenge_parser_rejects_corrupted_diagrams()
    test_challenge_temp_file_cleanup()
    test_challenge_oracle_concurrency()
    test_challenge_sparql_gate_fault_injection()
    print("=== ALL EMPIRICAL CHALLENGE HARNESS TESTS PASSED ===")
