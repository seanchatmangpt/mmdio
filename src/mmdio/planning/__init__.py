"""Receipt-bearing Mermaid documentation for formal planning systems."""

from .bundle import PlanningDocumentationBundle, generate_planning_bundle
from .dfcm import (
    DFCM_CLAIM_CEILING,
    DFCM_SCHEMA,
    DFCMAxis,
    DFCMCandidate,
    DFCMCell,
    DFCMStatus,
    PlanningDFCMCorpus,
    PlanningDFCMMatrix,
    PROJECTION_CONTRACTS,
    enumerate_candidates,
    generate_dfcm_corpus,
    generate_planning_dfcm,
)
from .formalisms import PROFILES, FormalismProfile, normalize_formalism
from .io import write_planning_bundle
from .jsonio import load_planning_graph, planning_graph_from_dict, planning_graph_from_json
from .model import (
    PlanningEdge,
    PlanningEdgeKind,
    PlanningGraph,
    PlanningNode,
    PlanningNodeKind,
    graph,
)
from .projections import PlanningDocument, generate_planning_documents
from .receipts import CLAIM_CEILING, PlanningDocumentReceipt, receipt_for, verify_receipt

__all__ = [
    "CLAIM_CEILING",
    "DFCM_CLAIM_CEILING",
    "DFCM_SCHEMA",
    "DFCMAxis",
    "DFCMCandidate",
    "DFCMCell",
    "DFCMStatus",
    "PROFILES",
    "PROJECTION_CONTRACTS",
    "FormalismProfile",
    "PlanningDFCMCorpus",
    "PlanningDFCMMatrix",
    "PlanningDocument",
    "PlanningDocumentationBundle",
    "PlanningDocumentReceipt",
    "PlanningEdge",
    "PlanningEdgeKind",
    "PlanningGraph",
    "PlanningNode",
    "PlanningNodeKind",
    "enumerate_candidates",
    "generate_dfcm_corpus",
    "generate_planning_bundle",
    "generate_planning_dfcm",
    "generate_planning_documents",
    "graph",
    "load_planning_graph",
    "normalize_formalism",
    "planning_graph_from_dict",
    "planning_graph_from_json",
    "receipt_for",
    "verify_receipt",
    "write_planning_bundle",
]
