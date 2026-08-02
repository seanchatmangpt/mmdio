"""
Comprehensive Empirical Audit of E2E Oracle Harness and Test Suite
"""

import subprocess
import tempfile
import os
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ORACLE_SCRIPT = PROJECT_ROOT / "tests" / "oracle" / "verify_mermaid.mjs"

# Corrupted diagram test suite
CORRUPT_CASES = {
    "flowchart_truncated_edge": ("flowchart TD\n  A -->", "flowchart"),
    "flowchart_unclosed_label": ("flowchart TD\n  A[Unclosed label", "flowchart"),
    "sequence_invalid_syntax": ("sequenceDiagram\n  actor Alice\n  Alice-->Bob invalid syntax", "sequence"),
    "pie_invalid_value": ("pie title Broken Pie\n  \"Category 1\" : not_a_number", "pie"),
    "c4_broken_macro": ("C4Context\n  Person(unclosed_macro", "c4"),
    "mindmap_unbalanced": ("mindmap\n  root((Unclosed", "mindmap"),
    "er_invalid_cardinality": ("erDiagram\n  CUSTOMER ||--invalid_cardinality ORDER : places", "er"),
    "gantt_invalid_date": ("gantt\n  dateFormat INVALID_DATE_FORMAT\n  section Test\n  Task1 : a1, invalid-date, 30d", "gantt"),
    "git_broken_command": ("gitGraph\n  invalidGitCommand", "git"),
    "invalid_header": ("invalidDiagramHeaderType\n  A -> B", "unknown"),
}

def audit_current_oracle():
    print("======================================================================")
    print("AUDITING CURRENT E2E ORACLE HARNESS (verify_mermaid.mjs)")
    print("======================================================================")
    
    results = {}
    for name, (source, expected_type) in CORRUPT_CASES.items():
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(source)
            temp_path = f.name
            
        try:
            res = subprocess.run(
                ["node", str(ORACLE_SCRIPT), temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            passed = (res.returncode == 0)
            results[name] = {
                "passed_oracle": passed,
                "returncode": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip()
            }
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    accepted_corrupt_count = sum(1 for r in results.values() if r["passed_oracle"])
    rejected_corrupt_count = sum(1 for r in results.values() if not r["passed_oracle"])
    
    print(f"Total Corrupted Test Cases: {len(CORRUPT_CASES)}")
    print(f"Oracle ACCEPTED (False Positives): {accepted_corrupt_count}")
    print(f"Oracle REJECTED (Correct Failures): {rejected_corrupt_count}\n")
    
    for name, r in results.items():
        status = "FALSE POSITIVE (PASS)" if r["passed_oracle"] else "CORRECT REJECTION (FAIL)"
        print(f"[{status}] {name}:")
        print(f"   Stdout: {r['stdout']}")
        if r['stderr']:
            print(f"   Stderr: {r['stderr']}")
            
    return results

def audit_fixed_oracle_behavior():
    print("\n======================================================================")
    print("DEMONSTRATING INTENDED BEHAVIOR WITH mermaid.parse()")
    print("======================================================================")
    
    # Inline node script testing mermaid.parse vs detectType
    node_test_script = """
    import fs from 'node:fs/promises';
    import mermaid from 'mermaid';

    const filePath = process.argv[2];
    await mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
    const source = await fs.readFile(filePath, 'utf8');

    try {
        const parseRes = await mermaid.parse(source);
        console.log("PARSE_SUCCESS");
        process.exit(0);
    } catch (e) {
        console.error("PARSE_ERROR: " + e.message);
        process.exit(1);
    }
    """
    
    oracle_dir = PROJECT_ROOT / "tests" / "oracle"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mjs", dir=str(oracle_dir), delete=False) as script_file:
        script_file.write(node_test_script)
        script_path = script_file.name
        
    try:
        results = {}
        for name, (source, expected_type) in CORRUPT_CASES.items():
            with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as mmd_file:
                mmd_file.write(source)
                mmd_path = mmd_file.name
                
            try:
                res = subprocess.run(
                    ["node", script_path, mmd_path],
                    cwd=str(PROJECT_ROOT / "tests" / "oracle"),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                results[name] = {
                    "passed_parse": (res.returncode == 0),
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip()
                }
            finally:
                if os.path.exists(mmd_path):
                    os.unlink(mmd_path)
                    
        rejected_count = sum(1 for r in results.values() if not r["passed_parse"])
        print(f"With mermaid.parse(): {rejected_count}/{len(CORRUPT_CASES)} corrupted diagrams were REJECTED as expected!")
        for name, r in results.items():
            print(f"[{'FAIL' if not r['passed_parse'] else 'PASS'}] {name} -> Stderr: {r['stderr']}")
    finally:
        if os.path.exists(script_path):
            os.unlink(script_path)

if __name__ == "__main__":
    audit_current_oracle()
    audit_fixed_oracle_behavior()
