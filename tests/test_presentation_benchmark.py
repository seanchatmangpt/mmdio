# Copyright (c) 2026 Sean Chatman
"""Regression bound for the presentation projection benchmark (real subprocess, real files)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "presentation_bench.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )


def test_projection_costs_one_admission_not_one_per_file() -> None:
    result = _run("--sizes", "400,1000", "--repeats", "5")
    receipt = json.loads(result.stdout)
    assert result.returncode == 0, result.stdout + result.stderr
    assert receipt["schema"] == "mmdio.presentation-benchmark/1"
    assert receipt["verdict"] == "PASS"
    assert receipt["worst_write_over_verify"] <= receipt["max_ratio"] == 3.5
    assert [row["documents"] for row in receipt["rows"]] == [4, 4]
    assert all(row["replay_s"] > 0 for row in receipt["rows"])


def test_bound_is_not_vacuous() -> None:
    # An impossible ceiling must be refused, proving the gate can fail.
    result = _run("--sizes", "400", "--repeats", "3", "--max-ratio", "0.01")
    assert result.returncode == 1
    assert json.loads(result.stdout)["verdict"] == "REGRESSION"
    # A run with no gated size is a refused (vacuous) benchmark, not a pass.
    vacuous = _run("--sizes", "10", "--repeats", "1")
    assert vacuous.returncode == 2
    assert "vacuous" in vacuous.stderr
