"""mmdio REST API for every registered Mermaid diagram type."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from mmdio.engine import (
    DocumentError,
    capability_records,
    canonicalize_source,
    detect_document_type,
    diff_documents,
    issue_receipt,
    merge_documents,
    parse_document,
    verify_receipt,
)

app = FastAPI(title="mmdio", version="0.2.0")


class SourceRequest(BaseModel):
    """Source-bearing request with an optional declared profile type."""

    model_config = ConfigDict(extra="forbid")
    source: str = Field(min_length=1)
    diagram_type: str | None = None


class PairRequest(BaseModel):
    """Two source subjects for a same-type diff."""

    model_config = ConfigDict(extra="forbid")
    left: str = Field(min_length=1)
    right: str = Field(min_length=1)


class MergeRequest(BaseModel):
    """Three source subjects for a bounded merge."""

    model_config = ConfigDict(extra="forbid")
    base: str = Field(min_length=1)
    left: str = Field(min_length=1)
    right: str = Field(min_length=1)


class ReceiptRequest(BaseModel):
    """Receipt carrier supplied for independent replay verification."""

    model_config = ConfigDict(extra="forbid")
    receipt: dict[str, Any]


def _http_refusal(exc: DocumentError) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={"standing": "REFUSED", "code": exc.code, "message": str(exc)},
    )


@app.get("/health")
def health() -> dict[str, Any]:
    """Return bounded service and capability standing."""
    return {"standing": "ALIVE", "diagram_types": len(capability_records())}


@app.get("/v1/capabilities")
def capabilities() -> dict[str, Any]:
    """Return the exact 39-type executable capability manifest."""
    records = capability_records()
    return {"count": len(records), "types": records}


@app.post("/v1/detect")
def detect(request: SourceRequest) -> dict[str, Any]:
    """Detect a canonical diagram type."""
    try:
        diagram_type = detect_document_type(request.source)
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {"standing": "ALIVE", "diagram_type": diagram_type.value}


@app.post("/v1/parse")
def parse(request: SourceRequest) -> dict[str, Any]:
    """Parse source into its exact lossless document class."""
    try:
        document = parse_document(request.source, request.diagram_type)
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {"standing": "ALIVE", "document": document.model_dump(mode="json")}


@app.post("/v1/canonicalize")
def canonicalize(request: SourceRequest) -> dict[str, Any]:
    """Canonicalize and re-admit source."""
    try:
        source = canonicalize_source(request.source)
        document = parse_document(source, request.diagram_type)
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {
        "standing": "ALIVE",
        "diagram_type": str(document.type),
        "source": source,
        "source_sha256": document.source_sha256,
    }


@app.post("/v1/validate")
def validate(request: SourceRequest) -> dict[str, Any]:
    """Validate, receipt, and expose replay evidence."""
    try:
        document = parse_document(request.source, request.diagram_type)
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {"standing": "ALIVE", "receipt": issue_receipt(document)}


@app.post("/v1/diff")
def diff(request: PairRequest) -> dict[str, Any]:
    """Diff two same-type canonical documents."""
    try:
        result = diff_documents(parse_document(request.left), parse_document(request.right))
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {"standing": "ALIVE", "diff": result.model_dump(mode="json")}


@app.post("/v1/merge")
def merge(request: MergeRequest) -> dict[str, Any]:
    """Execute a conflict-safe three-way merge."""
    try:
        result = merge_documents(
            parse_document(request.base),
            parse_document(request.left),
            parse_document(request.right),
        )
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {"standing": "ALIVE", "merge": result.model_dump(mode="json")}


@app.post("/v1/receipts/verify")
def verify(request: ReceiptRequest) -> dict[str, Any]:
    """Verify receipt identity and replay its source."""
    try:
        document = verify_receipt(request.receipt)
    except DocumentError as exc:
        raise _http_refusal(exc) from exc
    return {
        "standing": "ALIVE",
        "diagram_type": str(document.type),
        "source_sha256": document.source_sha256,
        "source": document.source,
    }
