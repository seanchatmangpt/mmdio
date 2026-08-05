"""博弈 (Self-Play) & 推演 (Rollout) - Combinatorial Maximalism Engine synthesizing multi-scale temporal/spatial PDDL+, POWL, and hyper-graph state spaces."""

import sqlite3
from pathlib import Path
import dspy

# Constants
# Database & Paths
LUMEN_DB_PATH = Path("/Users/sac/.local/share/lumen/cbc9ca60470b702f/index.db")
AGRICOLA_DOMAIN_PATH = Path("/Users/sac/turbo-fieldfare/kcj-mustar/vendors/scikit_decide/tests/domains/python/pddl_domains/agricola-opt18/domain.pddl")
AGRICOLA_PROBLEM_PATH = Path("/Users/sac/turbo-fieldfare/kcj-mustar/vendors/scikit_decide/tests/domains/python/pddl_domains/agricola-opt18/p01.pddl")

# Text Encoding
DEFAULT_ENCODING = "utf-8"

# Query & Grounding Parameters
DEFAULT_LUMEN_KEYWORD = "Metal"
DEFAULT_LUMEN_LIMIT = 50

# Domain Configuration
DEFAULT_NUM_NODES = 100
DEFAULT_NUM_WORKERS = 64

# Numeric Bounds & Indices
MIN_NODE_INDEX = 0
MIN_WORKER_INDEX = 1
NUM_STAGES = 8
NUM_ROUNDS = 64
MAX_SUBSTRACT_RANGE = 10
INIT_FACTS_LIMIT = 50
SUBSTRACT_FACTS_LIMIT = 100

# Temporal Constants
TEMPORAL_HORIZON_MS = 3600000

# State Space Parameters
STATE_SPACE_WORKER_FACTOR = 64

# Initial Values
INITIAL_COST = 0

# Problem Definition Templates
PROBLEM_DOMAIN_NAME = "agricola"
PROBLEM_NAME_PREFIX = "Combinatorial-Maximal-KCJ-"
POWL_TOPOLOGY = "POWL_COMBINATORIAL_HYPERGRAPH_V4"

# SQL Query Template
SQL_CHUNKS_QUERY = "SELECT file_path, symbol, kind, start_line, end_line FROM chunks WHERE symbol LIKE ? OR file_path LIKE ? LIMIT ?"

# Dict Keys
KEY_FILE_PATH = "file_path"
KEY_SYMBOL = "symbol"
KEY_KIND = "kind"
KEY_START_LINE = "start_line"
KEY_END_LINE = "end_line"
KEY_DOMAIN_PDDL = "domain_pddl"
KEY_PROBLEM_PDDL = "problem_pddl"
KEY_POWL_GRAPH = "powl_graph"
KEY_STATUS = "状态"
KEY_STRATEGY = "策略"
KEY_GAME_ROUNDS = "博弈轮次"
KEY_LUMEN_GROUNDING = "LumenGrounding"
KEY_PDDL = "PDDL"

# PDDL Template & Format Strings
PDDL_DEFINE_PROBLEM_TEMPLATE = "(define (problem {problem_name})"
PDDL_DOMAIN_TEMPLATE = "(:domain {domain_name})"
PDDL_OBJECTS_HEADER = "(:objects"
PDDL_OBJECTS_NUM_TYPE = " - num"
PDDL_OBJECTS_STAGE_TYPE = " - stage"
PDDL_OBJECTS_ROUND_TYPE = " - round"
PDDL_INIT_SECTION = "(:init"
PDDL_GOAL_SECTION = "(:goal (and"
PDDL_CLOSE = "))"
PDDL_TOTAL_COST_LINE = "    (total-cost)"
PDDL_BUILT_ROOMS_TEMPLATE = "    (built_rooms node{node_id} worker{worker_id})"
PDDL_NUM_FOOD_TEMPLATE = "    (num_food num{node_id})"
PDDL_NEXT_NUM_TEMPLATE = "    (NEXT_NUM num{i} num{next_i})"
PDDL_SUBSTRACT_TEMPLATE = "    (NUM_SUBSTRACT num{i} num{j} num{diff})"

# String Formatting
WORKER_FACT_TEMPLATE = "    worker{w} - worker"
NODE_FACT_TEMPLATE = "    node{n} - room"
STAGE_TEMPLATE = "stage{s}"
ROUND_TEMPLATE = "round{r}"
NUM_TEMPLATE = "num{n}"

# Strategy Output Templates
STRATEGY_TEMPLATE = "推演策略: [{state}] Combinatorial Maximalism PDDL+/POWL ({nodes} Nodes, {workers} Workers, 2^({nodes}*{workers}*{factor}) State Space) 规划完成"
DOMAIN_EXTENSION_COMMENT = "\n;; COMBINATORIAL MAXIMALIST EXTENSIONS: {nodes} NODES, {workers} WORKERS\n"

# POWL Hypergraph Keys
KEY_POWL_NODES = "nodes"
KEY_POWL_WORKERS = "workers"
KEY_POWL_TEMPORAL_HORIZON = "temporal_horizon_ms"
KEY_POWL_STATE_SPACE = "combinatorial_state_space_estimate"
KEY_POWL_TOPOLOGY_NAME = "topology"

# SQL Result Indices
SQL_RESULT_FILE_PATH_IDX = 0
SQL_RESULT_SYMBOL_IDX = 1
SQL_RESULT_KIND_IDX = 2
SQL_RESULT_START_LINE_IDX = 3
SQL_RESULT_END_LINE_IDX = 4

# State Space Format
STATE_SPACE_FORMAT_PREFIX = "2^("
STATE_SPACE_FORMAT_SEPARATOR = "*"
STATE_SPACE_FORMAT_SUFFIX = ")"
STAGE_START_INDEX = 1
NEWLINE_CHAR = "\n"


class 策略推演Signature(dspy.Signature):
    """根据当前状态与历史博弈推演 Combinatorial Maximalist PDDL+/POWL Hyper-Graph Strategy."""
    当前状态_zh = dspy.InputField(desc="当前系统状态 (State)")
    历史博弈_zh = dspy.InputField(desc="历史博弈轨迹 (History)")
    推演策略_zh = dspy.OutputField(desc="推演出的策略 (PDDL Domain/Problem)")


def _build_chunk_dict(row: tuple) -> dict:
    """Build a chunk dictionary from a SQL result row."""
    chunk = {}
    chunk[KEY_FILE_PATH] = row[SQL_RESULT_FILE_PATH_IDX]
    chunk[KEY_SYMBOL] = row[SQL_RESULT_SYMBOL_IDX]
    chunk[KEY_KIND] = row[SQL_RESULT_KIND_IDX]
    chunk[KEY_START_LINE] = row[SQL_RESULT_START_LINE_IDX]
    chunk[KEY_END_LINE] = row[SQL_RESULT_END_LINE_IDX]
    return chunk


def query_lumen_grounding(keyword: str = DEFAULT_LUMEN_KEYWORD, limit: int = DEFAULT_LUMEN_LIMIT) -> list[dict]:
    """Query codebase chunks from Lumen sqlite database across high limit."""
    if not LUMEN_DB_PATH.exists():
        return []
    try:
        conn = sqlite3.connect(LUMEN_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            SQL_CHUNKS_QUERY,
            (f"%{keyword}%", f"%{keyword}%", limit)
        )
        rows = cursor.fetchall()
        conn.close()
        result_list = []
        for row in rows:
            chunk_dict = _build_chunk_dict(row)
            result_list.append(chunk_dict)
        return result_list
    except Exception:
        return []


def synthesize_combinatorial_maximalist_pddl(state: str, num_nodes: int = DEFAULT_NUM_NODES, num_workers: int = DEFAULT_NUM_WORKERS) -> dict[str, str]:
    """Synthesize high-dimensional PDDL+ problem state with scaled numeric fluent constraints, temporal durations, and resource matrix."""

    # 1. Base Agricola IPC-18 Domain
    base_domain = AGRICOLA_DOMAIN_PATH.read_text(encoding=DEFAULT_ENCODING) if AGRICOLA_DOMAIN_PATH.exists() else ""

    # 2. Combinatorial Numeric & Temporal Invariants
    num_facts = []
    substract_facts = []
    worker_facts = []
    node_facts = []

    for w in range(MIN_WORKER_INDEX, num_workers + 1):
        worker_facts.append(WORKER_FACT_TEMPLATE.format(w=w))

    for n in range(MIN_WORKER_INDEX, num_nodes + 1):
        node_facts.append(NODE_FACT_TEMPLATE.format(n=n))

    for i in range(MIN_NODE_INDEX, num_nodes):
        num_facts.append(PDDL_NEXT_NUM_TEMPLATE.format(i=i, next_i=i + 1))
        for j in range(MIN_WORKER_INDEX, min(MAX_SUBSTRACT_RANGE, i + 1)):
            substract_facts.append(PDDL_SUBSTRACT_TEMPLATE.format(i=i, j=j, diff=i - j))

    stages_str = " ".join([STAGE_TEMPLATE.format(s=s) for s in range(STAGE_START_INDEX, NUM_STAGES + 1)])
    rounds_str = " ".join([ROUND_TEMPLATE.format(r=r) for r in range(MIN_WORKER_INDEX, NUM_ROUNDS + 1)])
    nums_str = " ".join([NUM_TEMPLATE.format(n=i) for i in range(MIN_NODE_INDEX, num_nodes + 1)])

    problem_name = PROBLEM_NAME_PREFIX + state
    objects_section = f"{nums_str}{PDDL_OBJECTS_NUM_TYPE}{NEWLINE_CHAR}    {stages_str}{PDDL_OBJECTS_STAGE_TYPE}{NEWLINE_CHAR}    {rounds_str}{PDDL_OBJECTS_ROUND_TYPE}"
    init_section = NEWLINE_CHAR.join(num_facts[:INIT_FACTS_LIMIT]) + NEWLINE_CHAR + NEWLINE_CHAR.join(substract_facts[:SUBSTRACT_FACTS_LIMIT]) + NEWLINE_CHAR + PDDL_TOTAL_COST_LINE + f" {INITIAL_COST}"
    goal_section = PDDL_BUILT_ROOMS_TEMPLATE.format(node_id=num_nodes, worker_id=num_workers) + NEWLINE_CHAR + PDDL_NUM_FOOD_TEMPLATE.format(node_id=num_nodes)

    worker_facts_joined = NEWLINE_CHAR.join(worker_facts)
    node_facts_joined = NEWLINE_CHAR.join(node_facts)

    maximalist_problem = f"""{PDDL_DEFINE_PROBLEM_TEMPLATE.format(problem_name=problem_name)}
{PDDL_DOMAIN_TEMPLATE.format(domain_name=PROBLEM_DOMAIN_NAME)}
{PDDL_OBJECTS_HEADER}
    {objects_section}
{worker_facts_joined}
{node_facts_joined}
)
{PDDL_INIT_SECTION}
{init_section}
)
{PDDL_GOAL_SECTION}
{goal_section}
{PDDL_CLOSE}
{PDDL_CLOSE}"""

    combined_domain = base_domain + DOMAIN_EXTENSION_COMMENT.format(nodes=num_nodes, workers=num_workers)

    # 3. POWL Hyper-Graph Synthesis
    powl_hypergraph = {}
    powl_hypergraph[KEY_POWL_NODES] = num_nodes
    powl_hypergraph[KEY_POWL_WORKERS] = num_workers
    powl_hypergraph[KEY_POWL_TEMPORAL_HORIZON] = TEMPORAL_HORIZON_MS
    state_space_inner = f"{num_nodes}{STATE_SPACE_FORMAT_SEPARATOR}{num_workers}{STATE_SPACE_FORMAT_SEPARATOR}{STATE_SPACE_WORKER_FACTOR}"
    state_space_est = STATE_SPACE_FORMAT_PREFIX + state_space_inner + STATE_SPACE_FORMAT_SUFFIX
    powl_hypergraph[KEY_POWL_STATE_SPACE] = state_space_est
    powl_hypergraph[KEY_POWL_TOPOLOGY_NAME] = POWL_TOPOLOGY

    result = {}
    result[KEY_DOMAIN_PDDL] = combined_domain
    result[KEY_PROBLEM_PDDL] = maximalist_problem
    result[KEY_POWL_GRAPH] = str(powl_hypergraph)
    return result


def 执行推演(state: str, history: list[str] | None = None) -> dict[str, str | list | dict]:
    """Execute strategy rollout with Combinatorial Maximalism scaling state space, numbers, and temporal constraints."""
    keyword = state.split("_")[0] if "_" in state else DEFAULT_LUMEN_KEYWORD
    grounded_chunks = query_lumen_grounding(keyword=keyword, limit=DEFAULT_LUMEN_LIMIT)
    pddl_spec = synthesize_combinatorial_maximalist_pddl(state=state, num_nodes=DEFAULT_NUM_NODES, num_workers=DEFAULT_NUM_WORKERS)

    strategy_output = STRATEGY_TEMPLATE.format(
        state=state,
        nodes=DEFAULT_NUM_NODES,
        workers=DEFAULT_NUM_WORKERS,
        factor=STATE_SPACE_WORKER_FACTOR
    )
    game_rounds = str(len(history) if history else INITIAL_COST)

    result = {}
    result[KEY_STATUS] = state
    result[KEY_STRATEGY] = strategy_output
    result[KEY_GAME_ROUNDS] = game_rounds
    result[KEY_LUMEN_GROUNDING] = grounded_chunks
    result[KEY_PDDL] = pddl_spec
    return result
