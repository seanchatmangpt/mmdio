"""Render Block diagrams to Mermaid syntax (type-scoped)."""

from . import block_models


def render_block(diagram: block_models.BlockDiagram) -> str:
    """
    Render block diagram to Mermaid syntax.

    Format:
        block-beta
            columns 3
            A["Module A"]
            B["Module B"]
            C["Module C"]
            A --> B
            B --> C

    Args:
        diagram: BlockDiagram AST

    Returns:
        Mermaid block-beta syntax as string
    """
    lines = ["block-beta"]

    # Add columns directive if specified
    if diagram.columns is not None:
        lines.append(f"  columns {diagram.columns}")

    # Add block declarations
    for block in diagram.blocks:
        label = block.label.replace('"', '\\"')
        lines.append(f'  {block.id}["{label}"]')

    # Add connections
    for conn in diagram.connections:
        if conn.label:
            label = conn.label.replace("|", "")
            lines.append(f"  {conn.source} {conn.arrow_type} {conn.target} |{label}|")
        else:
            lines.append(f"  {conn.source} {conn.arrow_type} {conn.target}")

    return "\n".join(lines)
