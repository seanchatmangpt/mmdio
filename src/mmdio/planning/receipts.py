"""Receipt and replay primitives for planning-document projections."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from .model import PlanningGraph
from .projections import PlanningDocument


CLAIM_CEILING = "PLANNING_DOCUMENT_PROJECTION_ONLY"


@dataclass(frozen=True, slots=True)
class PlanningDocumentReceipt:
    """Tamper-evident binding between a planning graph and one Mermaid projection."""

    schema: str
    formalism: str
    subject: str
    planning_digest: str
    document_name: str
    diagram_type: str
    document_sha256: str
    claim_ceiling: str = CLAIM_CEILING

    def canonical_json(self) -> str:
        """Serialize the receipt carrier deterministically."""
        return json.dumps(
            asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )

    def digest(self) -> str:
        """Return the SHA-256 identity of this receipt carrier."""
        return sha256(self.canonical_json().encode()).hexdigest()


def receipt_for(subject: PlanningGraph, document: PlanningDocument) -> PlanningDocumentReceipt:
    """Manufacture one bounded projection receipt."""
    if document.planning_digest != subject.digest():
        raise ValueError("MMDIO-PLAN-007 document does not bind the supplied planning graph")
    return PlanningDocumentReceipt(
        schema="mmdio.planning-document-receipt/1",
        formalism=subject.formalism,
        subject=subject.subject,
        planning_digest=subject.digest(),
        document_name=document.name,
        diagram_type=document.diagram_type,
        document_sha256=document.content_sha256(),
    )


def verify_receipt(
    subject: PlanningGraph,
    document: PlanningDocument,
    receipt: PlanningDocumentReceipt,
) -> None:
    """Refuse a receipt that does not replay from the exact subject and document bytes."""
    expected = receipt_for(subject, document)
    if receipt != expected:
        raise ValueError("MMDIO-PLAN-008 planning-document receipt mismatch")
