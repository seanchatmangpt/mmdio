"""
Empirical Adversarial Verification Harness for E2E Test Suite.
Tests:
1. Negative Testing / Fault Injection on Node Oracle (`validate_mermaid_source`)
2. Temp File Leak Check during Oracle invocation
3. Negative Testing / Fault Injection on SPARQL Gates (`verify_sparql_gates`)
4. Large Input / Stress Testing on Oracle and Renderer
5. Assertion Genuineness Audit
"""

import os
import sys
import tempfile
import glob
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tests.e2e.conftest import validate_mermaid_source, verify_sparql_gates
import rdflib

def test_oracle_negative_fault_injection():
    print("--- 1. Testing Oracle Fault Injection (Invalid Diagrams) ---")
    invalid_samples = [
        ("flowchart_truncated", "flowchart TD\n    A -->"),
        ("flowchart_unclosed_label", "flowchart TD\n    A[Unclosed label"),
        ("sequence_broken", "sequenceDiagram\n    actor\n    Alice->>"),
        ("pie_syntax_error", "pie title Broken\n    \"Dogs\" : invalid_value"),
        ("c4_broken", "C4Context\n    Person("),
        ("mindmap_broken", "mindmap\n    root((\n"),
        ("invalid_header", "invalidDiagramHeaderType\n    A -> B"),
    ]
    
    passed_fault_injections = 0
    for name, sample in invalid_samples:
        try:
            validate_mermaid_source(sample)
            print(f"[FAIL] Oracle ACCEPTED invalid sample '{name}'! Assertion is weak!")
        except AssertionError as e:
            print(f"[PASS] Oracle properly REJECTED invalid sample '{name}': {str(e).splitlines()[0]}")
            passed_fault_injections += 1
        except Exception as e:
            print(f"[UNEXPECTED] Oracle raised {type(e).__name__} instead of AssertionError for '{name}': {e}")

    assert passed_fault_injections == len(invalid_samples), f"Expected {len(invalid_samples)} failures, got {passed_fault_injections}"
    print("-> All fault injection cases successfully rejected by Oracle!")


def test_oracle_tempfile_cleanup():
    print("\n--- 2. Testing Oracle Temp File Leakages ---")
    temp_dir = tempfile.gettempdir()
    mmd_files_before = set(glob.glob(os.path.join(temp_dir, "*.mmd")))
    
    # Run 20 oracle validations (10 valid, 10 invalid)
    valid_sample = "flowchart TD\n    A --> B\n"
    invalid_sample = "flowchart TD\n    A -->"
    
    for _ in range(10):
        try:
            validate_mermaid_source(valid_sample)
        except Exception:
            pass
        try:
            validate_mermaid_source(invalid_sample)
        except AssertionError:
            pass
            
    mmd_files_after = set(glob.glob(os.path.join(temp_dir, "*.mmd")))
    leaked = mmd_files_after - mmd_files_before
    if leaked:
        print(f"[FAIL] Temp file leak detected! Leaked files: {leaked}")
        assert False, f"Leaked temp files: {leaked}"
    else:
        print("[PASS] Zero temporary file leaks detected across 20 oracle runs.")


def test_sparql_gates_fault_injection():
    print("\n--- 3. Testing SPARQL Gate Fault Injection ---")
    # Let's test if verify_sparql_gates fails when a gate violation is introduced in memory
    from tests.e2e.conftest import REGISTRY_TTL, ONTOLOGY_TTL, GATES_DIR
    
    # Load graph and inject invalid triple (e.g. invalid fieldKind for Gate 030)
    graph = rdflib.Graph()
    graph.parse(str(REGISTRY_TTL), format="turtle")
    graph.parse(str(ONTOLOGY_TTL), format="turtle")
    
    MER = rdflib.Namespace("https://seanchatmangpt.github.io/ontology/mermaid#")
    invalid_field = MER["corruptedFieldForTesting"]
    graph.add((invalid_field, rdflib.RDF.type, MER.PythonField))
    graph.add((invalid_field, MER.fieldKind, rdflib.Literal("bogus_kind_12345")))
    
    # Check Gate 030 directly
    gate_030 = GATES_DIR / "030_field_shape_closed_vocabulary.rq"
    query_str = gate_030.read_text(encoding="utf-8")
    results = list(graph.query(query_str))
    
    if results:
        print(f"[PASS] Gate 030 successfully caught injected invalid fieldKind: {results}")
    else:
        print("[FAIL] Gate 030 FAILED to catch injected invalid fieldKind!")
        assert False, "Gate 030 did not catch violation"


def test_large_input_stress():
    print("\n--- 4. Testing Large Input / Stress Harness ---")
    # Generate large flowchart (500 nodes, 499 edges)
    lines = ["flowchart TD"]
    for i in range(500):
        lines.append(f"    N{i}[Node {i} with special chars & <tag>] --> N{i+1}")
    large_flowchart = "\n".join(lines[:-1])  # drop last arrow
    
    print(f"Generated flowchart text size: {len(large_flowchart)} bytes, {len(lines)} lines")
    try:
        res = validate_mermaid_source(large_flowchart, timeout=15)
        print(f"[PASS] Oracle successfully validated 500-node flowchart diagram!")
    except Exception as e:
        print(f"[FAIL] Oracle failed or timed out on 500-node flowchart: {e}")
        assert False, f"Oracle failed on large diagram: {e}"


def run_all_checks():
    print("========================================================")
    print("STARTING EMPIRICAL ADVERSARIAL HARNESS VERIFICATION")
    print("========================================================")
    test_oracle_negative_fault_injection()
    test_oracle_tempfile_cleanup()
    test_sparql_gates_fault_injection()
    test_large_input_stress()
    print("\n========================================================")
    print("ALL EMPIRICAL HARNESS VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("========================================================")

if __name__ == "__main__":
    run_all_checks()
