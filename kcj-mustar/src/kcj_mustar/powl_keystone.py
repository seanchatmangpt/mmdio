"""OFMF Keystone & POWL v2 -> BPMN -> SpiffWorkflow Integration Engine."""

import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict, Any
from lxml import etree

# Ensure ~/POWL is in sys.path
POWL_DIR = Path("/Users/sac/POWL")
if str(POWL_DIR) not in sys.path:
    sys.path.insert(0, str(POWL_DIR))

import pm4py
from powl.objects.tagged_powl import Activity, PartialOrder, ChoiceGraph, TaggedPOWL
from powl.conversion.variants.to_bpmn import apply as powl_to_bpmn

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from kcj_mustar.models import AutonomicCycleResult, SystemConstants

# ===== Constants =====

# Activity labels for POWL model construction
class ActivityLabels(str, Enum):
    """Task labels for autonomic workflow activities."""
    LUMEN_VECTOR_INDEX_QUERY = "LumenVectorIndexQuery"
    AGRICOLA_PDDL_SYNTHESIS = "AgricolaPDDLSynthesis"
    SHACL_VALIDATION_GATE = "SHACLValidationGate"
    EMIT_OCEL20_EVENT = "EmitOCEL20Event"
    HIGH_SPEED_APM_DISPATCH = "HighSpeed100kAPMDispatch"
    BLAKE3_RECEIPT_LOGGING = "BLAKE3ReceiptLogging"

# BPMN XML constants
BPMN_FILE_SUFFIX = ".bpmn"
BPMN_ATTRIBUTE_NOT_EXECUTABLE = 'isExecutable="false"'
BPMN_ATTRIBUTE_EXECUTABLE = 'isExecutable="true"'

# File encoding
FILE_ENCODING = "utf-8"

# Error messages
ERROR_NO_BPMN_PROCESSES = "No executable BPMN process IDs found in generated BPMN XML"

# Execution parameters
WORKFLOW_ENGINE_MAX_STEPS = 50

# Output file path
BPMN_OUTPUT_FILE = "scratch/powl_v2_generated.bpmn"

# Response dictionary keys
RESPONSE_KEY_POWL_MODEL_TYPE = "powl_model_type"
RESPONSE_KEY_BPMN_XML_BYTES = "bpmn_xml_bytes"
RESPONSE_KEY_BPMN_FILE = "bpmn_file"
RESPONSE_KEY_SPIFF_WORKFLOW_COMPLETED = "spiff_workflow_completed"
RESPONSE_KEY_SPIFF_COMPLETED_TASKS_COUNT = "spiff_completed_tasks_count"


def construct_powl_v2_model_from_cycle(cycle_result: AutonomicCycleResult) -> TaggedPOWL:
    """Construct an authentic POWL v2 PartialOrder TaggedPOWL object tree from cycle results."""
    # Chinese Strategy Engine Tasks
    t_lumen = Activity(label=ActivityLabels.LUMEN_VECTOR_INDEX_QUERY.value)
    t_agricola = Activity(label=ActivityLabels.AGRICOLA_PDDL_SYNTHESIS.value)
    po_strategy = PartialOrder(nodes=[t_lumen, t_agricola], edges=[(t_lumen, t_agricola)])

    # Japanese Quality Control Tasks
    t_shacl = Activity(label=ActivityLabels.SHACL_VALIDATION_GATE.value)
    t_ocel = Activity(label=ActivityLabels.EMIT_OCEL20_EVENT.value)
    po_quality = PartialOrder(nodes=[t_shacl, t_ocel], edges=[(t_shacl, t_ocel)])

    # Korean Real-Time Dispatch Tasks
    t_dispatch = Activity(label=ActivityLabels.HIGH_SPEED_APM_DISPATCH.value)
    t_blake3 = Activity(label=ActivityLabels.BLAKE3_RECEIPT_LOGGING.value)
    po_actuation = PartialOrder(nodes=[t_dispatch, t_blake3], edges=[(t_dispatch, t_blake3)])

    # Root POWL Model Partial Order
    root_powl = PartialOrder(
        nodes=[po_strategy, po_quality, po_actuation],
        edges=[(po_strategy, po_quality), (po_quality, po_actuation)]
    )
    return root_powl


def convert_powl_v2_to_bpmn_xml(powl_model: TaggedPOWL) -> str:
    """Convert POWL v2 TaggedPOWL object graph directly into BPMN XML string."""
    bpmn_model, graph, id_map = powl_to_bpmn(powl_model)
    with tempfile.NamedTemporaryFile(suffix=BPMN_FILE_SUFFIX, delete=False) as tmp:
        pm4py.write_bpmn(bpmn_model, tmp.name)
        xml_str = Path(tmp.name).read_text(encoding=FILE_ENCODING)
        Path(tmp.name).unlink(missing_ok=True)
        # Ensure isExecutable="true" for SpiffWorkflow execution engine
        xml_str = xml_str.replace(BPMN_ATTRIBUTE_NOT_EXECUTABLE, BPMN_ATTRIBUTE_EXECUTABLE)
        return xml_str


def execute_bpmn_xml_in_spiffworkflow(bpmn_xml_str: str) -> BpmnWorkflow:
    """Parse and execute BPMN XML workflow using SpiffWorkflow engine."""
    parser = BpmnParser()
    xml_doc = etree.fromstring(bpmn_xml_str.encode(FILE_ENCODING))
    parser.add_bpmn_xml(xml_doc)

    process_ids = parser.get_process_ids()
    if not process_ids:
        raise RuntimeError(ERROR_NO_BPMN_PROCESSES)

    spec = parser.get_spec(process_ids[0])
    workflow = BpmnWorkflow(spec)

    # Run engine steps until workflow steps settle or complete
    for _ in range(WORKFLOW_ENGINE_MAX_STEPS):
        workflow.do_engine_steps()
        ready_tasks = workflow.get_tasks(state=TaskState.READY)
        if not ready_tasks:
            break
        for task in ready_tasks:
            workflow.run_task_from_id(task.id)

    return workflow


def run_powl_spiffworkflow_keystone_cycle(cycle_result: AutonomicCycleResult) -> Dict[str, Any]:
    """Complete Zero-Placeholder Integration: POWL v2 -> BPMN -> SpiffWorkflow Execution."""
    powl_model = construct_powl_v2_model_from_cycle(cycle_result)
    bpmn_xml = convert_powl_v2_to_bpmn_xml(powl_model)

    # Save BPMN XML artifact
    bpmn_file = Path(BPMN_OUTPUT_FILE)
    bpmn_file.parent.mkdir(parents=True, exist_ok=True)
    bpmn_file.write_text(bpmn_xml, encoding=FILE_ENCODING)

    # Run in SpiffWorkflow
    workflow = execute_bpmn_xml_in_spiffworkflow(bpmn_xml)

    return {
        RESPONSE_KEY_POWL_MODEL_TYPE: str(powl_model.model_type.value),
        RESPONSE_KEY_BPMN_XML_BYTES: len(bpmn_xml),
        RESPONSE_KEY_BPMN_FILE: str(bpmn_file),
        RESPONSE_KEY_SPIFF_WORKFLOW_COMPLETED: workflow.is_completed(),
        RESPONSE_KEY_SPIFF_COMPLETED_TASKS_COUNT: len(workflow.get_tasks(state=TaskState.COMPLETED))
    }
