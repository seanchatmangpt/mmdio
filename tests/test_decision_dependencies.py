from __future__ import annotations

import pytest


def test_scikit_decide_imports_in_decision_runtime() -> None:
    pytest.importorskip("skdecide")
    from mmdio.decide.backend import ScikitDecideBackend

    backend = ScikitDecideBackend()
    assert isinstance(backend.list_domains(), list)
    assert isinstance(backend.list_solvers(), list)


def test_fastmcp_server_constructs_in_decision_runtime() -> None:
    pytest.importorskip("fastmcp")
    from mmdio.decide.mcp import create_server

    assert create_server() is not None
