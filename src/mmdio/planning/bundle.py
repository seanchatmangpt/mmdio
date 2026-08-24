"""Planning-document bundle manufacture and deterministic Markdown plan books."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .dfcm import PlanningDFCMMatrix, generate_planning_dfcm
from .model import PlanningGraph
from .projections import PlanningDocument, generate_planning_documents
from .receipts import CLAIM_CEILING, PlanningDocumentReceipt, receipt_for, verify_receipt


@dataclass(frozen=True, slots=True)
class PlanningDocumentationBundle:
    """All justified documentation projections for one exact planning graph."""

    graph: PlanningGraph
    documents: tuple[PlanningDocument, ...]
    receipts: tuple[PlanningDocumentReceipt, ...]
    dfcm: PlanningDFCMMatrix | None = None

    def dfcm_matrix(self) -> PlanningDFCMMatrix:
        """Return the exact DFCM matrix, deriving it for legacy constructors."""
        return self.dfcm if self.dfcm is not None else generate_planning_dfcm(self.graph)

    def markdown(self) -> str:
        """Render the complete planning book as deterministic Markdown."""
        matrix = self.dfcm_matrix()
        lines = [
            f"# {self.graph.subject}",
            "",
            f"- Formalism: `{self.graph.formalism}`",
            f"- Planning digest: `{self.graph.digest()}`",
            f"- Claim ceiling: `{CLAIM_CEILING}`",
            f"- DFCM design candidates: `{matrix.candidate_count}`",
            f"- DFCM admitted: `{matrix.admitted_count}`",
            f"- DFCM refused: `{matrix.refused_count}`",
            f"- DFCM digest: `{matrix.digest()}`",
            "",
        ]
        for document in self.documents:
            lines.extend(
                (
                    f"## {document.name.replace('-', ' ').title()}",
                    "",
                    f"Diagram type: `{document.diagram_type}`",
                    "",
                    "```mermaid",
                    document.content.rstrip("\n"),
                    "```",
                    "",
                )
            )
        return "\n".join(lines)

    def manifest(self) -> dict[str, object]:
        """Return a deterministic evidence manifest for the bundle."""
        markdown = self.markdown()
        matrix = self.dfcm_matrix()
        return {
            "schema": "mmdio.planning-document-bundle/2",
            "formalism": self.graph.formalism,
            "subject": self.graph.subject,
            "planning_digest": self.graph.digest(),
            "markdown_sha256": sha256(markdown.encode()).hexdigest(),
            "documents": [
                {
                    "name": document.name,
                    "diagram_type": document.diagram_type,
                    "document_sha256": document.content_sha256(),
                    "receipt_sha256": receipt.digest(),
                }
                for document, receipt in zip(self.documents, self.receipts, strict=True)
            ],
            "dfcm": {
                "schema": "mmdio.planning-dfcm/1",
                "digest": matrix.digest(),
                "candidate_count": matrix.candidate_count,
                "admitted_count": matrix.admitted_count,
                "refused_count": matrix.refused_count,
            },
            "claim_ceiling": CLAIM_CEILING,
        }

    def manifest_json(self) -> str:
        """Serialize the bundle manifest deterministically."""
        return json.dumps(self.manifest(), sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    def verify(self) -> None:
        """Verify receipts, DFCM closure, and document/disposition correspondence."""
        if len(self.documents) != len(self.receipts):
            raise ValueError("MMDIO-PLAN-009 planning bundle document/receipt cardinality mismatch")
        for document, receipt in zip(self.documents, self.receipts, strict=True):
            verify_receipt(self.graph, document, receipt)
        matrix = self.dfcm_matrix()
        if (
            matrix.formalism != self.graph.formalism
            or matrix.subject != self.graph.subject
            or matrix.planning_digest != self.graph.digest()
        ):
            raise ValueError("MMDIO-DFCM-011 DFCM matrix does not bind the exact planning graph")
        matrix.verify_complete()
        matrix.verify_documents(self.documents)


def generate_planning_bundle(subject: PlanningGraph) -> PlanningDocumentationBundle:
    """Generate every lawful planning document and disposition every DFCM candidate."""
    documents = generate_planning_documents(subject)
    receipts = tuple(receipt_for(subject, document) for document in documents)
    dfcm = generate_planning_dfcm(subject)
    bundle = PlanningDocumentationBundle(
        graph=subject,
        documents=documents,
        receipts=receipts,
        dfcm=dfcm,
    )
    bundle.verify()
    return bundle
