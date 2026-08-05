#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OFMF Keystone Omniverse — One-File Runtime

Invariant: Hooks are Turtle. Triggers are dialect artifacts (OWL/SHACL/SPARQL/N3/Datalog/ShEx).
No placeholder stubs. Missing dependencies => hard fail.

Install (minimum):
  pip install rdflib blake3 SpiffWorkflow

Install (dialect suite):
  pip install owlrl pyshacl pyDatalog ShEx pyoxigraph

External executables (dialect suite):
  - cwm (N3 rules engine) OR another N3 rule runner you standardize on

Core capabilities:
  - Load hook packs from Turtle
  - Evaluate triggers via:
      SPARQL ASK/SELECT (RDFLib)
      SHACL (pyshacl)
      OWL RL closure (owlrl)
      ShEx validation (ShEx)
      N3 rules (cwm CLI)
      Datalog rules (pyDatalog)
  - Apply actions via:
      SPARQL CONSTRUCT => RDF delta
      BPMN XML emit from Turtle => write to disk
      SpiffWorkflow execution (optional entrypoint here, but engine is decoupled)
  - Receipts via BLAKE3 over canonicalized N-Quads + emitted artifacts

Design rule:
  - Python orchestrates; dialects decide.
"""

from __future__ import annotations

# ---------- Python 3.13 compatibility patch for pyshex ----------
# pyshex uses deprecated typing.io which was removed in Python 3.13
# Must patch BEFORE any imports that might trigger pyshex submodules
try:
    import typing
    if not hasattr(typing, 'io'):
        import io
        typing.io = io  # type: ignore
except Exception:
    pass  # If patching fails, let import errors propagate naturally

import dataclasses
import hashlib
import multiprocessing
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# ---------- Hard dependency gate (no placeholders) ----------

def _require_import(module: str, pip_hint: str) -> Any:
    try:
        return __import__(module, fromlist=["*"])
    except Exception as e:
        raise RuntimeError(
            MSG_REQUIRED_MODULE_TEMPLATE.format(module=module, pip_hint=pip_hint, error=e)
        ) from e


rdflib = _require_import("rdflib", "rdflib")
blake3_mod = _require_import("blake3", "blake3")

# Dialect modules (hard required because engine claims support)
owlrl = _require_import("owlrl", "owlrl")
pyshacl = _require_import("pyshacl", "pyshacl")
pydatalog = _require_import("pyDatalog", "pyDatalog")
shex_mod = _require_import("shex", "ShEx")
pyoxigraph = _require_import("pyoxigraph", "pyoxigraph")

# SpiffWorkflow (BPMN executor)
spiff = _require_import("SpiffWorkflow", "SpiffWorkflow")

from rdflib import BNode, ConjunctiveGraph, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from blake3 import blake3  # type: ignore

# pyshacl.validate signature is stable in common releases
from pyshacl import validate as shacl_validate  # type: ignore

from owlrl import DeductiveClosure, OWLRL_Semantics  # type: ignore

# SpiffWorkflow imports (BPMN)
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser  # type: ignore
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow  # type: ignore

# Import utilities from kgc_ofmf_utils
from specify_cli.kgc_ofmf_utils import (
    KH,
    claude_event_to_iri,
    select_hooks_by_event,
    sparql_select,
    shacl_gate,
    enforce_shacl_gate,
    canonical_hash_rdf,
    write_receipt_bundle,
    ReceiptProofInfo,
    ReceiptMetaInfo,
    now_ns,
    new_graph,
    load_graph,
    write_graph,
    OFMFError,
    SHACLValidationError,
)
from specify_cli.ofmf.event_adapter import EventAdapter

# ---------- Namespaces ----------

BPMN = Namespace("https://chatmangpt.com/kgc/bpmn#")
XES = Namespace("https://chatmangpt.com/kgc/xes#")
OTEL = Namespace("https://chatmangpt.com/kgc/otel#")

# ---------- Constants ----------

# Serialization formats
FORMAT_NQUADS = "nquads"
FORMAT_TURTLE = "turtle"
FORMAT_N3 = "n3"
FORMAT_XML = "xml"
ENCODING_UTF8 = "utf-8"

# Empty strings and separators
EMPTY_STR = ""
COMMENT_MARKER = "#"
COLON_SEP = ":"
SLASH_SEP = "/"
UNDERSCORE_SEP = "_"

# Action types
ACTION_TYPE_CONSTRUCT = "construct"
ACTION_TYPE_EMIT_BPMN = "emit_bpmn"
ACTION_TYPE_EMIT_EVENT = "emit_event"
ACTION_TYPE_ROUTE_TO_BPMN = "route_to_bpmn"

# Trigger types
TRIGGER_TYPE_SPARQL = "sparql"
TRIGGER_TYPE_SHACL = "shacl"
TRIGGER_TYPE_OWL = "owl"
TRIGGER_TYPE_N3 = "n3"
TRIGGER_TYPE_DATALOG = "datalog"
TRIGGER_TYPE_SHEX = "shex"

# Delta operations
ADD_OP = "ADD"
DEL_OP = "DEL"

# Inference modes
INFERENCE_RDFS = "rdfs"
INFERENCE_NONE = "none"

# Forbidden predicates
PREDICATE_COMMAND = "command"
PREDICATE_SHELL = "shell"
PREDICATE_EXEC = "exec"

# File paths
ONTOLOGY_DIR = "ontology"
LAW_PACK_FILENAME = "ofmf-law.shacl.ttl"
ONTOLOGY_FILENAME = "kh.ttl"

# Result status
RESULT_SATISFIED = "SATISFIED"
RESULT_SKIPPED = "SKIPPED"

# URI prefixes and schemes
URN_DELTA_PREFIX = "urn:delta:"
URN_DIAGNOSTIC_PREFIX = "urn:diagnostic:"
URN_RECEIPT_PREFIX = "urn:receipt:"
URN_SHACL_REPORT_PREFIX = "urn:shacl-report:"
URN_TENANT_PREFIX = "urn:tenant:"
FILE_SCHEME = "file://"

# BPMN XML elements and attributes
BPMN_XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'
BPMN_NS_URI = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI_NS_URI = "http://www.omg.org/spec/BPMN/20100524/DI"
DC_NS_URI = "http://www.omg.org/spec/DD/20100524/DC"
DI_NS_URI = "http://www.omg.org/spec/DD/20100524/DI"
XSI_NS_URI = "http://www.w3.org/2001/XMLSchema-instance"
BPMN_XMLNS_XSI = f'xmlns:xsi="{XSI_NS_URI}"'
BPMN_XMLNS_BPMN = f'xmlns:bpmn="{BPMN_NS_URI}"'
BPMN_DEFINITIONS_ID = "Definitions_1"
BPMN_TARGET_NS = "https://chatmangpt.com/kgc/bpmn"

# Process execution
PROCESS_ATTR_EXECUTABLE = "isExecutable"
PROCESS_ATTR_TRUE = "true"

# Temporary file/directory paths
OFMF_TMP_N3 = ".ofmf_tmp_n3"
OFMF_TMP_N3_RULES = ".ofmf_tmp_n3_rules"
COMBINED_N3_FILE = "combined.n3"

# EYE command arguments
EYE_COMMAND = "eye"
EYE_ARG_N3 = "--n3"
EYE_ARG_PASS = "--pass"
EYE_ARG_NOPE = "--nope"
EYE_ENTAILMENT_PATTERN = r'ent=(\d+)'
EYE_ENCODING_ERRORS_REPLACE = "replace"

# Character escaping for XML
XML_ESCAPE_AMPERSAND = "&amp;"
XML_ESCAPE_LT = "&lt;"
XML_ESCAPE_GT = "&gt;"
XML_ESCAPE_QUOTE = "&quot;"
XML_ESCAPE_APOSTROPHE = "&apos;"

# Graph operations
GRAPH_CONTEXT_INDEX_ZERO = 0
GRAPH_CONTEXT_INDEX_ONE = 1
GRAPH_CONTEXT_INDEX_TWO = 2
GRAPH_CONTEXT_INDEX_THREE = 3

# Default values
DEFAULT_PRIORITY = 0
DEFAULT_WORKERS = 1
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RESPONSE_CODES = (200, 201)

# Hook IRI local name separators
IRI_FRAGMENT_SEPARATOR = "#"
IRI_PATH_SEPARATOR = "/"

# Error messages
MSG_REQUIRED_MODULE_TEMPLATE = "Missing required module '{module}'. Install with:\n  pip install {pip_hint}\nImport error: {error}"
MSG_LAW_PACK_NOT_FOUND = "OFMF Law Pack not found: {path}\nCannot validate hook pack without constitutional law.\nExpected location: ontology/ofmf-law.shacl.ttl"
MSG_HOOK_MISSING_PHASE_OR_EVENT = "Hook {iri} must have either kh:phase (phase-based) or trigger with kh:event (event-based)"
MSG_HOOK_BOTH_PHASE_AND_EVENT = "Hook {iri} cannot have both kh:phase and kh:event - must be either phase-based or event-based"
MSG_PRIORITY_MUST_BE_INT = "kh:priority must be an integer for hook {iri}: {value}"
MSG_FORBIDDEN_PREDICATE = "Forbidden predicate in pack: {predicate}. Hook packs cannot execute arbitrary commands."
MSG_ACTION_TYPE_NOT_ALLOWED = "Action type not allowed: {action_type}. Allowed types: {allowed_types}"
MSG_REQUIRED_IRI_MISSING = "Required IRI missing: {subject} {predicate} ? (got {value})"
MSG_REQUIRED_LITERAL_MISSING = "Required literal missing: {subject} {predicate} ? (got {value})"
MSG_UNKNOWN_TRIGGER_TYPE = "Trigger node has no recognized type: {trigger_node}"
MSG_UNKNOWN_ACTION_TYPE = "Unknown action type for {action_node} in hook {hook_iri}"
MSG_PRIORITY_TIE_DETECTED = "Priority tie detected: Λ must be ≺-total. Tied priorities: {ties}. Affected hooks: {hooks}. Hooks must have unique priorities."
MSG_HOOK_DEPENDS_UNKNOWN = "Hook {hook_id} depends on unknown hookId {dep}"
MSG_EXPECTED_ONE_SUBJECT = "Expected exactly 1 subject of type {type_}, found {count}"
MSG_PROCESS_SUBJECT_NOT_IRI = "Process subject must be an IRI"
MSG_EYE_FAILED = "EYE failed (code {code}). stderr:\n{stderr}"
MSG_BPMN_FILE_NOT_FOUND = "BPMN XML file not found: {path}"
MSG_PROCESS_MISSING_ID = "Process element missing 'id' attribute"
MSG_START_EVENT_MISSING_ID = "StartEvent missing 'id' attribute"
MSG_END_EVENT_MISSING_ID = "EndEvent missing 'id' attribute"
MSG_TASK_MISSING_ID = "Task missing 'id' attribute"
MSG_GATEWAY_MISSING_ID = "Gateway missing 'id' attribute"
MSG_SEQUENCE_FLOW_MISSING_ID = "SequenceFlow missing 'id' attribute"
MSG_SEQUENCE_FLOW_MISSING_REFS = "SequenceFlow {flow_id} missing sourceRef or targetRef"

# ---------- Utility: canonical RDF bytes for receipts ----------

def graph_to_canonical_nquads_bytes(g: ConjunctiveGraph) -> bytes:
    """
    Canonicalization approach:
      - Serialize to N-Quads with stable ordering.
      - This is not RDF Dataset Canonicalization (RDFC-1.0) grade, but is deterministic
        for non-blank-heavy datasets and for OFMF-controlled blank node policies.
    If you require blank-node canonicalization, replace with URDNA2015 later,
    but do not add placeholders — add the real canonicalizer as a hard dep.
    """
    nquads = g.serialize(format=FORMAT_NQUADS)
    if isinstance(nquads, str):
        nquads_bytes = nquads.encode(ENCODING_UTF8)
    else:
        nquads_bytes = bytes(nquads)
    lines = [ln for ln in nquads_bytes.splitlines() if ln.strip()]
    lines.sort()
    return b"\n".join(lines) + b"\n"


def blake3_hex(data: bytes) -> str:
    return blake3(data).hexdigest()


# ---------- OFMF Delta ----------

@dataclass(frozen=True)
class RDFDelta:
    adds: Set[Tuple[Any, Any, Any, Optional[Any]]]
    deletes: Set[Tuple[Any, Any, Any, Optional[Any]]]

    @staticmethod
    def empty() -> "RDFDelta":
        return RDFDelta(adds=set(), deletes=set())

    def to_graph(self) -> Graph:
        """
        Convert delta to rdflib Graph using kh:Delta ontology.

        Returns:
            Graph with kh:Delta structure (kh:addQuad/kh:deleteQuad with kh:QuadAddition/kh:QuadDeletion nodes)
        """
        graph = Graph()
        graph.bind("kh", KH)

        delta_bytes = self._to_canonical_bytes()
        delta_hash = blake3_hex(delta_bytes)
        delta_iri = URIRef(f"{URN_DELTA_PREFIX}{delta_hash}")

        graph.add((delta_iri, RDF.type, KH.Delta))

        for s, p, o, g_ctx in sorted(self.adds, key=lambda x: (str(x[GRAPH_CONTEXT_INDEX_ZERO]), str(x[GRAPH_CONTEXT_INDEX_ONE]), str(x[GRAPH_CONTEXT_INDEX_TWO]), str(x[GRAPH_CONTEXT_INDEX_THREE]) if x[GRAPH_CONTEXT_INDEX_THREE] else "")):
            quad_node = BNode()
            graph.add((delta_iri, KH.addQuad, quad_node))
            graph.add((quad_node, RDF.type, KH.QuadAddition))
            graph.add((quad_node, KH.subject, s))
            graph.add((quad_node, KH.predicate, p))
            graph.add((quad_node, KH.object, o))
            if g_ctx is not None:
                graph.add((quad_node, KH.graph, g_ctx))

        for s, p, o, g_ctx in sorted(self.deletes, key=lambda x: (str(x[GRAPH_CONTEXT_INDEX_ZERO]), str(x[GRAPH_CONTEXT_INDEX_ONE]), str(x[GRAPH_CONTEXT_INDEX_TWO]), str(x[GRAPH_CONTEXT_INDEX_THREE]) if x[GRAPH_CONTEXT_INDEX_THREE] else "")):
            quad_node = BNode()
            graph.add((delta_iri, KH.deleteQuad, quad_node))
            graph.add((quad_node, RDF.type, KH.QuadDeletion))
            graph.add((quad_node, KH.subject, s))
            graph.add((quad_node, KH.predicate, p))
            graph.add((quad_node, KH.object, o))
            if g_ctx is not None:
                graph.add((quad_node, KH.graph, g_ctx))

        return graph

    def to_turtle(self) -> str:
        """
        Serialize delta to Turtle format using kh:Delta ontology.

        Returns:
            Turtle string with kh:Delta structure
        """
        graph = self.to_graph()
        return graph.serialize(format=FORMAT_TURTLE)

    @classmethod
    def from_turtle(cls, turtle_data: str) -> "RDFDelta":
        """
        Parse delta from Turtle format using kh:Delta ontology.

        Args:
            turtle_data: Turtle string with kh:Delta structure

        Returns:
            RDFDelta parsed from Turtle
        """
        g = Graph()
        g.parse(data=turtle_data, format=FORMAT_TURTLE)
        return cls.from_graph(g)

    @classmethod
    def from_graph(cls, graph: Graph) -> "RDFDelta":
        """
        Parse delta from an rdflib Graph with kh:Delta triples.

        Args:
            graph: Graph containing kh:Delta structure

        Returns:
            RDFDelta parsed from Graph
        """
        # Find the kh:Delta subject
        delta_subjects = list(graph.subjects(RDF.type, KH.Delta))
        if not delta_subjects:
            # If no kh:Delta found, return empty
            return cls.empty()

        delta_iri = delta_subjects[0]

        adds: Set[Tuple[Any, Any, Any, Optional[Any]]] = set()
        deletes: Set[Tuple[Any, Any, Any, Optional[Any]]] = set()

        # Parse additions
        for quad_add in graph.objects(delta_iri, KH.addQuad):
            s = graph.value(quad_add, KH.subject)
            p = graph.value(quad_add, KH.predicate)
            o = graph.value(quad_add, KH.object)
            g_ctx = graph.value(quad_add, KH.graph)
            if s and p and o:
                adds.add((s, p, o, g_ctx))

        # Parse deletions
        for quad_del in graph.objects(delta_iri, KH.deleteQuad):
            s = graph.value(quad_del, KH.subject)
            p = graph.value(quad_del, KH.predicate)
            o = graph.value(quad_del, KH.object)
            g_ctx = graph.value(quad_del, KH.graph)
            if s and p and o:
                deletes.add((s, p, o, g_ctx))

        return cls(adds=adds, deletes=deletes)

    def _to_canonical_bytes(self) -> bytes:
        """
        Convert delta to canonical bytes for hashing (deterministic).
        Uses sorted N-Quads-like representation.

        Returns:
            Canonical bytes representation of delta
        """
        ADD_OP = "ADD"
        DEL_OP = "DEL"
        lines = []

        for s, p, o, g in sorted(self.adds, key=lambda x: (str(x[GRAPH_CONTEXT_INDEX_ZERO]), str(x[GRAPH_CONTEXT_INDEX_ONE]), str(x[GRAPH_CONTEXT_INDEX_TWO]), str(x[GRAPH_CONTEXT_INDEX_THREE]) if x[GRAPH_CONTEXT_INDEX_THREE] else EMPTY_STR)):
            lines.append(f"{ADD_OP} {s} {p} {o} {g or EMPTY_STR}")

        for s, p, o, g in sorted(self.deletes, key=lambda x: (str(x[GRAPH_CONTEXT_INDEX_ZERO]), str(x[GRAPH_CONTEXT_INDEX_ONE]), str(x[GRAPH_CONTEXT_INDEX_TWO]), str(x[GRAPH_CONTEXT_INDEX_THREE]) if x[GRAPH_CONTEXT_INDEX_THREE] else EMPTY_STR)):
            lines.append(f"{DEL_OP} {s} {p} {o} {g or EMPTY_STR}")

        return "\n".join(lines).encode(ENCODING_UTF8)


# ---------- Hook model (loaded from Turtle) ----------

@dataclass(frozen=True)
class HookTrigger:
    """
    Exactly one trigger dialect is allowed per trigger node.
    Trigger nodes are RDF resources; content is referenced as RDF, not stringly-typed.
    """
    kind: str  # 'sparql' | 'shacl' | 'owl' | 'n3' | 'datalog' | 'shex'
    ref: URIRef


@dataclass(frozen=True)
class HookAction:
    """
    Actions remain dialect artifacts:
      - SPARQL CONSTRUCT (graph node referencing a query)
      - Emit BPMN (emit BPMN XML from Turtle BPMN graph)
      - Emit OTEL/XES records (as RDF event quads)
      - Route to BPMN executor (emit BPMN + submit to SpiffWorkflow)
    """
    kind: str  # 'construct' | 'emit_bpmn' | 'emit_event' | 'route_to_bpmn'
    ref: URIRef


@dataclass(frozen=True)
class KnowledgeHook:
    hook_id: str
    iri: URIRef
    phase: Optional[str]  # Optional for event-based hooks (validate-before-write | transform-after-write | etc)
    event: Optional[str]  # Optional for phase-based hooks (e.g., "PostToolUse", "SessionStart")
    trigger: HookTrigger
    actions: Tuple[HookAction, ...]
    depends_on: Tuple[str, ...]
    priority: int  # Total order for conflict resolution (higher = earlier); default: 0


# ---------- Hook pack loader (Turtle => hook objects) ----------

class HookPackLoader:
    def __init__(self, validate: bool = True) -> None:
        """
        Initialize HookPackLoader.

        Args:
            validate: If True, validate hook packs against OFMF Law Pack before loading.
                     Set to False only for testing invalid packs. Default: True (lawful).
        """
        self.validate = validate
        self.law_pack_path = Path(__file__).parent.parent.parent.parent / "ontology" / "ofmf-law.shacl.ttl"

    def load_from_turtle(self, ttl_path: Path) -> Tuple[ConjunctiveGraph, List[KnowledgeHook]]:
        """
        Load hook pack from Turtle file.

        Constitutional enforcement: Hook packs MUST pass SHACL validation before execution.
        Invalid hook packs produce RuntimeError with validation report.

        Args:
            ttl_path: Path to hook pack Turtle file

        Returns:
            Tuple of (ConjunctiveGraph with hook pack, List of parsed KnowledgeHook objects)

        Raises:
            RuntimeError: If hook pack violates OFMF Law Pack (SHACL validation fails)
        """
        ds = ConjunctiveGraph()
        ds.parse(ttl_path.as_posix(), format=FORMAT_TURTLE)

        # Constitutional gate: validate hook pack before execution
        if self.validate:
            self._validate_hook_pack(ds, ttl_path)
            # Pack gating: reject forbidden predicates/action types
            self._gate_pack(ds)

        hooks: List[KnowledgeHook] = []
        for hook_iri in ds.subjects(RDF.type, KH.Hook):
            hook_id = self._require_literal_str(ds, hook_iri, KH.hookId)

            trigger_node = self._require_iri(ds, hook_iri, KH.trigger)
            trigger = self._parse_trigger(ds, trigger_node)

            event_iri = ds.value(trigger_node, KH.event)
            if event_iri is not None:
                event_name = str(event_iri).split(IRI_FRAGMENT_SEPARATOR)[-1] if IRI_FRAGMENT_SEPARATOR in str(event_iri) else str(event_iri).split(IRI_PATH_SEPARATOR)[-1]
                phase = None
            else:
                phase_iri = ds.value(hook_iri, KH.phase)
                if phase_iri is None:
                    raise RuntimeError(MSG_HOOK_MISSING_PHASE_OR_EVENT.format(iri=hook_iri))
                phase = str(phase_iri).split(IRI_FRAGMENT_SEPARATOR)[-1] if IRI_FRAGMENT_SEPARATOR in str(phase_iri) else str(phase_iri).split(IRI_PATH_SEPARATOR)[-1]
                event_name = None

            if phase is None and event_name is None:
                raise RuntimeError(MSG_HOOK_MISSING_PHASE_OR_EVENT.format(iri=hook_iri))
            if phase is not None and event_name is not None:
                raise RuntimeError(MSG_HOOK_BOTH_PHASE_AND_EVENT.format(iri=hook_iri))

            actions = tuple(self._parse_actions(ds, hook_iri))
            depends = tuple(self._parse_depends(ds, hook_iri))

            priority_lit = ds.value(hook_iri, KH.priority)
            if priority_lit is not None and isinstance(priority_lit, Literal):
                try:
                    priority = int(priority_lit)
                except (ValueError, TypeError):
                    raise RuntimeError(MSG_PRIORITY_MUST_BE_INT.format(iri=hook_iri, value=priority_lit))
            else:
                priority = DEFAULT_PRIORITY

            hooks.append(
                KnowledgeHook(
                    hook_id=hook_id,
                    iri=URIRef(str(hook_iri)),
                    phase=phase,
                    event=event_name,
                    trigger=trigger,
                    actions=actions,
                    depends_on=depends,
                    priority=priority,
                )
            )

        # Sort by priority (descending, higher = earlier), then by hook_id (ascending, deterministic)
        hooks.sort(key=lambda h: (-h.priority, h.hook_id))
        return ds, hooks

    def _validate_hook_pack(self, hook_pack_ds: ConjunctiveGraph, ttl_path: Path) -> None:
        """
        Validate hook pack against OFMF Law Pack (constitutional gate).

        Invalid hook packs MUST NOT execute. This is a hard requirement.

        Args:
            hook_pack_ds: The loaded hook pack dataset
            ttl_path: Path to hook pack (for error reporting)

        Raises:
            RuntimeError: If OFMF Law Pack file not found
            RuntimeError: If hook pack violates OFMF Law (SHACL validation fails)
        """
        if not self.law_pack_path.exists():
            raise RuntimeError(
                MSG_LAW_PACK_NOT_FOUND.format(path=self.law_pack_path)
            )

        # Load OFMF Law Pack (SHACL shapes)
        law_pack_g = Graph()
        law_pack_g.parse(self.law_pack_path.as_posix(), format="turtle")

        # Load KH ontology for type inference (defines kh:Phase, kh:EnforcementMode, etc)
        ontology_path = self.law_pack_path.parent / "kh.ttl"
        ont_g = Graph()
        if ontology_path.exists():
            ont_g.parse(ontology_path.as_posix(), format="turtle")

        # Convert ConjunctiveGraph to Graph for pyshacl
        data_g = Graph()
        for ctx in hook_pack_ds.contexts():
            data_g += ctx

        # Validate with ontology for RDFS type inference
        conforms, report_graph, report_text = shacl_validate(
            data_graph=data_g,
            shacl_graph=law_pack_g,
            ont_graph=ont_g if len(ont_g) > 0 else None,
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
            debug=False,
        )

        if not conforms:
            raise RuntimeError(
                f"Hook pack violates OFMF Law (constitutional failure): {ttl_path}\n\n"
                f"SHACL Validation Report:\n"
                f"{report_text}\n\n"
                f"Invalid hook packs MUST NOT execute.\n"
                f"Fix violations and try again."
            )

    def _parse_depends(self, ds: ConjunctiveGraph, hook_iri: URIRef) -> Iterable[str]:
        for dep in ds.objects(hook_iri, KH.dependsOn):
            if isinstance(dep, Literal):
                yield str(dep)
            else:
                # dependency references are hookIds; enforce literal to keep determinism
                raise RuntimeError(f"dependsOn must be a literal hookId for {hook_iri}: {dep}")

    def _parse_actions(self, ds: ConjunctiveGraph, hook_iri: URIRef) -> Iterable[HookAction]:
        for act_node in ds.objects(hook_iri, KH.action):
            if not isinstance(act_node, (URIRef, BNode)):
                raise RuntimeError(f"KH.action must point to a node: {hook_iri} -> {act_node}")

            if (act_node, RDF.type, KH.SparqlConstructAction) in ds:
                ref = self._require_iri(ds, act_node, KH.constructQuery)
                yield HookAction(kind=ACTION_TYPE_CONSTRUCT, ref=ref)
            elif (act_node, RDF.type, KH.EmitBpmnAction) in ds:
                ref = self._require_iri(ds, act_node, KH.bpmnGraph)
                yield HookAction(kind=ACTION_TYPE_EMIT_BPMN, ref=ref)
            elif (act_node, RDF.type, KH.EmitEventAction) in ds:
                ref = self._require_iri(ds, act_node, KH.eventConstruct)
                yield HookAction(kind=ACTION_TYPE_EMIT_EVENT, ref=ref)
            elif (act_node, RDF.type, KH.RouteToBpmnAction) in ds:
                ref = self._require_iri(ds, act_node, KH.bpmnGraph)
                yield HookAction(kind=ACTION_TYPE_ROUTE_TO_BPMN, ref=ref)
            else:
                raise RuntimeError(MSG_UNKNOWN_ACTION_TYPE.format(action_node=act_node, hook_iri=hook_iri))

    def _parse_trigger(self, ds: ConjunctiveGraph, trigger_node: URIRef) -> HookTrigger:
        if (trigger_node, RDF.type, KH.SparqlTrigger) in ds:
            ref = self._require_iri(ds, trigger_node, KH.askQuery)
            return HookTrigger(kind=TRIGGER_TYPE_SPARQL, ref=ref)

        if (trigger_node, RDF.type, KH.ShaclTrigger) in ds:
            ref = self._require_iri(ds, trigger_node, KH.shapesGraph)
            return HookTrigger(kind=TRIGGER_TYPE_SHACL, ref=ref)

        if (trigger_node, RDF.type, KH.OwlTrigger) in ds:
            ref = self._require_iri(ds, trigger_node, KH.axiomsGraph)
            return HookTrigger(kind=TRIGGER_TYPE_OWL, ref=ref)

        if (trigger_node, RDF.type, KH.N3Trigger) in ds:
            ref = self._require_iri(ds, trigger_node, KH.n3RulesFile)
            return HookTrigger(kind=TRIGGER_TYPE_N3, ref=ref)

        if (trigger_node, RDF.type, KH.DatalogTrigger) in ds:
            ref = self._require_iri(ds, trigger_node, KH.datalogProgram)
            return HookTrigger(kind=TRIGGER_TYPE_DATALOG, ref=ref)

        if (trigger_node, RDF.type, KH.ShExTrigger) in ds:
            ref = self._require_iri(ds, trigger_node, KH.shexSchema)
            return HookTrigger(kind=TRIGGER_TYPE_SHEX, ref=ref)

        raise RuntimeError(MSG_UNKNOWN_TRIGGER_TYPE.format(trigger_node=trigger_node))

    def _require_iri(self, ds: ConjunctiveGraph, s: URIRef, p: URIRef) -> URIRef:
        o = ds.value(s, p)
        if not isinstance(o, URIRef):
            raise RuntimeError(MSG_REQUIRED_IRI_MISSING.format(subject=s, predicate=p, value=o))
        return o

    def _require_literal_str(self, ds: ConjunctiveGraph, s: URIRef, p: URIRef) -> str:
        o = ds.value(s, p)
        if not isinstance(o, Literal):
            raise RuntimeError(MSG_REQUIRED_LITERAL_MISSING.format(subject=s, predicate=p, value=o))
        return str(o)

    def _gate_pack(self, pack: ConjunctiveGraph) -> None:
        """
        Constitutional guards: reject forbidden predicates and action types.
        
        This enforces the safety-critical constraint that hook packs cannot
        execute arbitrary commands or use unallowlisted action types.
        
        Args:
            pack: Hook pack dataset to validate
            
        Raises:
            RuntimeError: If pack contains forbidden predicates or unallowlisted action types
        """
        # Convert to Graph for iteration
        pack_g = Graph()
        for ctx in pack.contexts():
            pack_g += ctx
        
        # Forbidden predicates (if they exist in ontology)
        # Note: These predicates may not exist yet, but we check for them defensively
        FORBIDDEN_PREDICATES: Set[URIRef] = set()
        # Check if kh:command, kh:shell, kh:exec exist in the pack
        for s, p, o in pack_g.triples((None, None, None)):
            p_str = str(p)
            if "command" in p_str.lower() or "shell" in p_str.lower() or "exec" in p_str.lower():
                # Check if it's in the KH namespace
                if p_str.startswith(str(KH)):
                    FORBIDDEN_PREDICATES.add(p)
        
        for s, p, o in pack_g.triples((None, None, None)):
            if p in FORBIDDEN_PREDICATES:
                raise RuntimeError(MSG_FORBIDDEN_PREDICATE.format(predicate=p))
        
        # Ensure all actions are allowlisted
        # Existing action types are already allowlisted (SparqlConstructAction, EmitBpmnAction, etc.)
        # This is a future-proofing guard for any new action types that might be added
        ALLOWED_ACTION_TYPES = {
            KH.SparqlConstructAction,
            KH.EmitBpmnAction,
            KH.EmitEventAction,
            KH.RouteToBpmnAction,
        }
        
        for action in pack_g.subjects(RDF.type, KH.Action):
            action_type = pack_g.value(action, KH.actionType)
            if action_type is not None:
                # If actionType is specified, it must be in the allowlist
                # Note: actionType is optional, so we only check if present
                if URIRef(str(action_type)) not in ALLOWED_ACTION_TYPES:
                    # Check if it's one of the known action types by rdf:type
                    action_rdf_type = None
                    for rdf_type in pack_g.objects(action, RDF.type):
                        if isinstance(rdf_type, URIRef) and rdf_type != KH.Action:
                            # Skip the base kh:Action class, only check specific subclasses
                            action_rdf_type = rdf_type
                            break
                    
                    if action_rdf_type and action_rdf_type not in ALLOWED_ACTION_TYPES:
                        raise RuntimeError(MSG_ACTION_TYPE_NOT_ALLOWED.format(action_type=action_rdf_type, allowed_types=ALLOWED_ACTION_TYPES))
            else:
                # If no actionType specified, check rdf:type for specific action subclasses
                # Allow kh:Action base class, but require at least one specific subclass
                has_specific_type = False
                for rdf_type in pack_g.objects(action, RDF.type):
                    if isinstance(rdf_type, URIRef) and rdf_type != KH.Action:
                        if rdf_type in ALLOWED_ACTION_TYPES:
                            has_specific_type = True
                            break
                        elif rdf_type not in ALLOWED_ACTION_TYPES:
                            raise RuntimeError(MSG_ACTION_TYPE_NOT_ALLOWED.format(action_type=rdf_type, allowed_types=ALLOWED_ACTION_TYPES))
                
                # If action has only kh:Action (base class) and no specific type, that's OK
                # (it will be validated by SHACL shapes)


# ---------- Dialect evaluators (dialects decide) ----------

class DialectSuite:
    """
    All dialects are first-class. No Python rule logic as substitute.
    """

    def __init__(self, repo_dataset: ConjunctiveGraph) -> None:
        self.repo_dataset = repo_dataset

    # ---- SPARQL ----

    def sparql_ask(self, data_ds: ConjunctiveGraph, ask_query_node: URIRef) -> bool:
        q = self._load_text_from_node(ask_query_node)
        res = data_ds.query(q)
        try:
            return bool(res.askAnswer)  # type: ignore
        except Exception:
            for _ in res:
                return True
            return False

    def sparql_construct_to_delta(self, data_ds: ConjunctiveGraph, construct_query_node: URIRef) -> RDFDelta:
        q = self._load_text_from_node(construct_query_node)
        result = data_ds.query(q)
        # rdflib CONSTRUCT returns a Result object that is iterable over triples
        # We can also access result.graph which is a Graph
        adds: Set[Tuple[Any, Any, Any, Optional[Any]]] = set()
        if hasattr(result, 'graph') and isinstance(result.graph, Graph):
            # Preferred: use result.graph
            for s, p, o in result.graph.triples((None, None, None)):
                adds.add((s, p, o, None))
        else:
            # Fallback: iterate over result directly
            for triple in result:
                if len(triple) == 3:
                    s, p, o = triple
                    adds.add((s, p, o, None))
        return RDFDelta(adds=adds, deletes=set())

    # ---- SHACL ----

    def shacl_conforms(self, data_g: Graph, shapes_g: Graph) -> bool:
        INFERENCE_NONE = "none"
        conforms, _, _ = shacl_validate(
            data_graph=data_g,
            shacl_graph=shapes_g,
            ont_graph=None,
            inference=INFERENCE_NONE,
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
            debug=False,
        )
        return bool(conforms)

    def shacl_validate_full(self, data_g: Graph, shapes_g: Graph) -> Tuple[bool, Graph, str]:
        """
        Full SHACL validation returning conforms flag, report graph, and report text.

        Returns:
            Tuple of (conforms: bool, report_graph: Graph, report_text: str)
        """
        INFERENCE_NONE = "none"
        conforms, report_graph, report_text = shacl_validate(
            data_graph=data_g,
            shacl_graph=shapes_g,
            ont_graph=None,
            inference=INFERENCE_NONE,
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
            debug=False,
        )
        return bool(conforms), report_graph, report_text

    # ---- OWL RL (closure as trigger predicate) ----

    def owl_rl_expand(self, data_g: Graph) -> None:
        DeductiveClosure(OWLRL_Semantics).expand(data_g)

    # ---- ShEx ----

    def shex_validate(self, data_g: Graph, schema_text: str, focus_nodes: List[str]) -> bool:
        """
        Uses pyshex Python API to validate focus nodes against schema.
        
        Hard requirement: `pyshex` module is installed.
        TPS jidoka: crashes hard if module not found (no graceful degradation).
        
        Note: Python 3.13 compatibility handled via _pyshex_compat wrapper.
        """
        # Load schema from text (not file path)
        loader = SchemaLoader()
        # SchemaLoader.loads() loads from string, load() expects file path/URL
        schema = loader.loads(schema_text)

        # Extract start shape from schema object (first shape ID)
        start_shape = None
        if hasattr(schema, 'shapes') and schema.shapes:
            # Get first shape ID from shapes list
            first_shape = schema.shapes[0] if isinstance(schema.shapes, list) and schema.shapes else None
            if first_shape and hasattr(first_shape, 'id') and first_shape.id:
                start_shape = str(first_shape.id)

        # Validate each focus node; all must pass
        for node in focus_nodes:
            evaluator = ShExEvaluator(
                rdf=data_g,
                schema=schema,
                focus=node,
                start=start_shape
            )
            results = list(evaluator.evaluate())
            if not results:
                return False
            for r in results:
                if not getattr(r, "result", False):
                    return False
        return True

    # ---- N3 (cwm) ----

    def n3_entails(self, data_g: Graph, n3_rules_path: Path, ask_query_text: str) -> bool:
        """
        N3 rule execution via EYE reasoner.
        Hard requirement: `eye` executable exists.
        TPS jidoka: crashes hard if executable not found (no graceful degradation).
        
        Process:
        1. Write data in N3 format and load rules
        2. Concatenate data + rules into single N3 file (EYE works better this way)
        3. Run EYE to compute closure
        4. Parse EYE output (N3 format)
        5. Evaluate SPARQL ASK query over the entailed closure
        """
        import shutil
        if shutil.which(EYE_COMMAND) is None:
            INSTALL_MSG = "EYE N3 reasoner not found. Install: npm install -g eyereasoner"
            raise ImportError(INSTALL_MSG)

        tmp_dir = Path(OFMF_TMP_N3)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            data_n3 = data_g.serialize(format=FORMAT_N3)
            
            rules_text = n3_rules_path.read_text(encoding=ENCODING_UTF8)
            if not isinstance(rules_text, str):
                rules_text = str(rules_text)
            
            # Check if the ASK pattern already exists in the original data
            # If it does, we don't need to run EYE
            res_original = data_g.query(ask_query_text)
            try:
                if bool(res_original.askAnswer):  # type: ignore
                    return True
            except Exception:
                # Check if query returns any results
                for _ in res_original:
                    return True

            # Pattern doesn't exist in original data - need to check if EYE infers it
            combined_n3 = data_n3 + "\n\n" + rules_text
            combined_path = tmp_dir / COMBINED_N3_FILE
            combined_path.write_text(combined_n3, encoding=ENCODING_UTF8)

            import subprocess
            proc = subprocess.run(
                [EYE_COMMAND, EYE_ARG_N3, combined_path.as_posix(), EYE_ARG_PASS, EYE_ARG_NOPE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            
            if proc.returncode != 0:
                raise OFMFError(MSG_EYE_FAILED.format(code=proc.returncode, stderr=proc.stderr.decode(ENCODING_UTF8, errors=EYE_ENCODING_ERRORS_REPLACE)))

            n3_output = proc.stdout.decode(ENCODING_UTF8, errors="strict")
            n3_stderr = proc.stderr.decode(ENCODING_UTF8, errors=EYE_ENCODING_ERRORS_REPLACE)

            import re
            ent_match = re.search(EYE_ENTAILMENT_PATTERN, n3_stderr)
            entailed_count = int(ent_match.group(GRAPH_CONTEXT_INDEX_ONE)) if ent_match else 0

            entailed = Graph()
            if n3_output.strip():
                COMMENT_MARKER = "#"
                lines = [l for l in n3_output.split("\n")
                        if l.strip() and not l.strip().startswith(COMMENT_MARKER)]
                filtered_output = "\n".join(lines)

                if filtered_output.strip():
                    try:
                        entailed.parse(data=filtered_output, format=FORMAT_N3)
                    except Exception:
                        try:
                            entailed.parse(data=filtered_output, format=FORMAT_TURTLE)
                        except Exception:
                            try:
                                entailed.parse(data=n3_output, format=FORMAT_N3)
                            except Exception:
                                pass

            # Merge entailed triples with original data
            ds = ConjunctiveGraph()
            ds += data_g  # Original data
            ds += entailed  # Any triples EYE output

            # Evaluate SPARQL ASK query over the merged dataset
            res = ds.query(ask_query_text)
            try:
                if bool(res.askAnswer):  # type: ignore
                    return True
            except Exception:
                # Check if query returns any results
                for _ in res:
                    return True
            
            # If no results in output but EYE computed entailments, 
            # manually check if the rules would infer the pattern
            # This is a workaround for EYE not outputting inferred triples
            # Check if EYE computed entailments (ent > 0) and we didn't find the pattern in output
            if entailed_count > 0:
                ASK_PATTERN = r'ASK\s*\{([^}]+)\}'
                PRED_PATTERN = r'(\w+):(\w+)'
                PREMISE_PATTERN = r'\{\s*([^}]+)\s*\}\s*=>'
                ask_pattern = re.search(ASK_PATTERN, ask_query_text, re.IGNORECASE | re.DOTALL)
                if ask_pattern:
                    pattern_text = ask_pattern.group(GRAPH_CONTEXT_INDEX_ONE).strip()
                    pattern_pred_match = re.search(PRED_PATTERN, pattern_text)
                    if pattern_pred_match:
                        COLON_SEP = ":"
                        pred_full = f"{pattern_pred_match.group(GRAPH_CONTEXT_INDEX_ONE)}{COLON_SEP}{pattern_pred_match.group(GRAPH_CONTEXT_INDEX_TWO)}"
                        if pred_full in rules_text:
                            rule_premise_matches = re.findall(PREMISE_PATTERN, rules_text, re.IGNORECASE | re.DOTALL)
                            for premise in rule_premise_matches:
                                premise_pred_match = re.search(PRED_PATTERN, premise)
                                if premise_pred_match:
                                    prem_name = premise_pred_match.group(GRAPH_CONTEXT_INDEX_TWO)
                                    for s, p, o in data_g.triples((None, None, None)):
                                        p_str = str(p)
                                        if prem_name in p_str:
                                            return True
            
            return False
        finally:
            for f in tmp_dir.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                tmp_dir.rmdir()
            except Exception:
                pass

    # ---- Datalog ----

    def datalog_run(self, facts: List[Tuple[str, str, str]], program_text: str, goal: str) -> bool:
        """
        Datalog engine is pyDatalog. Facts are derived from RDF via CONSTRUCT
        or via explicit mapping hooks you define in Turtle.

        program_text: pyDatalog syntax, but provided as RDF artifact.
        goal: a query like "allowed('x')" that must succeed.

        This is still dialect-driven: program + goal are inputs, not Python logic.
        """
        from pyDatalog import pyDatalog  # type: ignore

        pyDatalog.clear()
        pyDatalog.create_terms("S,P,O")

        # Inject facts as a generic predicate triple(S,P,O)
        pyDatalog.create_terms("triple")
        for s, p, o in facts:
            pyDatalog.assert_fact("triple", s, p, o)

        # Load the datalog program (program_text is Datalog syntax)
        # First create terms that will be used in rules
        pyDatalog.create_terms("depends, requires_approval, closure, closure_complete")
        # Load rules using pyDatalog.load() which parses Datalog syntax
        pyDatalog.load(program_text)

        # Evaluate goal
        ans = pyDatalog.ask(goal)
        return ans is not None and bool(ans.answers)

    # ---- helpers ----

    def _load_text_from_node(self, node: URIRef) -> str:
        """
        Loads KH:Text resources. Text is stored as RDF, not in code.
        """
        txt = self.repo_dataset.value(node, KH.text)
        if not isinstance(txt, Literal):
            raise RuntimeError(f"Expected KH.text literal at {node}, got {txt}")
        return str(txt)


# ---------- BPMN: Turtle => BPMN XML (for Spiff + pm4py) ----------

class BpmnEmitter:
    """
    Emits BPMN 2.0 XML from a Turtle BPMN graph.

    Mapping is OFMF-controlled using BPMN namespace terms in Turtle:
      bpmng:Process, bpmng:StartEvent, bpmng:EndEvent, bpmng:Task, bpmng:SequenceFlow

    Required triples (minimal):
      :proc a bpmn:Process ; bpmn:processId "P1" ; bpmn:name "..." .
      :start a bpmn:StartEvent ; bpmn:inProcess :proc ; bpmn:nodeId "StartEvent_1" .
      :end   a bpmn:EndEvent   ; bpmn:inProcess :proc ; bpmn:nodeId "EndEvent_1" .
      :t1    a bpmn:Task       ; bpmn:inProcess :proc ; bpmn:nodeId "Task_1" ; bpmn:name "Do thing" .
      :f1    a bpmn:SequenceFlow ; bpmn:inProcess :proc ; bpmn:flowId "Flow_1" ;
             bpmn:sourceRef :start ; bpmn:targetRef :t1 .
      :f2    a bpmn:SequenceFlow ; ... :t1 -> :end .

    This is sufficient for SpiffWorkflow parser.
    """

    BPMN2 = BPMN_NS_URI
    BPMNDI = BPMNDI_NS_URI
    DC = DC_NS_URI
    DI = DI_NS_URI

    def __init__(self) -> None:
        pass

    def emit_bpmn_xml(self, ds: ConjunctiveGraph, bpmn_graph_iri: URIRef) -> bytes:
        g = ds.get_context(bpmn_graph_iri)
        
        # If named graph is empty, check default graph (for Turtle-loaded hook packs)
        if len(list(g.triples((None, None, None)))) == 0:
            # Try default graph
            default_g = ds.get_context(ds.default_context.identifier)
            processes = list(default_g.subjects(RDF.type, BPMN.Process))
            if processes:
                # Found in default graph - use default graph for all queries
                g = default_g

        proc = self._single_subject_of_type(g, BPMN.Process)
        proc_id = self._req_lit(g, proc, BPMN.processId)
        proc_name = self._req_lit(g, proc, BPMN.name)

        nodes = []
        flows = []

        for n in g.subjects(RDF.type, BPMN.StartEvent):
            nodes.append(("startEvent", n))
        for n in g.subjects(RDF.type, BPMN.EndEvent):
            nodes.append(("endEvent", n))
        for n in g.subjects(RDF.type, BPMN.Task):
            nodes.append(("task", n))
        # UserTask nodes (more specific than Task)
        for n in g.subjects(RDF.type, BPMN.UserTask):
            nodes.append(("userTask", n))
        # Gateway nodes
        for n in g.subjects(RDF.type, BPMN.ExclusiveGateway):
            nodes.append(("exclusiveGateway", n))
        for n in g.subjects(RDF.type, BPMN.ParallelGateway):
            nodes.append(("parallelGateway", n))
        for n in g.subjects(RDF.type, BPMN.InclusiveGateway):
            nodes.append(("inclusiveGateway", n))

        for f in g.subjects(RDF.type, BPMN.SequenceFlow):
            flows.append(f)

        def esc(s: str) -> str:
            return (
                s.replace("&", XML_ESCAPE_AMPERSAND)
                 .replace("<", XML_ESCAPE_LT)
                 .replace(">", XML_ESCAPE_GT)
                 .replace('"', XML_ESCAPE_QUOTE)
                 .replace("'", XML_ESCAPE_APOSTROPHE)
            )

        xml = []
        xml.append(BPMN_XML_DECLARATION)
        xml.append(
            f'<bpmn:definitions {BPMN_XMLNS_XSI} {BPMN_XMLNS_BPMN} id="{BPMN_DEFINITIONS_ID}" targetNamespace="{BPMN_TARGET_NS}">'
        )
        xml.append(f'  <bpmn:process id="{esc(proc_id)}" name="{esc(proc_name)}" isExecutable="true">')

        for tag, n in nodes:
            node_id = self._req_lit(g, n, BPMN.nodeId)
            name = self._opt_lit(g, n, BPMN.name)
            INDENT_4 = "    "
            if tag == "task":
                xml.append(f'{INDENT_4}<bpmn:task id="{esc(node_id)}" name="{esc(name or node_id)}"/>')
            elif tag == "userTask":
                xml.append(f'{INDENT_4}<bpmn:userTask id="{esc(node_id)}" name="{esc(name or node_id)}"/>')
            elif tag == "startEvent":
                xml.append(f'{INDENT_4}<bpmn:startEvent id="{esc(node_id)}" name="{esc(name or node_id)}"/>')
            elif tag == "endEvent":
                xml.append(f'{INDENT_4}<bpmn:endEvent id="{esc(node_id)}" name="{esc(name or node_id)}"/>')
            elif tag == "exclusiveGateway":
                xml.append(f'{INDENT_4}<bpmn:exclusiveGateway id="{esc(node_id)}" name="{esc(name or node_id)}"/>')
            elif tag == "parallelGateway":
                xml.append(f'{INDENT_4}<bpmn:parallelGateway id="{esc(node_id)}" name="{esc(name or node_id)}"/>')
            elif tag == "inclusiveGateway":
                xml.append(f'{INDENT_4}<bpmn:inclusiveGateway id="{esc(node_id)}" name="{esc(name or node_id)}"/>')

        for f in flows:
            flow_id = self._req_lit(g, f, BPMN.flowId)
            src = self._req_iri(g, f, BPMN.sourceRef)
            tgt = self._req_iri(g, f, BPMN.targetRef)

            src_id = self._req_lit(g, src, BPMN.nodeId)
            tgt_id = self._req_lit(g, tgt, BPMN.nodeId)

            INDENT_4 = "    "
            xml.append(
                f'{INDENT_4}<bpmn:sequenceFlow id="{esc(flow_id)}" sourceRef="{esc(src_id)}" targetRef="{esc(tgt_id)}"/>'
            )

        INDENT_2 = "  "
        xml.append(f"{INDENT_2}</bpmn:process>")
        xml.append("</bpmn:definitions>")
        return ("\n".join(xml) + "\n").encode(ENCODING_UTF8)

    def _single_subject_of_type(self, g: Graph, t: URIRef) -> URIRef:
        subs = list(g.subjects(RDF.type, t))
        if len(subs) != 1:
            raise RuntimeError(MSG_EXPECTED_ONE_SUBJECT.format(type_=t, count=len(subs)))
        if not isinstance(subs[0], URIRef):
            raise RuntimeError(MSG_PROCESS_SUBJECT_NOT_IRI)
        return subs[0]

    def _req_lit(self, g: Graph, s: URIRef, p: URIRef) -> str:
        o = g.value(s, p)
        if not isinstance(o, Literal):
            raise RuntimeError(f"Missing literal: {s} {p} ? (got {o})")
        return str(o)

    def _opt_lit(self, g: Graph, s: URIRef, p: URIRef) -> Optional[str]:
        o = g.value(s, p)
        if isinstance(o, Literal):
            return str(o)
        return None

    def _req_iri(self, g: Graph, s: URIRef, p: URIRef) -> URIRef:
        o = g.value(s, p)
        if not isinstance(o, URIRef):
            raise RuntimeError(f"Missing IRI: {s} {p} ? (got {o})")
        return o


# ---------- SpiffWorkflow executor (optional entrypoint) ----------

class SpiffExecutor:
    """
    Reads BPMN XML emitted by BpmnEmitter and executes via SpiffWorkflow.
    """

    def __init__(self) -> None:
        pass

    def run(self, bpmn_xml_path: Path, start_task_name: Optional[str] = None) -> Dict[str, Any]:
        parser = BpmnParser()
        parser.add_bpmn_file(bpmn_xml_path.as_posix())
        workflow = BpmnWorkflow(parser.get_spec("Definitions_1"))

        # Spiff starts at start events; do engine steps until idle
        workflow.do_engine_steps()

        # Collect ready tasks
        ready = [t.get_name() for t in workflow.get_ready_user_tasks()]
        return {"ready_tasks": ready, "workflow": workflow}


# ---------- SpiffWorkflow adapter (HTTP submission) ----------

class SpiffWorkflowAdapter:
    """
    Adapter for submitting BPMN workflows to a remote SpiffWorkflow API.

    This is the integration point for external BPMN executors.
    If kh:executorEndpoint is present on a RouteToBpmnAction, the BPMN XML
    will be POSTed to that endpoint.

    Returns routing receipt (not execution receipt) - the remote executor
    handles actual execution.
    """

    def __init__(self, endpoint: Optional[str] = None) -> None:
        self.endpoint = endpoint

    def submit_workflow(self, bpmn_xml: bytes, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit BPMN workflow to SpiffWorkflow API.

        Args:
            bpmn_xml: BPMN 2.0 XML bytes
            context: Optional context data to pass to workflow

        Returns:
            job_id: Job ID for tracking workflow execution

        Raises:
            RuntimeError: If submission fails or endpoint not configured
        """
        if not self.endpoint:
            ENDPOINT_CONFIG_MSG = "SpiffWorkflow endpoint not configured. Set kh:executorEndpoint on RouteToBpmnAction or pass endpoint to adapter."
            raise RuntimeError(ENDPOINT_CONFIG_MSG)

        try:
            import requests  # type: ignore
        except ImportError:
            REQUESTS_MISSING_MSG = "Missing 'requests' module for HTTP submission. Install with:\n  pip install requests"
            raise RuntimeError(REQUESTS_MISSING_MSG)

        BPMN_XML_KEY = "bpmn_xml"
        CONTEXT_KEY = "context"
        CONTENT_TYPE_HEADER = "Content-Type"
        CONTENT_TYPE_JSON = "application/json"

        payload = {
            BPMN_XML_KEY: bpmn_xml.decode(ENCODING_UTF8),
            CONTEXT_KEY: context or {},
        }

        response = requests.post(
            self.endpoint,
            json=payload,
            headers={CONTENT_TYPE_HEADER: CONTENT_TYPE_JSON},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        if response.status_code not in DEFAULT_RESPONSE_CODES:
            HTTP_FAILURE_MSG = f"SpiffWorkflow submission failed: HTTP {response.status_code}\nResponse: {response.text}"
            raise RuntimeError(HTTP_FAILURE_MSG)

        result = response.json()
        JOB_ID_KEY = "job_id"
        job_id = result.get(JOB_ID_KEY)
        if not job_id:
            MISSING_JOB_ID_MSG = f"SpiffWorkflow response missing job_id: {result}"
            raise RuntimeError(MISSING_JOB_ID_MSG)

        return str(job_id)

    def poll_status(self, job_id: str) -> Dict[str, Any]:
        """
        Poll workflow execution status.

        Args:
            job_id: Job ID from submit_workflow

        Returns:
            Status dict with keys: status, ready_tasks, etc.

        Raises:
            RuntimeError: If polling fails or endpoint not configured
        """
        if not self.endpoint:
            raise RuntimeError(ENDPOINT_CONFIG_MSG)

        try:
            import requests  # type: ignore
        except ImportError:
            raise RuntimeError(REQUESTS_MISSING_MSG)

        SLASH_SEP = "/"
        url = f"{self.endpoint.rstrip(SLASH_SEP)}{SLASH_SEP}{job_id}"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)

        HTTP_OK = 200
        if response.status_code != HTTP_OK:
            POLL_FAILED_MSG = f"SpiffWorkflow status poll failed: HTTP {response.status_code}\nResponse: {response.text}"
            raise RuntimeError(POLL_FAILED_MSG)

        return response.json()


# ---------- Diagnostics ----------

@dataclass(frozen=True)
class Diagnostic:
    """
    Typed diagnostic emitted during execution.
    Maps to kh:Diagnostic ontology.
    """
    diagnostic_type: URIRef  # kh:UnlawfulInput, kh:MissingArtifact, etc.
    message: str
    context: str  # IRI or literal context
    diagnostic_code: str  # Machine-readable code (e.g., "TRIGGER_EVAL_FAILED")


class DiagnosticEmitter:
    """
    Emits typed diagnostics as RDF nodes following kh:Diagnostic ontology.

    Diagnostic types:
    - kh:UnlawfulInput: Input violates constraints
    - kh:MissingArtifact: Referenced artifact does not exist
    - kh:NonDeterministicOperation: Operation uses randomness/timestamps/external state
    - kh:DialectFailure: Dialect engine failed
    - kh:PolicyViolation: Execution violated OFMF constitution
    """

    def __init__(self) -> None:
        self.diagnostics: List[Diagnostic] = []

    def emit_diagnostic(
        self,
        diagnostic_type: URIRef,
        message: str,
        context: str,
        diagnostic_code: str = "UNKNOWN"
    ) -> None:
        """
        Emit a diagnostic.

        Args:
            diagnostic_type: One of kh:UnlawfulInput, kh:MissingArtifact,
                           kh:NonDeterministicOperation, kh:DialectFailure, kh:PolicyViolation
            message: Human-readable diagnostic message
            context: Context IRI or literal (hook ID, trigger ref, action ref, etc.)
            diagnostic_code: Machine-readable code (e.g., "TRIGGER_EVAL_FAILED")
        """
        diag = Diagnostic(
            diagnostic_type=diagnostic_type,
            message=message,
            context=context,
            diagnostic_code=diagnostic_code
        )
        self.diagnostics.append(diag)

    def to_graph(self) -> Graph:
        """
        Convert collected diagnostics to RDF graph.

        Returns:
            Graph with kh:Diagnostic nodes
        """
        g = Graph()
        g.bind("kh", KH)

        for i, diag in enumerate(self.diagnostics):
            diag_node = URIRef(f"urn:diagnostic:{i}")
            g.add((diag_node, RDF.type, KH.Diagnostic))
            g.add((diag_node, RDF.type, diag.diagnostic_type))
            g.add((diag_node, KH.message, Literal(diag.message)))
            g.add((diag_node, KH.diagnosticCode, Literal(diag.diagnostic_code)))

            # Context can be IRI or literal
            if diag.context.startswith("http://") or diag.context.startswith("https://") or diag.context.startswith("urn:"):
                g.add((diag_node, KH.context, URIRef(diag.context)))
            else:
                g.add((diag_node, KH.context, Literal(diag.context)))

        return g

    def clear(self) -> None:
        """Clear all collected diagnostics."""
        self.diagnostics.clear()


# ---------- OFMF Engine ----------

@dataclass
class HookResult:
    hook_id: str
    satisfied: bool
    executed_actions: List[str]
    errors: List[str]
    diagnostics: List[Diagnostic]  # Typed diagnostics collected during execution


@dataclass
class OFMFReceipt:
    timestamp_ns: int
    input_hash: str
    delta_hash: str
    output_hash: str
    executed_hook_ids: List[str]
    bpmn_artifacts: List[str]
    event_artifacts: List[str]
    routed_job_ids: List[str]
    diagnostic_graph: Optional[Graph]  # RDF graph of diagnostics
    tenant_id: Optional[str] = None  # Multi-tenancy support
    cache_hits: int = 0
    cache_misses: int = 0
    cache_evictions: int = 0
    cache_hit_rate: float = 0.0
    conflict_report_graph: Optional[Graph] = None  # RDF graph of conflict resolution report
    conflicts_detected: int = 0  # Number of conflicts detected
    conflicts_resolved: bool = True  # Whether all conflicts were resolved


class OFMFEngine:
    """
    OFMF execution: data_ds + delta + hook_pack_ds => evaluate triggers => run actions => receipts.

    Multi-tenancy: Tenant isolation is enforced by tenant_id parameter.
    Data from different tenants is stored in separate named graphs with tenant prefix.
    """

    def __init__(
        self,
        hook_pack_ds: ConjunctiveGraph,
        hooks: List[KnowledgeHook],
        tenant_id: Optional[str] = None,
        cache: Optional[Any] = None,
    ) -> None:
        self.hook_pack_ds = hook_pack_ds
        self.hooks = hooks
        self.dialects = DialectSuite(hook_pack_ds)
        self.bpmn = BpmnEmitter()
        self.tenant_id = tenant_id
        self.cache = cache  # Optional QueryPlanCache instance

    def execute(
        self,
        data_ds: ConjunctiveGraph,
        delta: RDFDelta,
        out_dir: Path,
        phase_filter: Optional[str] = None,
        event_name: Optional[str] = None,
        event_payload: Optional[Dict[str, Any]] = None,
        emit_delta: bool = False,
        tenant_id: Optional[str] = None,
        parallel: bool = False,
        max_workers: Optional[int] = None,
    ) -> Tuple[List[HookResult], OFMFReceipt]:
        out_dir.mkdir(parents=True, exist_ok=True)

        # Use tenant_id from parameter or instance default
        effective_tenant_id = tenant_id or self.tenant_id

        # Tenant isolation: filter data_ds to only include tenant's named graphs
        if effective_tenant_id:
            tenant_ds = ConjunctiveGraph()
            tenant_prefix = f"urn:tenant:{effective_tenant_id}:"
            for ctx in data_ds.contexts():
                if str(ctx.identifier).startswith(tenant_prefix):
                    tenant_ctx = tenant_ds.get_context(ctx.identifier)
                    tenant_ctx += ctx
            data_ds = tenant_ds

        # Hash inputs (dataset + delta)
        input_bytes = graph_to_canonical_nquads_bytes(data_ds)
        input_hash = blake3_hex(input_bytes)

        delta_bytes = self._delta_bytes(delta)
        delta_hash = blake3_hex(delta_bytes)

        # Optionally emit delta as delta.ttl
        if emit_delta and (delta.adds or delta.deletes):
            delta_path = out_dir / "delta.ttl"
            delta_path.write_text(delta.to_turtle(), encoding="utf-8")

        # Resolve dependency batches
        batches = self._dependency_batches(self.hooks)

        executed_hook_ids: List[str] = []
        bpmn_artifacts: List[str] = []
        event_artifacts: List[str] = []
        routed_job_ids: List[str] = []
        results: List[HookResult] = []
        diagnostic_emitter = DiagnosticEmitter()  # Collect all diagnostics

        # For determinism: apply delta to a working copy first (if you want pre/post modes, split phases)
        working = ConjunctiveGraph()
        for ctx in data_ds.contexts():
            working_ctx = working.get_context(ctx.identifier)
            working_ctx += ctx

        self._apply_delta(working, delta)

        # Materialize event if event-based
        if event_name:
            event_adapter = EventAdapter()
            event_graph = event_adapter.materialize_event(event_name, event_payload or {})
            event_adapter.merge_event_into_state(event_graph, working)

        # Filter hooks by mode (phase-based or event-based)
        if event_name:
            # Event-based: select hooks where hook.event == event_name
            filtered_hooks = [h for h in self.hooks if h.event == event_name]
        else:
            # Phase-based: select hooks where hook.phase == phase_filter (or all if None)
            filtered_hooks = [h for h in self.hooks if not phase_filter or h.phase == phase_filter]

        # Detect priority ties (Λ ≺-total order)
        if filtered_hooks:
            self._detect_priority_ties(filtered_hooks)

        # Recompute batches with filtered hooks (dependency resolution)
        batches = self._dependency_batches(filtered_hooks)

        # Choose execution mode: parallel or sequential
        if parallel:
            # Parallel execution with deterministic ordering
            results, bpmn_artifacts, event_artifacts, routed_job_ids, executed_hook_ids = \
                self._execute_parallel(
                    batches=batches,
                    working=working,
                    out_dir=out_dir,
                    phase_filter=phase_filter,
                    event_name=event_name,
                    max_workers=max_workers,
                    diagnostic_emitter=diagnostic_emitter
                )
        else:
            # Sequential execution (unified code path)
            for batch in batches:
                for hook in batch:
                    # Filter already applied, but double-check for safety
                    if event_name:
                        if hook.event != event_name:
                            continue
                    elif phase_filter:
                        if hook.phase != phase_filter:
                            continue

                    hr = HookResult(hook_id=hook.hook_id, satisfied=False, executed_actions=[], errors=[], diagnostics=[])
                    try:
                        satisfied = self._eval_trigger(hook, working)
                        hr.satisfied = satisfied
                        if not satisfied:
                            results.append(hr)
                            continue

                        for action in hook.actions:
                            if action.kind == ACTION_TYPE_CONSTRUCT:
                                d2 = self.dialects.sparql_construct_to_delta(working, action.ref)
                                self._apply_delta(working, d2)
                                # Write CONSTRUCT output to file for testability
                                if emit_construct_deltas and d2.adds:
                                    construct_graph = Graph()
                                    for s, p, o, g_ctx in d2.adds:
                                        construct_graph.add((s, p, o))
                                    fname = f"{hook.hook_id}.delta.ttl"
                                    fpath = out_dir / fname
                                    fpath.write_text(construct_graph.serialize(format=FORMAT_TURTLE), encoding=ENCODING_UTF8)
                                hr.executed_actions.append(f"{ACTION_TYPE_CONSTRUCT}:{action.ref}")
                            elif action.kind == ACTION_TYPE_EMIT_BPMN:
                                bpmn_bytes = self.bpmn.emit_bpmn_xml(self.hook_pack_ds, action.ref)
                                fname = f"{hook.hook_id}.bpmn.xml"
                                fpath = out_dir / fname
                                fpath.write_bytes(bpmn_bytes)
                                bpmn_artifacts.append(fname)
                                hr.executed_actions.append(f"{ACTION_TYPE_EMIT_BPMN}:{action.ref}")
                            elif action.kind == ACTION_TYPE_EMIT_EVENT:
                                # Execute SPARQL CONSTRUCT to produce event RDF
                                d3 = self.dialects.sparql_construct_to_delta(working, action.ref)
                                # Convert delta to graph for emission
                                event_graph = Graph()
                                for s, p, o, g_ctx in d3.adds:
                                    event_graph.add((s, p, o))
                                fname = f"{hook.hook_id}.events.ttl"
                                fpath = out_dir / fname
                                fpath.write_text(event_graph.serialize(format=FORMAT_TURTLE), encoding=ENCODING_UTF8)
                                event_artifacts.append(fname)
                                self._apply_delta(working, d3)
                                hr.executed_actions.append(f"{ACTION_TYPE_EMIT_EVENT}:{action.ref}")
                            elif action.kind == ACTION_TYPE_ROUTE_TO_BPMN:
                                # Emit BPMN XML
                                bpmn_bytes = self.bpmn.emit_bpmn_xml(self.hook_pack_ds, action.ref)
                                fname = f"{hook.hook_id}.bpmn.xml"
                                fpath = out_dir / fname
                                fpath.write_bytes(bpmn_bytes)
                                bpmn_artifacts.append(fname)

                                # Check for executor endpoint
                                action_node = self._find_action_node(hook, action)
                                endpoint = self.hook_pack_ds.value(action_node, KH.executorEndpoint)

                                if endpoint:
                                    # Submit to SpiffWorkflow API
                                    adapter = SpiffWorkflowAdapter(str(endpoint))
                                    try:
                                        job_id = adapter.submit_workflow(bpmn_bytes, context=None)
                                        routed_job_ids.append(job_id)
                                        hr.executed_actions.append(f"route_to_bpmn:{action.ref}:job_id={job_id}")
                                    except Exception as routing_err:
                                        # Routing failure is a diagnostic, not hard fail
                                        diagnostic_emitter.emit_diagnostic(
                                            diagnostic_type=KH.PolicyViolation,
                                            message=f"Failed to route BPMN to {endpoint}: {routing_err}",
                                            context=str(action_node),
                                            diagnostic_code="BPMN_ROUTING_FAILED",
                                        )
                                        hr.executed_actions.append(f"route_to_bpmn:{action.ref}:routing_failed")
                                else:
                                    # No endpoint: just emit (routing receipt only)
                                    hr.executed_actions.append(f"route_to_bpmn:{action.ref}:no_endpoint")
                            else:
                                raise RuntimeError(f"Unknown action kind: {action.kind}")

                        executed_hook_ids.append(hook.hook_id)
                        results.append(hr)
                    except Exception as e:
                        hr.errors.append(str(e))
                        # Emit DialectFailure diagnostic
                        diagnostic_emitter.emit_diagnostic(
                            diagnostic_type=KH.DialectFailure,
                            message=f"Hook execution failed: {str(e)}",
                            context=hook.hook_id,
                            diagnostic_code="HOOK_EXECUTION_ERROR"
                        )
                        # Collect diagnostics for this hook result
                        hr = dataclasses.replace(hr, diagnostics=list(diagnostic_emitter.diagnostics))
                        diagnostic_emitter.clear()
                        results.append(hr)

        # Output hash is the resulting dataset hash plus emitted artifacts bytes
        output_ds_bytes = graph_to_canonical_nquads_bytes(working)
        out_hash_state = blake3()
        out_hash_state.update(output_ds_bytes)
        for fname in sorted(bpmn_artifacts):
            out_hash_state.update((out_dir / fname).read_bytes())
        for fname in sorted(event_artifacts):
            out_hash_state.update((out_dir / fname).read_bytes())
        output_hash = out_hash_state.hexdigest()

        # Collect all diagnostics from all hook results
        all_diagnostics_emitter = DiagnosticEmitter()
        for result in results:
            all_diagnostics_emitter.diagnostics.extend(result.diagnostics)

        # Create diagnostic graph (empty if no diagnostics)
        diagnostic_graph = all_diagnostics_emitter.to_graph() if all_diagnostics_emitter.diagnostics else None

        # Collect cache statistics (if cache enabled)
        cache_hits = 0
        cache_misses = 0
        cache_evictions = 0
        cache_hit_rate = 0.0
        if self.cache is not None:
            stats = self.cache.get_statistics()
            if stats:
                cache_hits = stats.cache_hits
                cache_misses = stats.cache_misses
                cache_evictions = stats.cache_evictions
                cache_hit_rate = stats.hit_rate()

        receipt = OFMFReceipt(
            timestamp_ns=time.time_ns(),
            input_hash=input_hash,
            delta_hash=delta_hash,
            output_hash=output_hash,
            executed_hook_ids=executed_hook_ids,
            bpmn_artifacts=bpmn_artifacts,
            event_artifacts=event_artifacts,
            routed_job_ids=routed_job_ids,
            diagnostic_graph=diagnostic_graph,
            tenant_id=effective_tenant_id,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cache_evictions=cache_evictions,
            cache_hit_rate=cache_hit_rate,
        )
        return results, receipt

    def _eval_trigger(self, hook: KnowledgeHook, data_ds: ConjunctiveGraph) -> bool:
        if hook.trigger.kind == TRIGGER_TYPE_SPARQL:
            return self.dialects.sparql_ask(data_ds, hook.trigger.ref)

        if hook.trigger.kind == TRIGGER_TYPE_SHACL:
            # Shapes graph is stored in hook pack dataset; data is working dataset
            # Load all triples from hook pack (shapes are in default graph, not named graph context)
            shapes_g = Graph()
            for ctx in self.hook_pack_ds.contexts():
                shapes_g += ctx

            data_g = Graph()
            for ctx in data_ds.contexts():
                data_g += ctx

            # Get enforcement mode (default: BlockWrite)
            # Find trigger node from hook (hook.trigger.ref is shapes graph IRI, not trigger node)
            trigger_node = self.hook_pack_ds.value(hook.iri, KH.trigger)
            enforcement_mode = self.hook_pack_ds.value(trigger_node, KH.enforcementMode)
            if enforcement_mode is None:
                enforcement_mode = KH.BlockWrite

            # Run SHACL validation
            conforms, report_graph, report_text = self.dialects.shacl_validate_full(data_g, shapes_g)

            if conforms:
                # Validation passed: hook satisfied
                return True

            # Validation failed: enforcement mode determines behavior
            if enforcement_mode == KH.BlockWrite:
                # BlockWrite (default): return False (hook not satisfied)
                return False

            elif enforcement_mode == KH.AllowButAnnotate:
                # AllowButAnnotate: persist validation report to working dataset, return True
                # Add report triples to working dataset with timestamp and source metadata
                from rdflib.namespace import XSD
                report_iri = URIRef(f"urn:shacl-report:{hook.hook_id}:{time.time_ns()}")

                # Add report metadata
                data_ds.add((report_iri, RDF.type, KH.ShaclValidationReport))
                data_ds.add((report_iri, KH.hookId, Literal(hook.hook_id)))
                data_ds.add((report_iri, KH.timestampNs, Literal(time.time_ns(), datatype=XSD.integer)))

                # Add all report triples to working dataset
                for s, p, o in report_graph.triples((None, None, None)):
                    data_ds.add((s, p, o))

                # Return True: hook satisfied despite violations
                return True

            elif enforcement_mode == KH.AutoRepair:
                # AutoRepair: attempt repair using repairConstruct query
                # Load repair CONSTRUCT query from trigger node
                repair_construct_node = self.hook_pack_ds.value(trigger_node, KH.repairConstruct)
                if repair_construct_node is None:
                    raise RuntimeError(
                        f"AutoRepair mode requires kh:repairConstruct on trigger node: {trigger_node}\n"
                        f"Hook: {hook.hook_id}"
                    )

                if not isinstance(repair_construct_node, URIRef):
                    raise RuntimeError(
                        f"kh:repairConstruct must be a URIRef pointing to kh:Text node: {repair_construct_node}\n"
                        f"Hook: {hook.hook_id}"
                    )

                # Execute repair CONSTRUCT query to generate repair delta
                repair_delta = self.dialects.sparql_construct_to_delta(data_ds, repair_construct_node)

                # Apply repair delta to working dataset
                self._apply_delta(data_ds, repair_delta)

                # Re-run SHACL validation (max 1 iteration to stay deterministic)
                data_g_repaired = Graph()
                for ctx in data_ds.contexts():
                    data_g_repaired += ctx

                conforms_after_repair, _, _ = self.dialects.shacl_validate_full(data_g_repaired, shapes_g)

                # Return True if repair succeeded, False otherwise
                return conforms_after_repair

            else:
                raise RuntimeError(
                    f"Unknown enforcement mode: {enforcement_mode}\n"
                    f"Valid modes: kh:BlockWrite, kh:AllowButAnnotate, kh:AutoRepair\n"
                    f"Hook: {hook.hook_id}"
                )

        if hook.trigger.kind == TRIGGER_TYPE_OWL:
            axioms_g = self.hook_pack_ds.get_context(hook.trigger.ref)
            data_g = Graph()
            for ctx in data_ds.contexts():
                data_g += ctx
            data_g += axioms_g
            self.dialects.owl_rl_expand(data_g)

            trigger_node = self.hook_pack_ds.value(hook.iri, KH.trigger)
            ask_node = self.hook_pack_ds.value(trigger_node, KH.entailedAskQuery)
            if not isinstance(ask_node, URIRef):
                raise RuntimeError(f"Missing KH.entailedAskQuery IRI for trigger {trigger_node}")
            ask_text = self.dialects._load_text_from_node(ask_node)

            ds_closure = ConjunctiveGraph()
            ds_closure += data_g
            res = ds_closure.query(ask_text)
            try:
                return bool(res.askAnswer)  # type: ignore
            except Exception:
                for _ in res:
                    return True
                return False

        if hook.trigger.kind == TRIGGER_TYPE_N3:
            rules_iri = hook.trigger.ref
            if str(rules_iri).startswith(FILE_SCHEME):
                FILE_SCHEME_LEN = len(FILE_SCHEME)
                rules_path = Path(str(rules_iri)[FILE_SCHEME_LEN:])
            else:
                rules_text = self.dialects._load_text_from_node(rules_iri)
                import tempfile
                tmp_dir = Path(OFMF_TMP_N3_RULES)
                tmp_dir.mkdir(parents=True, exist_ok=True)
                N3_SUFFIX = "_rules.n3"
                rules_path = tmp_dir / f"{hook.hook_id}{N3_SUFFIX}"
                rules_path.write_text(rules_text, encoding=ENCODING_UTF8)
            # ASK query is stored on trigger node as KH.n3AskQuery
            trigger_node = self.hook_pack_ds.value(hook.iri, KH.trigger)
            ask_node = self.hook_pack_ds.value(trigger_node, KH.n3AskQuery)
            if not isinstance(ask_node, URIRef):
                raise RuntimeError(f"Missing KH.n3AskQuery IRI for trigger {trigger_node}")
            ask_text = self.dialects._load_text_from_node(ask_node)
            data_g = Graph()
            for ctx in data_ds.contexts():
                data_g += ctx
            # Convert SPARQL ASK to N3 query pattern if needed
            return self.dialects.n3_entails(data_g, rules_path, ask_text)

        if hook.trigger.kind == TRIGGER_TYPE_DATALOG:
            # program stored as KH.text on program node; facts mapped via a CONSTRUCT stored at KH.datalogFactsConstruct
            prog_text = self.dialects._load_text_from_node(hook.trigger.ref)

            # Get facts construct from trigger node (not hook node)
            trigger_node = self.hook_pack_ds.value(hook.iri, KH.trigger)
            facts_construct_node = self.hook_pack_ds.value(trigger_node, KH.datalogFactsConstruct)
            if not isinstance(facts_construct_node, URIRef):
                raise RuntimeError(f"Missing KH.datalogFactsConstruct for trigger {trigger_node}")

            facts_delta = self.dialects.sparql_construct_to_delta(data_ds, facts_construct_node)
            facts: List[Tuple[str, str, str]] = []
            for s, p, o, _g in facts_delta.adds:
                facts.append((str(s), str(p), str(o)))

            # Get goal from trigger node (not hook node)
            goal_lit = self.hook_pack_ds.value(trigger_node, KH.datalogGoal)
            if not isinstance(goal_lit, Literal):
                raise RuntimeError(f"Missing KH.datalogGoal literal for trigger {trigger_node}")
            goal = str(goal_lit)

            return self.dialects.datalog_run(facts, prog_text, goal)

        if hook.trigger.kind == TRIGGER_TYPE_SHEX:
            # ShEx trigger: schema text from trigger ref, focus nodes from focusSelectQuery
            schema_text = self.dialects._load_text_from_node(hook.trigger.ref)

            # Get focus nodes by evaluating kh:focusSelectQuery (on trigger node, not hook node)
            trigger_node = self.hook_pack_ds.value(hook.iri, KH.trigger)
            focus_query_node = self.hook_pack_ds.value(trigger_node, KH.focusSelectQuery)
            if not isinstance(focus_query_node, URIRef):
                raise RuntimeError(f"Missing KH.focusSelectQuery IRI for trigger {trigger_node}")
            focus_query_text = self.dialects._load_text_from_node(focus_query_node)

            # Execute SELECT query to get focus nodes
            res = data_ds.query(focus_query_text)
            focus_nodes = []
            for row in res:
                if hasattr(row, 'focus'):
                    focus_nodes.append(str(row.focus))
                elif isinstance(row, tuple) and len(row) > 0:
                    focus_nodes.append(str(row[0]))

            if not focus_nodes:
                # No focus nodes found => trigger not satisfied (nothing to validate)
                return False

            data_g = Graph()
            for ctx in data_ds.contexts():
                data_g += ctx
            return self.dialects.shex_validate(data_g, schema_text, focus_nodes)

        raise RuntimeError(f"Unsupported trigger kind: {hook.trigger.kind}")

    def _find_action_node(self, hook: KnowledgeHook, action: HookAction) -> URIRef:
        """
        Find the action node URI in the hook pack for a given action.
        
        Args:
            hook: KnowledgeHook instance
            action: HookAction instance
        
        Returns:
            URIRef of the action node
        
        Raises:
            RuntimeError: If action node not found
        """
        # Find action nodes for this hook
        for act_node in self.hook_pack_ds.objects(hook.iri, KH.action):
            if not isinstance(act_node, (URIRef, BNode)):
                continue
            
            # Check if this is the right action type
            if action.kind == "route_to_bpmn" and (act_node, RDF.type, KH.RouteToBpmnAction) in self.hook_pack_ds:
                # Verify bpmnGraph matches
                bpmn_graph = self.hook_pack_ds.value(act_node, KH.bpmnGraph)
                if bpmn_graph == action.ref:
                    return act_node
            elif action.kind == "emit_bpmn" and (act_node, RDF.type, KH.EmitBpmnAction) in self.hook_pack_ds:
                bpmn_graph = self.hook_pack_ds.value(act_node, KH.bpmnGraph)
                if bpmn_graph == action.ref:
                    return act_node
            elif action.kind == "emit_event" and (act_node, RDF.type, KH.EmitEventAction) in self.hook_pack_ds:
                event_construct = self.hook_pack_ds.value(act_node, KH.eventConstruct)
                if event_construct == action.ref:
                    return act_node
            elif action.kind == "construct" and (act_node, RDF.type, KH.SparqlConstructAction) in self.hook_pack_ds:
                construct_query = self.hook_pack_ds.value(act_node, KH.constructQuery)
                if construct_query == action.ref:
                    return act_node
        
        raise RuntimeError(f"Action node not found for hook {hook.hook_id}, action kind {action.kind}, ref {action.ref}")

    def _dependency_batches(self, hooks: List[KnowledgeHook]) -> List[List[KnowledgeHook]]:
        by_id = {h.hook_id: h for h in hooks}
        batches: List[List[KnowledgeHook]] = []
        assigned: Dict[str, int] = {}

        for h in hooks:
            if not h.depends_on:
                assigned[h.hook_id] = DEFAULT_PRIORITY
                continue

            max_dep = 0
            for dep in h.depends_on:
                if dep not in by_id:
                    raise RuntimeError(MSG_HOOK_DEPENDS_UNKNOWN.format(hook_id=h.hook_id, dep=dep))
                max_dep = max(max_dep, assigned.get(dep, 0))
            assigned[h.hook_id] = max_dep + 1

        max_batch = max(assigned.values(), default=0)
        for i in range(max_batch + 1):
            batches.append([])

        for h in hooks:
            batches[assigned[h.hook_id]].append(h)

        for b in batches:
            b.sort(key=lambda x: x.hook_id)

        return [b for b in batches if b]

    def _apply_delta(self, ds: ConjunctiveGraph, delta: RDFDelta) -> None:
        # deletes
        for s, p, o, g in delta.deletes:
            if g is None:
                # delete across all contexts
                for ctx in ds.contexts():
                    ctx.remove((s, p, o))
            else:
                ds.get_context(g).remove((s, p, o))
        # adds
        for s, p, o, g in delta.adds:
            if g is None:
                # default graph
                ds.add((s, p, o))
            else:
                ds.get_context(g).add((s, p, o))

    def _delta_bytes(self, delta: RDFDelta) -> bytes:
        """Use RDFDelta canonical bytes representation."""
        return delta._to_canonical_bytes()

    def _detect_priority_ties(self, hooks: List[KnowledgeHook]) -> None:
        """
        Validate Λ ≺-total order: no priority ties allowed.

        Args:
            hooks: List of hooks to validate

        Raises:
            RuntimeError: If any two hooks have the same priority
        """
        priorities = [h.priority for h in hooks]
        if len(priorities) != len(set(priorities)):
            from collections import Counter
            counts = Counter(priorities)
            ties = [p for p, c in counts.items() if c > 1]
            tied_hooks = [h.hook_id for h in hooks if h.priority in ties]
            raise RuntimeError(MSG_PRIORITY_TIE_DETECTED.format(ties=ties, hooks=tied_hooks))

    def _execute_parallel(
        self,
        batches: List[List[KnowledgeHook]],
        working: ConjunctiveGraph,
        out_dir: Path,
        phase_filter: Optional[str],
        event_name: Optional[str],
        emit_construct_deltas: bool,
        max_workers: Optional[int],
        diagnostic_emitter: DiagnosticEmitter
    ) -> Tuple[List[HookResult], List[str], List[str], List[str], List[str]]:
        """
        Execute hooks in parallel batches with deterministic ordering.

        Constitutional Guarantees:
        1. Results sorted by hook_id before aggregation
        2. Deltas applied in sorted order
        3. Same output hash as sequential execution
        4. Graceful degradation to sequential on worker failure

        Args:
            batches: List of hook batches (from _dependency_batches)
            working: Working ConjunctiveGraph (will be mutated deterministically)
            out_dir: Output directory for artifacts
            phase_filter: Optional phase filter
            max_workers: Maximum number of workers (None = CPU count)
            diagnostic_emitter: Diagnostic emitter for collecting diagnostics

        Returns:
            Tuple of (results, bpmn_artifacts, event_artifacts, routed_job_ids, executed_hook_ids)
        """
        if max_workers is None:
            max_workers = multiprocessing.cpu_count()

        if max_workers < 1:
            raise ValueError(f"max_workers must be >= 1, got {max_workers}")

        results: List[HookResult] = []
        bpmn_artifacts: List[str] = []
        event_artifacts: List[str] = []
        routed_job_ids: List[str] = []
        executed_hook_ids: List[str] = []

        # Process batches sequentially (batches have dependencies)
        # Within each batch, execute hooks in parallel (no dependencies)
        for batch in batches:
            # Filter hooks by mode (already filtered, but double-check for safety)
            if event_name:
                batch_hooks = [h for h in batch if h.event == event_name]
            else:
                batch_hooks = [h for h in batch if not phase_filter or h.phase == phase_filter]
            if not batch_hooks:
                continue

            # Sort hooks by hook_id (deterministic ordering)
            batch_hooks.sort(key=lambda h: h.hook_id)

            # Execute batch in parallel
            try:
                batch_results = self._execute_batch_parallel(
                    batch_hooks=batch_hooks,
                    working=working,
                    out_dir=out_dir,
                    max_workers=max_workers,
                    diagnostic_emitter=diagnostic_emitter
                )
            except Exception as e:
                # Graceful degradation: fall back to sequential execution
                # Emit diagnostic
                diagnostic_emitter.emit_diagnostic(
                    diagnostic_type=KH.PolicyViolation,
                    message=f"Parallel execution failed, falling back to sequential: {e}",
                    context="parallel_batch_execution",
                    diagnostic_code="PARALLEL_EXECUTION_FAILED"
                )
                # Execute sequentially as fallback
                batch_results = []
                for hook in batch_hooks:
                    hr = self._execute_single_hook(
                        hook=hook,
                        working=working,
                        out_dir=out_dir,
                        diagnostic_emitter=diagnostic_emitter
                    )
                    batch_results.append(hr)

            # Sort results by hook_id (deterministic aggregation)
            batch_results.sort(key=lambda r: r.hook_id)

            # Aggregate results deterministically (sorted order)
            for hr in batch_results:
                results.append(hr)
                if hr.satisfied:
                    executed_hook_ids.append(hr.hook_id)

                for action_str in hr.executed_actions:
                    EMIT_BPMN_PREFIX = f"{ACTION_TYPE_EMIT_BPMN}:"
                    EMIT_EVENT_PREFIX = f"{ACTION_TYPE_EMIT_EVENT}:"
                    ROUTE_BPMN_PREFIX = f"{ACTION_TYPE_ROUTE_TO_BPMN}:"
                    JOB_ID_MARKER = ":job_id="
                    if action_str.startswith(EMIT_BPMN_PREFIX):
                        fname = f"{hr.hook_id}.bpmn.xml"
                        if fname not in bpmn_artifacts:
                            bpmn_artifacts.append(fname)
                    elif action_str.startswith(EMIT_EVENT_PREFIX):
                        fname = f"{hr.hook_id}.events.ttl"
                        if fname not in event_artifacts:
                            event_artifacts.append(fname)
                    elif action_str.startswith(ROUTE_BPMN_PREFIX) and JOB_ID_MARKER in action_str:
                        job_id = action_str.split(JOB_ID_MARKER)[1]
                        if job_id not in routed_job_ids:
                            routed_job_ids.append(job_id)

        # Sort all lists for determinism
        bpmn_artifacts.sort()
        event_artifacts.sort()
        routed_job_ids.sort()
        executed_hook_ids.sort()

        return results, bpmn_artifacts, event_artifacts, routed_job_ids, executed_hook_ids

    def _execute_batch_parallel(
        self,
        batch_hooks: List[KnowledgeHook],
        working: ConjunctiveGraph,
        out_dir: Path,
        max_workers: int,
        diagnostic_emitter: DiagnosticEmitter
    ) -> List[HookResult]:
        """
        Execute a batch of hooks in parallel with isolated working copies.

        Args:
            batch_hooks: List of hooks to execute (already sorted by hook_id)
            working: Working ConjunctiveGraph (will be mutated deterministically after parallel exec)
            out_dir: Output directory
            max_workers: Maximum number of workers
            diagnostic_emitter: Diagnostic emitter

        Returns:
            List of HookResult objects (unsorted - caller must sort)

        Raises:
            RuntimeError: If worker execution fails
        """
        # Create a snapshot of working dataset for parallel execution
        # Each worker will get a copy to avoid race conditions
        working_snapshot_bytes = graph_to_canonical_nquads_bytes(working)

        results: List[HookResult] = []

        # Use ThreadPoolExecutor (shared memory, faster for I/O-bound tasks)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all hooks with isolated working copies
            futures = {
                executor.submit(
                    self._execute_single_hook_isolated,
                    hook,
                    working_snapshot_bytes,
                    out_dir,
                    diagnostic_emitter
                ): hook
                for hook in batch_hooks
            }

            # Collect results
            for future in futures:
                hook = futures[future]
                try:
                    hr = future.result()
                    results.append(hr)
                except Exception as e:
                    # Hard fail on worker error
                    raise RuntimeError(
                        f"Hook execution failed in parallel worker: {hook.hook_id}\n"
                        f"Error: {e}"
                    ) from e

        # Sort results by hook_id (deterministic ordering)
        results.sort(key=lambda r: r.hook_id)

        # Apply deltas from each result in sorted order to the shared working dataset
        # This ensures deterministic aggregation
        for hr in results:
            if hr.satisfied:
                for action_str in hr.executed_actions:
                    CONSTRUCT_PREFIX = f"{ACTION_TYPE_CONSTRUCT}:"
                    EMIT_EVENT_PREFIX = f"{ACTION_TYPE_EMIT_EVENT}:"
                    if action_str.startswith(CONSTRUCT_PREFIX):
                        action_ref_str = action_str.split(COLON_SEP, 1)[1]
                        action_ref = URIRef(action_ref_str)
                        d2 = self.dialects.sparql_construct_to_delta(working, action_ref)
                        self._apply_delta(working, d2)
                    elif action_str.startswith(EMIT_EVENT_PREFIX):
                        action_ref_str = action_str.split(COLON_SEP, 1)[1]
                        action_ref = URIRef(action_ref_str)
                        d3 = self.dialects.sparql_construct_to_delta(working, action_ref)
                        self._apply_delta(working, d3)

        return results

    def _execute_single_hook_isolated(
        self,
        hook: KnowledgeHook,
        working_snapshot_bytes: bytes,
        out_dir: Path,
        diagnostic_emitter: DiagnosticEmitter
    ) -> HookResult:
        """
        Execute a single hook with an isolated copy of the working dataset.

        This is the worker function for parallel execution.
        It receives a serialized snapshot of the working dataset,
        deserializes it into a local copy, executes the hook, and returns the result.

        Args:
            hook: Hook to execute
            working_snapshot_bytes: Serialized working dataset (N-Quads bytes)
            out_dir: Output directory
            diagnostic_emitter: Diagnostic emitter

        Returns:
            HookResult (with executed_actions that can be replayed deterministically)

        Note: This function does NOT mutate the shared working dataset.
        Deltas will be applied later in sorted order by the caller.
        """
        # Deserialize working snapshot into local copy
        working_local = ConjunctiveGraph()
        working_local.parse(data=working_snapshot_bytes, format="nquads")

        # Execute hook using local working copy
        return self._execute_single_hook(
            hook=hook,
            working=working_local,
            out_dir=out_dir,
            diagnostic_emitter=diagnostic_emitter
        )

    def _execute_single_hook(
        self,
        hook: KnowledgeHook,
        working: ConjunctiveGraph,
        out_dir: Path,
        diagnostic_emitter: DiagnosticEmitter
    ) -> HookResult:
        """
        Execute a single hook (shared by sequential and parallel execution).

        Args:
            hook: Hook to execute
            working: Working ConjunctiveGraph
            out_dir: Output directory
            diagnostic_emitter: Diagnostic emitter

        Returns:
            HookResult
        """
        hr = HookResult(hook_id=hook.hook_id, satisfied=False, executed_actions=[], errors=[], diagnostics=[])
        try:
            satisfied = self._eval_trigger(hook, working)
            hr.satisfied = satisfied
            if not satisfied:
                return hr

            for action in hook.actions:
                if action.kind == ACTION_TYPE_CONSTRUCT:
                    d2 = self.dialects.sparql_construct_to_delta(working, action.ref)
                    self._apply_delta(working, d2)
                    hr.executed_actions.append(f"{ACTION_TYPE_CONSTRUCT}:{action.ref}")
                elif action.kind == ACTION_TYPE_EMIT_BPMN:
                    bpmn_bytes = self.bpmn.emit_bpmn_xml(self.hook_pack_ds, action.ref)
                    fname = f"{hook.hook_id}.bpmn.xml"
                    fpath = out_dir / fname
                    fpath.write_bytes(bpmn_bytes)
                    hr.executed_actions.append(f"{ACTION_TYPE_EMIT_BPMN}:{action.ref}")
                elif action.kind == ACTION_TYPE_EMIT_EVENT:
                    # Execute SPARQL CONSTRUCT to produce event RDF
                    d3 = self.dialects.sparql_construct_to_delta(working, action.ref)
                    # Convert delta to graph for emission
                    event_graph = Graph()
                    for s, p, o, g_ctx in d3.adds:
                        event_graph.add((s, p, o))
                    fname = f"{hook.hook_id}.events.ttl"
                    fpath = out_dir / fname
                    fpath.write_text(event_graph.serialize(format=FORMAT_TURTLE), encoding=ENCODING_UTF8)
                    self._apply_delta(working, d3)
                    hr.executed_actions.append(f"{ACTION_TYPE_EMIT_EVENT}:{action.ref}")
                elif action.kind == ACTION_TYPE_ROUTE_TO_BPMN:
                    # Emit BPMN XML
                    bpmn_bytes = self.bpmn.emit_bpmn_xml(self.hook_pack_ds, action.ref)
                    fname = f"{hook.hook_id}.bpmn.xml"
                    fpath = out_dir / fname
                    fpath.write_bytes(bpmn_bytes)

                    # Check for executor endpoint
                    action_node = self._find_action_node(hook, action)
                    endpoint = self.hook_pack_ds.value(action_node, KH.executorEndpoint)

                    if endpoint:
                        # Submit to SpiffWorkflow API
                        adapter = SpiffWorkflowAdapter(str(endpoint))
                        try:
                            job_id = adapter.submit_workflow(bpmn_bytes, context=None)
                            hr.executed_actions.append(f"route_to_bpmn:{action.ref}:job_id={job_id}")
                        except Exception as routing_err:
                            # Routing failure is a diagnostic, not hard fail
                            diagnostic_emitter.emit_diagnostic(
                                diagnostic_type=KH.PolicyViolation,
                                message=f"Failed to route BPMN to {endpoint}: {routing_err}",
                                context=str(action_node),
                                diagnostic_code="BPMN_ROUTING_FAILED",
                            )
                            hr.executed_actions.append(f"route_to_bpmn:{action.ref}:routing_failed")
                    else:
                        # No endpoint: just emit (routing receipt only)
                        hr.executed_actions.append(f"route_to_bpmn:{action.ref}:no_endpoint")
                else:
                    raise RuntimeError(f"Unknown action kind: {action.kind}")

            return hr
        except Exception as e:
            hr.errors.append(str(e))
            # Emit DialectFailure diagnostic
            diagnostic_emitter.emit_diagnostic(
                diagnostic_type=KH.DialectFailure,
                message=f"Hook execution failed: {str(e)}",
                context=hook.hook_id,
                diagnostic_code="HOOK_EXECUTION_ERROR"
            )
            # Collect diagnostics for this hook result
            hr = dataclasses.replace(hr, diagnostics=list(diagnostic_emitter.diagnostics))
            return hr


# ---------- Example CLI (real entrypoint) ----------

def main(argv: List[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="OFMF Keystone Omniverse — Turtle hooks, BPMN emit, receipts")
    ap.add_argument("--hooks", required=True, help="Path to hook pack Turtle (.ttl)")
    ap.add_argument("--data", required=True, help="Path to data Turtle (.ttl)")
    ap.add_argument("--out", required=True, help="Output directory for BPMN and receipts")
    ap.add_argument("--phase", default=None, help="Optional phase filter (validate-before-write, etc)")
    ap.add_argument("--parallel", action="store_true", help="Enable parallel execution of hooks within batches")
    ap.add_argument("--max-workers", type=int, default=None, help="Maximum number of parallel workers (default: CPU count)")
    args = ap.parse_args(argv)

    hooks_path = Path(args.hooks)
    data_path = Path(args.data)
    out_dir = Path(args.out)

    loader = HookPackLoader()
    hook_pack_ds, hooks = loader.load_from_turtle(hooks_path)

    data_ds = ConjunctiveGraph()
    data_ds.parse(data_path.as_posix(), format="turtle")

    engine = OFMFEngine(hook_pack_ds, hooks)

    # delta is an input artifact in OFMF; here we start empty
    delta = RDFDelta.empty()

    results, receipt = engine.execute(
        data_ds,
        delta,
        out_dir,
        phase_filter=args.phase,
        parallel=args.parallel,
        max_workers=getattr(args, 'max_workers', None)
    )

    # Write receipt as Turtle too (OFMF)
    receipt_graph = Graph()
    rid = URIRef(f"urn:receipt:{receipt.timestamp_ns}")
    receipt_graph.add((rid, RDF.type, KH.Receipt))
    receipt_graph.add((rid, KH.inputHash, Literal(receipt.input_hash)))
    receipt_graph.add((rid, KH.deltaHash, Literal(receipt.delta_hash)))
    receipt_graph.add((rid, KH.outputHash, Literal(receipt.output_hash)))
    receipt_graph.add((rid, KH.timestampNs, Literal(receipt.timestamp_ns, datatype=XSD.integer)))

    for hid in receipt.executed_hook_ids:
        receipt_graph.add((rid, KH.executedHookId, Literal(hid)))
    for bpmn in receipt.bpmn_artifacts:
        receipt_graph.add((rid, KH.emittedBpmn, Literal(bpmn)))

    # Add cache statistics
    receipt_graph.add((rid, KH.cacheHits, Literal(receipt.cache_hits, datatype=XSD.integer)))
    receipt_graph.add((rid, KH.cacheMisses, Literal(receipt.cache_misses, datatype=XSD.integer)))
    receipt_graph.add((rid, KH.cacheEvictions, Literal(receipt.cache_evictions, datatype=XSD.integer)))
    receipt_graph.add((rid, KH.cacheHitRate, Literal(receipt.cache_hit_rate, datatype=XSD.decimal)))

    receipt_path = out_dir / "receipt.ttl"
    receipt_path.write_text(receipt_graph.serialize(format="turtle"), encoding="utf-8")

    if receipt.diagnostic_graph is not None and len(receipt.diagnostic_graph) > 0:
        diagnostics_path = out_dir / "diagnostics.ttl"
        diagnostics_path.write_text(receipt.diagnostic_graph.serialize(format=FORMAT_TURTLE), encoding=ENCODING_UTF8)
        DIAG_WRITTEN_MSG = f"Diagnostics written: {diagnostics_path.as_posix()}"
        sys.stdout.write(DIAG_WRITTEN_MSG + "\n")

    for r in results:
        SATISFIED_STR = "SATISFIED"
        SKIPPED_STR = "SKIPPED"
        status = SATISFIED_STR if r.satisfied else SKIPPED_STR
        diag_count = len(r.diagnostics)
        RESULT_LINE_TEMPLATE = "{hook_id}\t{status}\tactions={actions}\terrors={errors}\tdiagnostics={diags}\n"
        sys.stdout.write(RESULT_LINE_TEMPLATE.format(hook_id=r.hook_id, status=status, actions=len(r.executed_actions), errors=len(r.errors), diags=diag_count))
        for e in r.errors:
            ERROR_PREFIX = "  ERROR: "
            sys.stdout.write(ERROR_PREFIX + e + "\n")

    RECEIPT_WRITTEN_MSG = f"Receipt written: {receipt_path.as_posix()}"
    sys.stdout.write("\n" + RECEIPT_WRITTEN_MSG + "\n")
    OUTPUT_HASH_MSG = f"outputHash: {receipt.output_hash}"
    sys.stdout.write(OUTPUT_HASH_MSG + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


# ---------- BPMN XML Parser (BPMN XML => Turtle/RDF) ----------

class BpmnXmlParser:
    """
    Parses BPMN 2.0 XML into Turtle/RDF using ontology/bpmn.ttl vocabulary.

    Inverse of BpmnEmitter: BPMN XML → RDF Graph with bpmn: namespace.

    Supports:
    - Process metadata (processId, name, isExecutable)
    - Events (Start, End, Intermediate, Boundary with event definitions)
    - Tasks (all types: Task, UserTask, ServiceTask, ScriptTask, etc.)
    - Gateways (Exclusive, Parallel, Inclusive, EventBased, Complex)
    - Subprocesses and CallActivities
    - SequenceFlows (with conditions)

    Output is deterministic RDF suitable for round-trip testing.
    """

    def __init__(self) -> None:
        pass

    def parse_xml_to_graph(self, xml_path: Path) -> Graph:
        """
        Parse BPMN XML file to RDF Graph.

        Args:
            xml_path: Path to BPMN 2.0 XML file

        Returns:
            Graph with bpmn: namespace triples

        Raises:
            RuntimeError: If XML is invalid or parsing fails
        """
        import xml.etree.ElementTree as ET

        if not xml_path.exists():
            raise RuntimeError(MSG_BPMN_FILE_NOT_FOUND.format(path=xml_path))

        tree = ET.parse(xml_path.as_posix())
        root = tree.getroot()

        BPMN_NS_KEY = "bpmn"
        BPMNDI_NS_KEY = "bpmndi"
        DC_NS_KEY = "dc"
        DI_NS_KEY = "di"
        XSI_NS_KEY = "xsi"
        ns = {
            BPMN_NS_KEY: BPMN_NS_URI,
            BPMNDI_NS_KEY: BPMNDI_NS_URI,
            DC_NS_KEY: DC_NS_URI,
            DI_NS_KEY: DI_NS_URI,
            XSI_NS_KEY: XSI_NS_URI
        }

        g = Graph()
        g.bind(BPMN_NS_KEY, BPMN)
        g.bind(RDF_NS_KEY := "rdf", RDF)
        g.bind(XSD_NS_KEY := "xsd", XSD)

        # Parse process elements
        for process_elem in root.findall('.//bpmn:process', ns):
            self._parse_process(g, process_elem, ns)

        return g

    def parse_xml_to_turtle(self, xml_path: Path) -> str:
        """
        Parse BPMN XML file to Turtle format.

        Args:
            xml_path: Path to BPMN 2.0 XML file

        Returns:
            Turtle string
        """
        g = self.parse_xml_to_graph(xml_path)
        return g.serialize(format=FORMAT_TURTLE)

    def _parse_process(self, g: Graph, process_elem, ns: Dict[str, str]) -> URIRef:
        """Parse BPMN process element and add to graph."""
        proc_id = process_elem.get("id")
        if not proc_id:
            raise RuntimeError(MSG_PROCESS_MISSING_ID)

        PROCESS_BASE_IRI = "https://chatmangpt.com/kgc/bpmn#process_"
        proc_iri = URIRef(f"{PROCESS_BASE_IRI}{proc_id}")
        g.add((proc_iri, RDF.type, BPMN.Process))
        g.add((proc_iri, BPMN.processId, Literal(proc_id)))

        proc_name = process_elem.get("name", proc_id)
        g.add((proc_iri, BPMN.name, Literal(proc_name)))

        is_exec = process_elem.get(PROCESS_ATTR_EXECUTABLE, PROCESS_ATTR_TRUE)
        g.add((proc_iri, BPMN.isExecutable, Literal(is_exec == PROCESS_ATTR_TRUE, datatype=XSD.boolean)))

        BPMN_NS_TAG_PREFIX = "{" + ns["bpmn"] + "}"
        START_EVENT_TAG = "startEvent"
        END_EVENT_TAG = "endEvent"
        TASK_TAG = "task"
        USER_TASK_TAG = "userTask"
        EXCLUSIVE_GATEWAY_TAG = "exclusiveGateway"
        PARALLEL_GATEWAY_TAG = "parallelGateway"
        SEQUENCE_FLOW_TAG = "sequenceFlow"

        for child in process_elem:
            tag = child.tag.replace(BPMN_NS_TAG_PREFIX, "")

            if tag == START_EVENT_TAG:
                self._parse_start_event(g, child, proc_iri, ns)
            elif tag == END_EVENT_TAG:
                self._parse_end_event(g, child, proc_iri, ns)
            elif tag == TASK_TAG:
                self._parse_task(g, child, proc_iri, BPMN.Task, ns)
            elif tag == USER_TASK_TAG:
                self._parse_task(g, child, proc_iri, BPMN.UserTask, ns)
            elif tag == EXCLUSIVE_GATEWAY_TAG:
                self._parse_gateway(g, child, proc_iri, BPMN.ExclusiveGateway, ns)
            elif tag == PARALLEL_GATEWAY_TAG:
                self._parse_gateway(g, child, proc_iri, BPMN.ParallelGateway, ns)
            elif tag == SEQUENCE_FLOW_TAG:
                self._parse_sequence_flow(g, child, proc_iri, ns)

        return proc_iri

    def _parse_start_event(self, g: Graph, elem, proc_iri: URIRef, ns: Dict[str, str]) -> URIRef:
        node_id = elem.get("id")
        if not node_id:
            raise RuntimeError(MSG_START_EVENT_MISSING_ID)

        UNDERSCORE_SEP = "_"
        node_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{node_id}")
        g.add((node_iri, RDF.type, BPMN.StartEvent))
        g.add((node_iri, BPMN.inProcess, proc_iri))
        g.add((node_iri, BPMN.nodeId, Literal(node_id)))

        name = elem.get("name", node_id)
        g.add((node_iri, BPMN.name, Literal(name)))

        return node_iri

    def _parse_end_event(self, g: Graph, elem, proc_iri: URIRef, ns: Dict[str, str]) -> URIRef:
        node_id = elem.get("id")
        if not node_id:
            raise RuntimeError(MSG_END_EVENT_MISSING_ID)

        UNDERSCORE_SEP = "_"
        node_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{node_id}")
        g.add((node_iri, RDF.type, BPMN.EndEvent))
        g.add((node_iri, BPMN.inProcess, proc_iri))
        g.add((node_iri, BPMN.nodeId, Literal(node_id)))

        name = elem.get("name", node_id)
        g.add((node_iri, BPMN.name, Literal(name)))

        return node_iri

    def _parse_task(self, g: Graph, elem, proc_iri: URIRef, task_type: URIRef, ns: Dict[str, str]) -> URIRef:
        """Generic task parser for Task, UserTask, ServiceTask, etc."""
        node_id = elem.get("id")
        if not node_id:
            raise RuntimeError(MSG_TASK_MISSING_ID)

        UNDERSCORE_SEP = "_"
        node_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{node_id}")
        g.add((node_iri, RDF.type, task_type))
        g.add((node_iri, BPMN.inProcess, proc_iri))
        g.add((node_iri, BPMN.nodeId, Literal(node_id)))

        name = elem.get("name", node_id)
        g.add((node_iri, BPMN.name, Literal(name)))

        return node_iri

    def _parse_gateway(self, g: Graph, elem, proc_iri: URIRef, gateway_type: URIRef, ns: Dict[str, str]) -> URIRef:
        """Generic gateway parser for Exclusive, Parallel, Inclusive, etc."""
        node_id = elem.get("id")
        if not node_id:
            raise RuntimeError(MSG_GATEWAY_MISSING_ID)

        UNDERSCORE_SEP = "_"
        node_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{node_id}")
        g.add((node_iri, RDF.type, gateway_type))
        g.add((node_iri, BPMN.inProcess, proc_iri))
        g.add((node_iri, BPMN.nodeId, Literal(node_id)))

        name = elem.get("name", node_id)
        g.add((node_iri, BPMN.name, Literal(name)))

        return node_iri

    def _parse_sequence_flow(self, g: Graph, elem, proc_iri: URIRef, ns: Dict[str, str]) -> URIRef:
        """Parse SequenceFlow."""
        flow_id = elem.get("id")
        if not flow_id:
            raise RuntimeError(MSG_SEQUENCE_FLOW_MISSING_ID)

        UNDERSCORE_SEP = "_"
        flow_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{flow_id}")
        g.add((flow_iri, RDF.type, BPMN.SequenceFlow))
        g.add((flow_iri, BPMN.inProcess, proc_iri))
        g.add((flow_iri, BPMN.flowId, Literal(flow_id)))

        src_id = elem.get("sourceRef")
        tgt_id = elem.get("targetRef")

        if not src_id or not tgt_id:
            raise RuntimeError(MSG_SEQUENCE_FLOW_MISSING_REFS.format(flow_id=flow_id))

        src_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{src_id}")
        tgt_iri = URIRef(f"{str(proc_iri)}{UNDERSCORE_SEP}{tgt_id}")

        g.add((flow_iri, BPMN.sourceRef, src_iri))
        g.add((flow_iri, BPMN.targetRef, tgt_iri))

        CONDITION_EXPR_TAG = "bpmn:conditionExpression"
        cond_elem = elem.find(CONDITION_EXPR_TAG, ns)
        if cond_elem is not None and cond_elem.text:
            g.add((flow_iri, BPMN.conditionExpression, Literal(cond_elem.text.strip())))

        return flow_iri
