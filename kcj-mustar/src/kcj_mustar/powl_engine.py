"""POWL (Partially Ordered Workflow Language) Diagram Renderer aligned with ~/POWL models & mfw-planner architecture."""

import html
from typing import Dict, Any, List


# Constants - Cycle Result Keys
STRATEGY_KEY = "strategy"
STATE_KEY = "状态"
STATE_DEFAULT = "cluster_idle"
RECEIPT_KEY = "receipt"
RECEIPT_DEFAULT_LENGTH = 64
QUALITY_KEY = "quality"
OCEL_EVENT_KEY = "OCEL_Event"
OCEL_EID_KEY = "ocel:eid"
OCEL_EID_DEFAULT = "evt-000"
DISPATCH_KEY = "dispatch"
APM_KEY = "APM"
APM_DEFAULT = 100000

# Constants - Mermaid Graph Structure
GRAPH_TD = "graph TD"
POWL_ROOT_MODEL_ID = "POWL_Root_Model"
POWL_ROOT_MODEL_LABEL = "POWL Model: KCJ Autonomic Cycle ({state})"

# Constants - Chinese Strategy Engine (Partial Order)
PO_CHINESE_STRATEGY_ID = "PO_Chinese_Strategy"
PO_CHINESE_STRATEGY_LABEL = "Partial Order: 博弈_selfplay (Chinese Strategy Engine)"
T1_ID = "T1"
T1_LABEL = "Transition: Query Lumen sqlite-vec Vector Index"
T2_ID = "T2"
T2_LABEL = "Transition: Synthesize Agricola PDDL+ Domain (568 Lines)"
PDDL_LINES = 568
T3_ID = "T3"
T3_LABEL = "Transition: Construct POWL Hyper-Graph (100 Nodes, 64 Workers)"
HYPERGRAPH_NODES = 100
HYPERGRAPH_WORKERS = 64

# Constants - Japanese Quality Engine (Choice Gate)
CHOICE_JAPANESE_QUALITY_ID = "Choice_Japanese_Quality"
CHOICE_JAPANESE_QUALITY_LABEL = "Choice Gate & Andon Fences: 現場_quality (Japanese Quality Control)"
Q1_ID = "Q1"
Q1_LABEL = "Choice Gate: Val PDDL Verification & Tree Check"
Q_PASS_ID = "Q_Pass"
Q_PASS_LABEL_PREFIX = "Transition: Emit OCEL 2.0 Event Log ("
Q_FAIL_ID = "Q_Fail"
Q_FAIL_LABEL = "Transition: Trigger Andon Cord Line-Stop (行灯停止)"
Q_PASS_CONDITION = "Pass Invariants"
Q_FAIL_CONDITION = "Detect Defect"

# Constants - Korean Actuation Engine (Partial Order)
PO_KOREAN_ACTUATION_ID = "PO_Korean_Actuation"
PO_KOREAN_ACTUATION_LABEL = "Partial Order: 구動_actuation (Korean Real-Time Dispatch)"
D1_ID = "D1"
D1_LABEL_PREFIX = "Transition: Execute High-Speed Dispatch ("
D1_LABEL_SUFFIX = " APM)"
D2_ID = "D2"
D2_LABEL_PREFIX = "Transition: Append Cryptographic BLAKE3 Receipt ("
D2_LABEL_SUFFIX = "...)"
RECEIPT_DISPLAY_LENGTH = 16

# Constants - Entropy
ENTROPY_SEED_COMMENT = "% Entropy Seed: "

# Constants - String Literals
NEWLINE = "\n"
SUBGRAPH_KEYWORD = "subgraph "
CLOSING_BRACKET = "\"]"
CHOICE_GATE_KEYWORD = "Choice Gate"
PARTIAL_ORDER_KEYWORD = "Partial Order"
LOOP_START_INDEX = 0
MERMAID_END_INNER = "    end"
MERMAID_END_OUTER = "  end"
Q1_LABEL = "Choice Gate: Val PDDL Verification & Tree Check"
RECEIPT_DEFAULT_CHAR = "0"
EMPTY_STRING = ""

# Constants - SVG Rendering
DEFAULT_SVG_TITLE = "POWL Workflow Diagram"
SVG_WIDTH = 1100
SVG_MIN_HEIGHT = 500
SVG_NODE_HEIGHT_MULTIPLIER = 55
SVG_HEIGHT_BASE = 140
SVG_INITIAL_Y_OFFSET = 80
SVG_CHOICE_GATE_COLOR = "#f9e2af"
SVG_PARTIAL_ORDER_COLOR = "#89b4fa"
SVG_DEFAULT_NODE_COLOR = "#1e1e2e"
SVG_DARK_TEXT_COLOR = "#11111b"
SVG_LIGHT_TEXT_COLOR = "#cdd6f4"
SVG_ACCENT_COLOR = "#a6e3a1"
SVG_FONT_FAMILY_MONO = "monospace"
SVG_FONT_FAMILY_SANS = "sans-serif"
SVG_FONT_SIZE_LARGE = 22
SVG_FONT_SIZE_NODE = 14
SVG_STROKE_WIDTH = 2
SVG_RECT_X_OFFSET = 50
SVG_RECT_WIDTH = 1000
SVG_RECT_HEIGHT = 40
SVG_RECT_CORNER_RADIUS = 8
SVG_TEXT_X_OFFSET = 500
SVG_TEXT_Y_OFFSET = 25
SVG_LINE_X_START = 550
SVG_LINE_Y_OFFSET = 15
SVG_MARKER_REF_X = 5
SVG_MARKER_REF_Y = 5
SVG_MARKER_WIDTH = 6
SVG_MARKER_HEIGHT = 6
SVG_ROOT_FILL = "#11111b"
SVG_ROOT_CORNER_RADIUS = 10
SVG_TITLE_X_OFFSET = 30
SVG_TITLE_Y_OFFSET = 45
SVG_TITLE_COLOR = "#89b4fa"
SVG_ARROW_MARKER_ID = "arrow"
SVG_ARROW_PATH = "M 0 0 L 10 5 L 0 10 z"
SVG_XMLNS = "http://www.w3.org/2000/svg"
SVG_SUBGRAPH_OPEN = "["
SVG_SUBGRAPH_CLOSE = "]"
SVG_CHOICE_OPEN = "{"
SVG_CHOICE_CLOSE = "}"
SVG_TEXT_ANCHOR_MIDDLE = "middle"
SVG_FONT_WEIGHT_BOLD = "bold"
SVG_MARKER_ORIENT = "auto-start-reverse"


def generate_powl_mermaid_from_run(cycle_result: Dict[str, Any], entropy_seed: str = "") -> str:
    """Transform real Chicago TDD cycle output into a valid POWL (Partially Ordered Workflow Language) Mermaid diagram."""
    
    state = cycle_result.get(STRATEGY_KEY, {}).get(STATE_KEY, STATE_DEFAULT)
    receipt = str(cycle_result.get(RECEIPT_KEY, RECEIPT_DEFAULT_CHAR * RECEIPT_DEFAULT_LENGTH))
    ocel_eid = cycle_result.get(QUALITY_KEY, {}).get(OCEL_EVENT_KEY, {}).get(OCEL_EID_KEY, OCEL_EID_DEFAULT)
    dispatch_apm = cycle_result.get(DISPATCH_KEY, {}).get(APM_KEY, APM_DEFAULT)

    lines = [GRAPH_TD]
    lines.append(f"  subgraph {POWL_ROOT_MODEL_ID}[\"{POWL_ROOT_MODEL_LABEL.format(state=state)}\"]")
    
    # 1. Partial Order Node: Chinese Strategy Engine (博弈_selfplay)
    lines.append(f"    subgraph {PO_CHINESE_STRATEGY_ID}[\"{PO_CHINESE_STRATEGY_LABEL}\"]")
    lines.append(f"      {T1_ID}[\"{T1_LABEL}\"]")
    lines.append(f"      {T2_ID}[\"{T2_LABEL}\"]")
    lines.append(f"      {T3_ID}[\"{T3_LABEL}\"]")
    lines.append(f"      {T1_ID} --> {T2_ID} --> {T3_ID}")
    lines.append(MERMAID_END_INNER)

    # 2. Choice Gate & Partial Order Node: Japanese Quality Engine (現場_quality)
    lines.append(f"    subgraph {CHOICE_JAPANESE_QUALITY_ID}[\"{CHOICE_JAPANESE_QUALITY_LABEL}\"]")
    lines.append(f"      {Q1_ID}{{\"{Q1_LABEL}\"}}")
    lines.append(f"      {Q_PASS_ID}[\"{Q_PASS_LABEL_PREFIX}{ocel_eid})\"]")
    lines.append(f"      {Q_FAIL_ID}[\"{Q_FAIL_LABEL}\"]")
    lines.append(f"      {Q1_ID} -->|\"{Q_PASS_CONDITION}\"| {Q_PASS_ID}")
    lines.append(f"      {Q1_ID} -->|\"{Q_FAIL_CONDITION}\"| {Q_FAIL_ID}")
    lines.append(MERMAID_END_INNER)

    # 3. Partial Order Node: Korean Actuation Engine (구동_actuation)
    lines.append(f"    subgraph {PO_KOREAN_ACTUATION_ID}[\"{PO_KOREAN_ACTUATION_LABEL}\"]")
    lines.append(f"      {D1_ID}[\"{D1_LABEL_PREFIX}{dispatch_apm:,}{D1_LABEL_SUFFIX}\"]")
    lines.append(f"      {D2_ID}[\"{D2_LABEL_PREFIX}{receipt[:RECEIPT_DISPLAY_LENGTH]}{D2_LABEL_SUFFIX}\"]")
    lines.append(f"      {D1_ID} --> {D2_ID}")
    lines.append(MERMAID_END_INNER)

    lines.append(MERMAID_END_OUTER)

    # Connect Partial Order & Choice Blocks via POWL Control Edge Dependencies
    lines.append(f"  {PO_CHINESE_STRATEGY_ID} --> {CHOICE_JAPANESE_QUALITY_ID}")
    lines.append(f"  {Q_PASS_ID} --> {PO_KOREAN_ACTUATION_ID}")

    if entropy_seed:
        lines.append(f"  {ENTROPY_SEED_COMMENT}{entropy_seed}")

    return NEWLINE.join(lines)


def render_powl_to_svg(powl_mermaid_code: str, title: str = DEFAULT_SVG_TITLE) -> str:
    """Render POWL Mermaid workflow diagram into dark-mode SVG format."""
    clean_code = powl_mermaid_code.strip()

    # Parse subgraphs and transitions
    nodes = []
    for line in clean_code.splitlines():
        line_str = line.strip()
        if SVG_SUBGRAPH_OPEN + "\"" in line_str and CLOSING_BRACKET in line_str:
            parts = line_str.split(SVG_SUBGRAPH_OPEN + "\"")
            node_id = parts[0].strip().replace(SUBGRAPH_KEYWORD, "")
            label = parts[1].split(CLOSING_BRACKET)[0]
            nodes.append((node_id, label))
        elif SVG_CHOICE_OPEN + "\"" in line_str and SVG_CHOICE_CLOSE + "\"" in line_str:
            parts = line_str.split(SVG_CHOICE_OPEN + "\"")
            node_id = parts[0].strip()
            label = parts[1].split(SVG_CHOICE_CLOSE)[0]
            nodes.append((node_id, label))

    width = SVG_WIDTH
    height = max(SVG_MIN_HEIGHT, len(nodes) * SVG_NODE_HEIGHT_MULTIPLIER + SVG_HEIGHT_BASE)

    svg_nodes = []
    y_offset = SVG_INITIAL_Y_OFFSET
    for idx, (node_id, label) in enumerate(nodes):
        is_choice = CHOICE_GATE_KEYWORD in label
        box_color = SVG_CHOICE_GATE_COLOR if is_choice else (SVG_PARTIAL_ORDER_COLOR if PARTIAL_ORDER_KEYWORD in label else SVG_DEFAULT_NODE_COLOR)
        text_color = SVG_DARK_TEXT_COLOR if is_choice or PARTIAL_ORDER_KEYWORD in label else SVG_LIGHT_TEXT_COLOR

        svg_nodes.append(
            f'<g transform="translate({SVG_RECT_X_OFFSET}, {y_offset})">'
            f'<rect width="{SVG_RECT_WIDTH}" height="{SVG_RECT_HEIGHT}" rx="{SVG_RECT_CORNER_RADIUS}" fill="{box_color}" stroke="{SVG_ACCENT_COLOR}" stroke-width="{SVG_STROKE_WIDTH}"/>'
            f'<text x="{SVG_TEXT_X_OFFSET}" y="{SVG_TEXT_Y_OFFSET}" fill="{text_color}" font-family="{SVG_FONT_FAMILY_MONO}" font-size="{SVG_FONT_SIZE_NODE}" font-weight="{SVG_FONT_WEIGHT_BOLD}" text-anchor="{SVG_TEXT_ANCHOR_MIDDLE}">{html.escape(label)}</text>'
            f'</g>'
        )
        if idx > LOOP_START_INDEX:
            svg_nodes.append(
                f'<line x1="{SVG_LINE_X_START}" y1="{y_offset - SVG_LINE_Y_OFFSET}" x2="{SVG_LINE_X_START}" y2="{y_offset}" stroke="{SVG_ACCENT_COLOR}" stroke-width="{SVG_STROKE_WIDTH}" marker-end="url({SVG_ARROW_MARKER_ID})"/>'
            )
        y_offset += SVG_NODE_HEIGHT_MULTIPLIER

    return f"""<svg xmlns="{SVG_XMLNS}" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <marker id="{SVG_ARROW_MARKER_ID}" viewBox="0 0 10 10" refX="{SVG_MARKER_REF_X}" refY="{SVG_MARKER_REF_Y}" markerWidth="{SVG_MARKER_WIDTH}" markerHeight="{SVG_MARKER_HEIGHT}" orient="{SVG_MARKER_ORIENT}">
      <path d="{SVG_ARROW_PATH}" fill="{SVG_ACCENT_COLOR}"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="{SVG_ROOT_FILL}" rx="{SVG_ROOT_CORNER_RADIUS}"/>
  <text x="{SVG_TITLE_X_OFFSET}" y="{SVG_TITLE_Y_OFFSET}" fill="{SVG_TITLE_COLOR}" font-family="{SVG_FONT_FAMILY_SANS}" font-size="{SVG_FONT_SIZE_LARGE}" font-weight="{SVG_FONT_WEIGHT_BOLD}">{html.escape(title)}</text>
  {EMPTY_STRING.join(svg_nodes)}
</svg>"""
