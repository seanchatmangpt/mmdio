"""Lossless structured Mermaid documents for every registered mmdio dialect.

The runtime is pure Python. JavaScript is a development oracle only: the pinned
Mermaid parser validates fixtures and emitted source in the oracle workflow.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, ClassVar, Final

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DiagramType(StrEnum):
    """Canonical diagram identifiers from ``engine/registry.ttl``."""

    C4 = "c4"
    FLOWCHART = "flowchart"
    FLOWCHART_V2 = "flowchart-v2"
    FLOWCHART_ELK = "flowchart-elk"
    SWIMLANE = "swimlane"
    ER = "er"
    GIT_GRAPH = "gitGraph"
    GANTT = "gantt"
    INFO = "info"
    PIE = "pie"
    QUADRANT = "quadrantChart"
    XYCHART = "xychart"
    REQUIREMENT = "requirement"
    SEQUENCE = "sequence"
    CLASS = "classDiagram"
    CLASS_V2 = "classDiagram-v2"
    STATE = "stateDiagram"
    STATE_V2 = "stateDiagram-v2"
    JOURNEY = "journey"
    TIMELINE = "timeline"
    MINDMAP = "mindmap"
    KANBAN = "kanban"
    SANKEY = "sankey"
    PACKET = "packet"
    RADAR = "radar"
    BLOCK = "block"
    TREE_VIEW = "treeView"
    ARCHITECTURE = "architecture"
    EVENT_MODELING = "eventmodeling"
    ISHIKAWA = "ishikawa"
    VENN = "venn"
    TREEMAP = "treemap"
    WARDLEY = "wardley"
    CYNEFIN = "cynefin"
    RAILROAD = "railroad"
    RAILROAD_EBNF = "railroad-ebnf"
    RAILROAD_ABNF = "railroad-abnf"
    RAILROAD_PEG = "railroad-peg"
    ZENUML = "zenuml"


class TokenKind(StrEnum):
    """Stable token categories for the universal concrete syntax tree."""

    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = "number"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    TEXT = "text"


class StatementKind(StrEnum):
    """Lossless lexical categories shared by every Mermaid dialect."""

    HEADER = "header"
    DIRECTIVE = "directive"
    COMMENT = "comment"
    STATEMENT = "statement"
    BLANK = "blank"


class OracleProfile(StrEnum):
    """How a registered type is represented in Mermaid 11.16.0."""

    NATIVE = "native"
    PROFILE = "profile"


@dataclass(frozen=True, slots=True)
class DiagramSpec:
    """Admitted capability record for one registered diagram type."""

    diagram_type: DiagramType
    internal_id: str
    document_class: str
    detect_pattern: str
    upstream_example: str
    accepted_js_types: tuple[str, ...]
    oracle_profile: OracleProfile = OracleProfile.NATIVE


# The order is the canonical catalog order in registry.ttl.
CATALOG: Final[tuple[DiagramSpec, ...]] = (
    DiagramSpec(DiagramType.C4, "c4", "C4Document", r"^\s*C4(?:Context|Container|Component|Dynamic|Deployment|Diagram)\b", "c4", ("c4",)),
    DiagramSpec(DiagramType.FLOWCHART, "flowchart", "FlowchartDocument", r"^\s*(?:flowchart|graph)\b", "flowchart", ("flowchart-v2", "flowchart")),
    DiagramSpec(DiagramType.FLOWCHART_V2, "flowchart-v2", "FlowchartV2Document", r"^\s*flowchart-v2\b", "flowchart", ("flowchart-v2", "flowchart"), OracleProfile.PROFILE),
    DiagramSpec(DiagramType.FLOWCHART_ELK, "flowchart-elk", "FlowchartElkDocument", r"^\s*flowchart-elk\b", "flowchart", ("flowchart-v2", "flowchart"), OracleProfile.PROFILE),
    DiagramSpec(DiagramType.SWIMLANE, "swimlane", "SwimlaneDocument", r"^\s*swimlane\b", "flowchart", ("flowchart-v2", "flowchart"), OracleProfile.PROFILE),
    DiagramSpec(DiagramType.ER, "er", "ERDocument", r"^\s*erDiagram\b", "er", ("er",)),
    DiagramSpec(DiagramType.GIT_GRAPH, "git", "GitGraphDocument", r"^\s*gitGraph\b", "git", ("gitGraph", "git")),
    DiagramSpec(DiagramType.GANTT, "gantt", "GanttDocument", r"^\s*gantt\b", "gantt", ("gantt",)),
    DiagramSpec(DiagramType.INFO, "info", "InfoDocument", r"^\s*info\b", "info", ("info",)),
    DiagramSpec(DiagramType.PIE, "pie", "PieDocument", r"^\s*pie\b", "pie", ("pie",)),
    DiagramSpec(DiagramType.QUADRANT, "quadrantChart", "QuadrantChartDocument", r"^\s*quadrantChart\b", "quadrant-chart", ("quadrantChart",)),
    DiagramSpec(DiagramType.XYCHART, "xychart", "XYChartDocument", r"^\s*xychart(?:-beta)?\b", "xychart", ("xychart", "xychart-beta")),
    DiagramSpec(DiagramType.REQUIREMENT, "requirement", "RequirementDocument", r"^\s*requirementDiagram\b", "requirement", ("requirement",)),
    DiagramSpec(DiagramType.SEQUENCE, "sequence", "SequenceDocument", r"^\s*sequenceDiagram\b", "sequence", ("sequence",)),
    DiagramSpec(DiagramType.CLASS, "class", "ClassDiagramDocument", r"^\s*classDiagram\b", "class", ("classDiagram", "class")),
    DiagramSpec(DiagramType.CLASS_V2, "classDiagram-v2", "ClassDiagramV2Document", r"^\s*classDiagram-v2\b", "class", ("classDiagram", "class"), OracleProfile.PROFILE),
    DiagramSpec(DiagramType.STATE, "state", "StateDiagramDocument", r"^\s*stateDiagram\b", "state", ("stateDiagram", "state")),
    DiagramSpec(DiagramType.STATE_V2, "stateDiagram-v2", "StateDiagramV2Document", r"^\s*stateDiagram-v2\b", "state", ("stateDiagram", "state"), OracleProfile.PROFILE),
    DiagramSpec(DiagramType.JOURNEY, "journey", "JourneyDocument", r"^\s*journey\b", "user-journey", ("journey",)),
    DiagramSpec(DiagramType.TIMELINE, "timeline", "TimelineDocument", r"^\s*timeline\b", "timeline", ("timeline",)),
    DiagramSpec(DiagramType.MINDMAP, "mindmap", "MindmapDocument", r"^\s*mindmap\b", "mindmap", ("mindmap",)),
    DiagramSpec(DiagramType.KANBAN, "kanban", "KanbanDocument", r"^\s*kanban\b", "kanban", ("kanban",)),
    DiagramSpec(DiagramType.SANKEY, "sankey", "SankeyDocument", r"^\s*sankey(?:-beta)?\b", "sankey", ("sankey", "sankey-beta")),
    DiagramSpec(DiagramType.PACKET, "packet", "PacketDocument", r"^\s*packet(?:-beta)?\b", "packet", ("packet", "packet-beta")),
    DiagramSpec(DiagramType.RADAR, "radar", "RadarDocument", r"^\s*radar(?:-beta)?\b", "radar", ("radar", "radar-beta")),
    DiagramSpec(DiagramType.BLOCK, "block", "BlockDocument", r"^\s*block(?:-beta)?\b", "block", ("block", "block-beta")),
    DiagramSpec(DiagramType.TREE_VIEW, "treeView", "TreeViewDocument", r"^\s*treeView(?:-beta)?\b", "tree-view", ("treeView", "treeView-beta")),
    DiagramSpec(DiagramType.ARCHITECTURE, "architecture", "ArchitectureDocument", r"^\s*architecture(?:-beta)?\b", "architecture", ("architecture", "architecture-beta")),
    DiagramSpec(DiagramType.EVENT_MODELING, "eventmodeling", "EventModelingDocument", r"^\s*eventmodeling(?:-beta)?\b", "eventmodeling", ("eventmodeling", "eventmodeling-beta")),
    DiagramSpec(DiagramType.ISHIKAWA, "ishikawa", "IshikawaDocument", r"^\s*ishikawa(?:-beta)?\b", "ishikawa", ("ishikawa", "ishikawa-beta")),
    DiagramSpec(DiagramType.VENN, "venn", "VennDocument", r"^\s*venn(?:-beta)?\b", "venn", ("venn", "venn-beta")),
    DiagramSpec(DiagramType.TREEMAP, "treemap", "TreemapDocument", r"^\s*treemap(?:-beta)?\b", "treemap", ("treemap", "treemap-beta")),
    DiagramSpec(DiagramType.WARDLEY, "wardley", "WardleyDocument", r"^\s*wardley(?:-beta)?\b", "wardley", ("wardley", "wardley-beta")),
    DiagramSpec(DiagramType.CYNEFIN, "cynefin", "CynefinDocument", r"^\s*cynefin(?:-beta)?\b", "cynefin", ("cynefin", "cynefin-beta")),
    DiagramSpec(DiagramType.RAILROAD, "railroad", "RailroadDocument", r"^\s*railroad(?:-beta)?\b", "railroad", ("railroad", "railroad-beta")),
    DiagramSpec(DiagramType.RAILROAD_EBNF, "railroad-ebnf", "RailroadEbnfDocument", r"^\s*railroad-ebnf\b", "railroad-ebnf", ("railroad-ebnf",)),
    DiagramSpec(DiagramType.RAILROAD_ABNF, "railroad-abnf", "RailroadAbnfDocument", r"^\s*railroad-abnf\b", "railroad-abnf", ("railroad-abnf",)),
    DiagramSpec(DiagramType.RAILROAD_PEG, "railroad-peg", "RailroadPegDocument", r"^\s*railroad-peg\b", "railroad-peg", ("railroad-peg",)),
    DiagramSpec(DiagramType.ZENUML, "zenuml", "ZenUMLDocument", r"^\s*zenuml\b", "zenuml", ("zenuml",)),
)

SPEC_BY_TYPE: Final[dict[DiagramType, DiagramSpec]] = {spec.diagram_type: spec for spec in CATALOG}
SPEC_BY_ID: Final[dict[str, DiagramSpec]] = {
    alias: spec
    for spec in CATALOG
    for alias in {spec.diagram_type.value, spec.internal_id}
}

# Legacy detector IDs are admitted aliases, not separate support tiers.
LEGACY_ALIASES: Final[Mapping[str, DiagramType]] = {
    "class": DiagramType.CLASS,
    "git": DiagramType.GIT_GRAPH,
    "state": DiagramType.STATE,
}


class MermaidToken(BaseModel):
    """One lossless non-whitespace token with a stable source span."""

    model_config = ConfigDict(frozen=True)

    kind: TokenKind
    value: str
    column_start: int = Field(ge=1)
    column_end: int = Field(ge=1)


class MermaidStatement(BaseModel):
    """One lossless source line with stable location and lexical kind."""

    model_config = ConfigDict(frozen=True)

    line: int = Field(ge=1)
    indent: int = Field(ge=0)
    kind: StatementKind
    text: str
    tokens: tuple[MermaidToken, ...] = ()


class MermaidDocument(BaseModel):
    """Lossless structured carrier shared by every registered diagram type."""

    model_config = ConfigDict(frozen=True)

    expected_type: ClassVar[DiagramType | None] = None

    type: DiagramType
    source: str
    header: str
    statements: tuple[MermaidStatement, ...]
    source_sha256: str

    @model_validator(mode="after")
    def validate_identity(self) -> MermaidDocument:
        """Bind class identity and content identity to the exact source."""
        if self.expected_type is not None and self.type != self.expected_type:
            msg = f"{type(self).__name__} requires type={self.expected_type.value}"
            raise ValueError(msg)
        expected_hash = hashlib.sha256(self.source.encode()).hexdigest()
        if self.source_sha256 != expected_hash:
            raise ValueError("source_sha256 does not identify source")
        return self


class DocumentDiff(BaseModel):
    """Deterministic source diff between two documents of the same type."""

    model_config = ConfigDict(frozen=True)

    diagram_type: DiagramType
    left_sha256: str
    right_sha256: str
    changed: bool
    unified_diff: tuple[str, ...]


class MergeResult(BaseModel):
    """Conflict-free three-way merge consequence."""

    model_config = ConfigDict(frozen=True)

    diagram_type: DiagramType
    source: str
    source_sha256: str
    selected: str


class DocumentError(ValueError):
    """Typed refusal raised before a document is admitted."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


HEADER_LINE = re.compile(r"^\s*(?!%%)(\S.*)$")
FRONTMATTER_BOUNDARY = re.compile(r"^\s*---\s*$")
TOKEN_PATTERN = re.compile(
    r"(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<number>-?\d+(?:\.\d+)?)"
    r"|(?P<operator><-->|-->|==>|-.->|--[ox]|<->|->|<-|--|::|\|[^\s|]+\||[=:])"
    r"|(?P<punctuation>[{}()\[\],;])"
    r"|(?P<identifier>[A-Za-z_][A-Za-z0-9_.-]*)"
    r"|(?P<text>\S)"
)


def _tokens(line: str) -> tuple[MermaidToken, ...]:
    """Lex one line into a total, lossless sequence of non-whitespace tokens."""
    result: list[MermaidToken] = []
    for match in TOKEN_PATTERN.finditer(line):
        group = match.lastgroup or "text"
        result.append(
            MermaidToken(
                kind=TokenKind(group),
                value=match.group(),
                column_start=match.start() + 1,
                column_end=match.end(),
            )
        )
    return tuple(result)


def _canonical_type(value: DiagramType | str) -> DiagramType:
    if isinstance(value, DiagramType):
        return value
    if value in LEGACY_ALIASES:
        return LEGACY_ALIASES[value]
    try:
        return DiagramType(value)
    except ValueError as exc:
        raise DocumentError("MMDIO-TYPE-001", f"unknown diagram type: {value}") from exc


def detect_document_type(source: str) -> DiagramType:
    """Detect a registered diagram type without an unsupported fallback."""
    if not isinstance(source, str) or not source.strip():
        raise DocumentError("MMDIO-DOC-001", "source is empty")

    text = _strip_frontmatter(source)
    # More-specific variants must win over base syntax.
    for spec in sorted(
        CATALOG,
        key=lambda item: (
            item.oracle_profile is OracleProfile.PROFILE,
            "-" in item.diagram_type.value,
            len(item.detect_pattern),
        ),
        reverse=True,
    ):
        if re.search(spec.detect_pattern, text, re.IGNORECASE | re.MULTILINE):
            return spec.diagram_type
    raise DocumentError("MMDIO-TYPE-002", "source does not match a registered diagram header")


def _strip_frontmatter(source: str) -> str:
    lines = source.splitlines()
    if not lines or not FRONTMATTER_BOUNDARY.match(lines[0]):
        return source
    for index in range(1, len(lines)):
        if FRONTMATTER_BOUNDARY.match(lines[index]):
            return "\n".join(lines[index + 1 :])
    raise DocumentError("MMDIO-DOC-002", "unterminated frontmatter")


def _header(source: str) -> str:
    body = _strip_frontmatter(source)
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("%%"):
            continue
        match = HEADER_LINE.match(line)
        if match:
            return match.group(1).strip()
    raise DocumentError("MMDIO-DOC-003", "diagram header is missing")


def _statements(source: str) -> tuple[MermaidStatement, ...]:
    result: list[MermaidStatement] = []
    seen_header = False
    in_frontmatter = False
    frontmatter_closed = False
    for number, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if number == 1 and FRONTMATTER_BOUNDARY.match(line):
            in_frontmatter = True
            result.append(MermaidStatement(line=number, indent=0, kind=StatementKind.DIRECTIVE, text=line, tokens=_tokens(line)))
            continue
        if in_frontmatter:
            result.append(MermaidStatement(line=number, indent=len(line) - len(line.lstrip()), kind=StatementKind.DIRECTIVE, text=line, tokens=_tokens(line)))
            if FRONTMATTER_BOUNDARY.match(line):
                in_frontmatter = False
                frontmatter_closed = True
            continue
        if not stripped:
            kind = StatementKind.BLANK
        elif stripped.startswith("%%{") or (frontmatter_closed and stripped == "---"):
            kind = StatementKind.DIRECTIVE
        elif stripped.startswith("%%"):
            kind = StatementKind.COMMENT
        elif not seen_header:
            kind = StatementKind.HEADER
            seen_header = True
        else:
            kind = StatementKind.STATEMENT
        result.append(
            MermaidStatement(
                line=number,
                indent=len(line) - len(line.lstrip()),
                kind=kind,
                text=line,
                tokens=_tokens(line),
            )
        )
    return tuple(result)


def canonicalize_source(source: str) -> str:
    """Normalize carrier trivia while preserving Mermaid statement semantics."""
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    if not lines:
        raise DocumentError("MMDIO-DOC-001", "source is empty")
    return "\n".join(lines) + "\n"


def parse_document(
    source: str,
    diagram_type: DiagramType | str | None = None,
) -> MermaidDocument:
    """Admit source into its exact generated document class."""
    canonical_source = canonicalize_source(source)
    detected = detect_document_type(canonical_source)
    admitted = detected if diagram_type is None else _canonical_type(diagram_type)
    if diagram_type is not None and detected != admitted:
        # Profile types intentionally lower to a native source syntax.
        profile = SPEC_BY_TYPE[admitted].oracle_profile is OracleProfile.PROFILE
        if not profile:
            raise DocumentError(
                "MMDIO-TYPE-003",
                f"declared type {admitted.value} conflicts with detected type {detected.value}",
            )
    from mmdio.engine.documents import DOCUMENT_CLASS_BY_TYPE

    document_class = DOCUMENT_CLASS_BY_TYPE[admitted]
    return document_class(
        type=admitted,
        source=canonical_source,
        header=_header(canonical_source),
        statements=_statements(canonical_source),
        source_sha256=hashlib.sha256(canonical_source.encode()).hexdigest(),
    )


def render_document(document: MermaidDocument) -> str:
    """Render a lossless document back to canonical Mermaid source."""
    return canonicalize_source(document.source)


def document_schema_for_type(diagram_type: DiagramType | str) -> dict[str, Any]:
    """Return the generated Pydantic schema for one of all 39 types."""
    from mmdio.engine.documents import DOCUMENT_CLASS_BY_TYPE

    return DOCUMENT_CLASS_BY_TYPE[_canonical_type(diagram_type)].model_json_schema()


def _receipt_payload(document: MermaidDocument) -> dict[str, Any]:
    return {
        "schema": "mmdio.document.receipt/v1",
        "diagram_type": str(document.type),
        "source_sha256": document.source_sha256,
        "statement_count": len(document.statements),
        "canonical_source": render_document(document),
    }


def issue_receipt(document: MermaidDocument) -> dict[str, Any]:
    """Issue a deterministic, replayable receipt for one canonical document."""
    payload = _receipt_payload(document)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {**payload, "receipt_sha256": hashlib.sha256(encoded).hexdigest()}


def verify_receipt(receipt: Mapping[str, Any]) -> MermaidDocument:
    """Verify identity and replay a document from its receipt carrier."""
    required = {
        "schema",
        "diagram_type",
        "source_sha256",
        "statement_count",
        "canonical_source",
        "receipt_sha256",
    }
    if missing := required.difference(receipt):
        raise DocumentError("MMDIO-RECEIPT-001", f"missing receipt fields: {sorted(missing)}")
    payload = {key: receipt[key] for key in required if key != "receipt_sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    expected = hashlib.sha256(encoded).hexdigest()
    if receipt["receipt_sha256"] != expected:
        raise DocumentError("MMDIO-RECEIPT-002", "receipt identity mismatch")
    document = parse_document(str(receipt["canonical_source"]), str(receipt["diagram_type"]))
    if document.source_sha256 != receipt["source_sha256"]:
        raise DocumentError("MMDIO-RECEIPT-003", "source identity mismatch")
    if len(document.statements) != receipt["statement_count"]:
        raise DocumentError("MMDIO-RECEIPT-004", "statement count mismatch")
    return document


def capability_records() -> list[dict[str, Any]]:
    """Return stable machine-readable records for all registered types."""
    return [
        {
            **asdict(spec),
            "diagram_type": spec.diagram_type.value,
            "oracle_profile": spec.oracle_profile.value,
            "accepted_js_types": list(spec.accepted_js_types),
        }
        for spec in CATALOG
    ]


def capability_json() -> str:
    """Serialize the exact capability manifest for the JavaScript oracle."""
    return json.dumps(capability_records(), sort_keys=True)


def parse_many(sources: Iterable[str]) -> tuple[MermaidDocument, ...]:
    """Parse multiple independent documents without cross-document state."""
    return tuple(parse_document(source) for source in sources)


def diff_documents(left: MermaidDocument, right: MermaidDocument) -> DocumentDiff:
    """Diff two exact document subjects without collapsing their type identity."""
    if left.type != right.type:
        raise DocumentError(
            "MMDIO-DIFF-001",
            f"cannot diff {left.type.value} against {right.type.value}",
        )
    lines = tuple(
        difflib.unified_diff(
            left.source.splitlines(keepends=True),
            right.source.splitlines(keepends=True),
            fromfile=f"left/{left.type.value}",
            tofile=f"right/{right.type.value}",
        )
    )
    return DocumentDiff(
        diagram_type=left.type,
        left_sha256=left.source_sha256,
        right_sha256=right.source_sha256,
        changed=left.source_sha256 != right.source_sha256,
        unified_diff=lines,
    )


def merge_documents(
    base: MermaidDocument,
    left: MermaidDocument,
    right: MermaidDocument,
) -> MergeResult:
    """Select the only conflict-free consequence of a bounded three-way merge."""
    if len({base.type, left.type, right.type}) != 1:
        raise DocumentError("MMDIO-MERGE-001", "all merge subjects must have the same type")
    if left.source == right.source:
        selected, document = "both", left
    elif left.source == base.source:
        selected, document = "right", right
    elif right.source == base.source:
        selected, document = "left", left
    else:
        raise DocumentError(
            "MMDIO-MERGE-002",
            "both branches changed the admitted source; explicit conflict resolution is required",
        )
    return MergeResult(
        diagram_type=document.type,
        source=document.source,
        source_sha256=document.source_sha256,
        selected=selected,
    )
