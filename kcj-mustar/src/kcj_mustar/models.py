"""Pydantic Models and Enums for KCJ Autonomic System constants, state configurations, and receipts."""

from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    ANDON_STOP = "ANDON_STOP"
    FAILED = "FAILED"
    PASSED = "PASSED"


class SystemConstants:
    CACHE_DIR = Path("/Users/sac/turbo-fieldfare/kcj-mustar/scratch/cache")
    GEMMA_API_BASE = "http://127.0.0.1:8080/v1"
    GEMMA_MODEL_ID = "openai/gemma-4-26b-a4b-it"
    API_KEY_NONE = "none"
    ENCODING_UTF8 = "utf-8"
    DEFAULT_PLAN_ID = "plan-001"
    
    # Cache limits
    DISK_SIZE_LIMIT_BYTES = 104857600  # 100 MB
    MEMORY_MAX_ENTRIES = 10000
    
    # LM hyper-parameters
    DEFAULT_TEMPERATURE = 0.2
    DEFAULT_MAX_TOKENS = 4096


class AutonomicCycleInput(BaseModel):
    state: str = Field(default="cluster_idle", description="Initial state tag")
    dirty_tree: bool = Field(default=False, description="Git dirty tree flag")
    build_passed: bool = Field(default=True, description="Build verification flag")
    use_gemma: bool = Field(default=True, description="Local Gemma server connection flag")


class AutonomicCycleResult(BaseModel):
    status: ExecutionStatus
    receipt: str | None = None
    strategy: dict | None = None
    quality: dict | None = None
    dispatch: dict | None = None


class CombinatorialMaximalismMetrics(BaseModel):
    total_nodes: int
    total_edges: int
    num_stages: int
    workers_per_stage: int
    theoretical_state_space: str


class POWLPlanResult(BaseModel):
    scenario: str
    combinatorial_maximalism: CombinatorialMaximalismMetrics
    powl_model_type: str
    bpmn_xml_bytes: int
    bpmn_file: str
    spiff_workflow_completed: bool
    spiff_completed_tasks_count: int
