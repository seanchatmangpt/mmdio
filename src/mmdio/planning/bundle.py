"""Planning-document bundle manufacture and deterministic Markdown plan books."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .model import PlanningGraph
from .projections import PlanningDocument, generate_planning_documents
from .receipts import CLAIM_CEILING, PlanningDocumentReceipt, receipt_for, verify_receipt


@dataclass(frozen=True, slots=True)
class PlanningDocumentationBundle:
    """All justified documentation projections for one exact planning graph."""

    graph: PlanningGraph
    documents: tuple[PlanningDocument, ...]
    receipts: tuple[PlanningDocumentReceipt, ...]

    def markdown(self) -> str:
        """Render the complete planning book as deterministic Markdown."""
        lines = [
            f"# {self.graph.subject}",
            "",
            f"- Formalism: `{self.graph.formalism}`",
            f"- Planning digest: `{self.graph.digest()}`",
            f"- Claim ceiling: `{CLAIM_CEILING}`",
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
        return {
            "schema": "mmdio.planning-document-bundle/1",
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
            "claim_ceiling": CLAIM_CEILING,
        }

    def manifest_json(self) -> str:
        """Serialize the bundle manifest deterministically."""
        return json.dumps(self.manifest(), sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    def verify(self) -> None:
        """Verify every receipt and the one-to-one document/receipt cardinality."""
        if len(self.documents) != len(self.receipts):
            raise ValueError("MMDIO-PLAN-009 planning bundle document/receipt cardinality mismatch")
        for document, receipt in zip(self.documents, self.receipts, strict=True):
            verify_receipt(self.graph, document, receipt)


def generate_planning_bundle(subject: PlanningGraph) -> PlanningDocumentationBundle:
    """Generate every applicable planning document and bind each to a receipt."""
    documents = generate_planning_documents(subject)
    receipts = tuple(receipt_for(subject, document) for document in documents)
    bundle = PlanningDocumentationBundle(graph=subject, documents=documents, receipts=receipts)
    bundle.verify()
    return bundle
