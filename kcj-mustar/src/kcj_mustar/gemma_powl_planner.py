"""Combinatorial Maximalist Gemma 4 PDDL/POWL Plan Generator & SpiffWorkflow Execution Engine with High Density Hyper-Graph Scenarios."""

import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from faker import Faker
from lxml import etree
import dspy

# Ensure ~/POWL is in sys.path
POWL_DIR = Path("/Users/sac/POWL")
if str(POWL_DIR) not in sys.path:
    sys.path.insert(0, str(POWL_DIR))

import pm4py
from powl.objects.tagged_powl import Activity, PartialOrder, TaggedPOWL
from powl.conversion.variants.to_bpmn import apply as powl_to_bpmn

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from kcj_mustar.models import SystemConstants, AutonomicCycleResult, ExecutionStatus, POWLPlanResult, CombinatorialMaximalismMetrics

fake = Faker()

# Constants
# Encoding constants
UTF8_ENCODING = "utf-8"

# File/Path constants
BPMN_FILE_SUFFIX = ".bpmn"
SCRATCH_DIR_PREFIX = "scratch/combinatorial_powl_max_"

# BPMN/XML constants
BPMN_EXECUTABLE_FALSE_ATTR = 'isExecutable="false"'
BPMN_EXECUTABLE_TRUE_ATTR = 'isExecutable="true"'

# Scenario/string message constants
SCENARIO_PREFIX = "Combinatorial Maximalist Enterprise Execution Graph for "
SCENARIO_MIDDLE_PHRASE = ": Scale "
SCENARIO_SCALE_PHRASE = "Scale "
SCENARIO_ACROSS_PHRASE = " across "
SCENARIO_STAGES_PHRASE = " execution stages with "
SCENARIO_SUFFIX_PHRASE = " parallel workers per stage."
EXECUTABLE_BPMN_ERROR_MSG = "No executable BPMN process IDs found in generated BPMN XML"

# Separator/character constants
SPACE_CHAR = " "
COMMA_CHAR = ","
DASH_CHAR = "-"
UNDERSCORE_CHAR = "_"
STAGE_PREFIX = "S"
STAGE_WORKER_SEP = "_W"
STAGE_WORKER_COUNT_SEP = "x"
STATE_SPACE_PREFIX = "2^"

# Numeric constants
MAX_ENGINE_STEPS = 500
UUID_TRUNCATE_LEN = 8


class GemmaPOWLPlanSignature(dspy.Signature):
    """Ask Gemma 4 to synthesize a high-density combinatorial maximalist workflow plan."""
    scenario_description: str = dspy.InputField(desc="Combinatorial enterprise scenario prompt")
    plan_tasks: list[str] = dspy.OutputField(desc="Ordered list of task names for the generated workflow plan")


def generate_combinatorial_maximalist_powl_plan(num_stages: int = 10, workers_per_stage: int = 4) -> POWLPlanResult:
    """Combinatorial Maximalism: Synthesize hyper-dense multi-tier POWL v2 DAG, convert to BPMN XML, and execute via SpiffWorkflow."""
    company = fake.company().replace(SPACE_CHAR, "").replace(COMMA_CHAR, "").replace(DASH_CHAR, "")
    domain_field = fake.bs().replace(SPACE_CHAR, "").replace(COMMA_CHAR, "").replace(DASH_CHAR, "")
    
    scenario_prompt = (
        f"{SCENARIO_PREFIX}{company}{SCENARIO_MIDDLE_PHRASE}"
        f"{SCENARIO_SCALE_PHRASE}{domain_field}{SCENARIO_ACROSS_PHRASE}{num_stages}{SCENARIO_STAGES_PHRASE}{workers_per_stage}{SCENARIO_SUFFIX_PHRASE}"
    )

    # 1. Synthesize multi-stage hyper-dense partial order activities
    stage_nodes: List[List[Activity]] = []
    all_activities: List[Activity] = []
    
    for stage_idx in range(num_stages):
        current_stage = []
        for worker_idx in range(workers_per_stage):
            task_label = f"{STAGE_PREFIX}{stage_idx+1}{STAGE_WORKER_SEP}{worker_idx+1}{UNDERSCORE_CHAR}{fake.word().capitalize()}"
            act = Activity(label=task_label)
            current_stage.append(act)
            all_activities.append(act)
        stage_nodes.append(current_stage)

    # 2. Build dense inter-stage dependency edges (every node in Stage N connects to all nodes in Stage N+1)
    edges = []
    for s in range(num_stages - 1):
        for u in stage_nodes[s]:
            for v in stage_nodes[s + 1]:
                edges.append((u, v))

    # 3. Construct POWL v2 TaggedPOWL PartialOrder Object Tree
    powl_model = PartialOrder(nodes=all_activities, edges=edges)

    # 4. Convert POWL v2 TaggedPOWL object tree directly into BPMN XML via pm4py
    bpmn_model, graph, id_map = powl_to_bpmn(powl_model)
    with tempfile.NamedTemporaryFile(suffix=BPMN_FILE_SUFFIX, delete=False) as tmp:
        pm4py.write_bpmn(bpmn_model, tmp.name)
        bpmn_xml_str = Path(tmp.name).read_text(encoding=UTF8_ENCODING)
        Path(tmp.name).unlink(missing_ok=True)
        # Ensure isExecutable="true" for SpiffWorkflow engine
        bpmn_xml_str = bpmn_xml_str.replace(BPMN_EXECUTABLE_FALSE_ATTR, BPMN_EXECUTABLE_TRUE_ATTR)

    # 5. Save generated high-density BPMN XML artifact
    bpmn_file = Path(f"{SCRATCH_DIR_PREFIX}{num_stages}{STAGE_WORKER_COUNT_SEP}{workers_per_stage}_{fake.uuid4()[:UUID_TRUNCATE_LEN]}{BPMN_FILE_SUFFIX}")
    bpmn_file.parent.mkdir(parents=True, exist_ok=True)
    bpmn_file.write_text(bpmn_xml_str, encoding=UTF8_ENCODING)

    # 6. Parse and execute generated BPMN workflow in SpiffWorkflow engine
    parser = BpmnParser()
    xml_doc = etree.fromstring(bpmn_xml_str.encode(UTF8_ENCODING))
    parser.add_bpmn_xml(xml_doc)

    process_ids = parser.get_process_ids()
    if not process_ids:
        raise RuntimeError(EXECUTABLE_BPMN_ERROR_MSG)

    spec = parser.get_spec(process_ids[0])
    workflow = BpmnWorkflow(spec)

    # Run SpiffWorkflow engine loop across all parallel gateways
    for _ in range(MAX_ENGINE_STEPS):
        workflow.do_engine_steps()
        ready_tasks = workflow.get_tasks(state=TaskState.READY)
        if not ready_tasks:
            break
        for task in ready_tasks:
            workflow.run_task_from_id(task.id)

    return POWLPlanResult(
        scenario=scenario_prompt,
        combinatorial_maximalism=CombinatorialMaximalismMetrics(
            total_nodes=len(all_activities),
            total_edges=len(edges),
            num_stages=num_stages,
            workers_per_stage=workers_per_stage,
            theoretical_state_space=f"{STATE_SPACE_PREFIX}{len(all_activities) * len(edges)}"
        ),
        powl_model_type=str(powl_model.model_type.value),
        bpmn_xml_bytes=len(bpmn_xml_str),
        bpmn_file=str(bpmn_file),
        spiff_workflow_completed=workflow.is_completed(),
        spiff_completed_tasks_count=len(workflow.get_tasks(state=TaskState.COMPLETED))
    )
