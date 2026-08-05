"""Test the all-dialect mmdio REST API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mmdio.api import app

client = TestClient(app)


def test_health_and_capabilities() -> None:
    assert client.get("/health").json() == {"standing": "ALIVE", "diagram_types": 39}
    response = client.get("/v1/capabilities")
    assert response.status_code == 200
    assert response.json()["count"] == 39


def test_parse_validate_and_verify_receipt() -> None:
    source = "architecture-beta\n  service api(server)[API]\n"
    parsed = client.post("/v1/parse", json={"source": source})
    assert parsed.status_code == 200
    assert parsed.json()["document"]["type"] == "architecture"

    validated = client.post("/v1/validate", json={"source": source})
    assert validated.status_code == 200
    receipt = validated.json()["receipt"]

    verified = client.post("/v1/receipts/verify", json={"receipt": receipt})
    assert verified.status_code == 200
    assert verified.json()["source"] == source


def test_unknown_source_is_422_refusal() -> None:
    response = client.post("/v1/parse", json={"source": "not mermaid\n"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "MMDIO-TYPE-002"


def test_diff_and_merge_routes() -> None:
    base = "timeline\n  2026 : base\n"
    left = "timeline\n  2026 : left\n"
    difference = client.post("/v1/diff", json={"left": base, "right": left})
    assert difference.status_code == 200
    assert difference.json()["diff"]["changed"] is True

    merged = client.post("/v1/merge", json={"base": base, "left": left, "right": base})
    assert merged.status_code == 200
    assert merged.json()["merge"]["selected"] == "left"
