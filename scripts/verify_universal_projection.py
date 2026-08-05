#!/usr/bin/env python3
"""Verify registry → capability ontology → Python projection closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from mmdio.engine.documents import DOCUMENT_CLASS_BY_TYPE
from mmdio.engine.supported import GENERATED_PYTHON_SUPPORTED
from mmdio.engine.universal import CATALOG, capability_json

ROOT = Path(__file__).resolve().parents[1]
MER = Namespace("https://seanchatmangpt.github.io/ontology/mermaid#")


def _require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    """Execute projection and SPARQL closure gates, then emit a receipt."""
    graph = Graph()
    for path in (
        ROOT / "src/mmdio/engine/registry.ttl",
        ROOT / "packs/mmdio-pack/ontology.ttl",
        ROOT / "packs/mmdio-pack/universal-capabilities.ttl",
    ):
        graph.parse(path)

    registry_ids = {
        str(graph.value(subject, MER.diagramId))
        for subject in graph.subjects(RDF.type, MER.DiagramType)
        if graph.value(subject, MER.diagramId) is not None
    }
    catalog_ids = {spec.diagram_type.value for spec in CATALOG}
    document_ids = {diagram_type.value for diagram_type in DOCUMENT_CLASS_BY_TYPE}

    _require(len(registry_ids) == 39, registry_ids)
    _require(
        registry_ids == catalog_ids == document_ids == set(GENERATED_PYTHON_SUPPORTED),
        "registry/catalog/document/supported type sets differ",
    )

    subjects = {
        str(graph.value(subject, MER.diagramId)): subject
        for subject in graph.subjects(RDF.type, MER.DiagramType)
    }
    for spec in CATALOG:
        subject = subjects[spec.diagram_type.value]
        _require(
            str(graph.value(subject, MER.documentClassName)) == spec.document_class,
            spec.diagram_type.value,
        )
        _require(
            str(graph.value(subject, MER.oracleExample)) == spec.upstream_example,
            spec.diagram_type.value,
        )
        _require(
            str(graph.value(subject, MER.oracleProfile)) == spec.oracle_profile.value,
            spec.diagram_type.value,
        )
        _require(
            {str(value) for value in graph.objects(subject, MER.acceptedJsType)}
            == set(spec.accepted_js_types),
            spec.diagram_type.value,
        )

    gate_results: dict[str, int] = {}
    for gate in sorted((ROOT / "packs/mmdio-pack/gates").glob("*.rq")):
        violations = list(graph.query(gate.read_text(encoding="utf-8")))
        gate_results[gate.name] = len(violations)
        _require(not violations, f"{gate.name}: {violations}")

    manifest = capability_json().encode()
    receipt = {
        "schema": "mmdio.universal-projection/v1",
        "registry_types": len(registry_ids),
        "catalog_types": len(catalog_ids),
        "document_classes": len(document_ids),
        "supported_types": len(GENERATED_PYTHON_SUPPORTED),
        "capability_sha256": hashlib.sha256(manifest).hexdigest(),
        "sparql_gates": gate_results,
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
