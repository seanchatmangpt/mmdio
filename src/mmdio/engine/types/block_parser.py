"""Lark transformer and parser for Block diagrams (type-scoped)."""

from lark import Transformer, Token
from . import block_models


def _unquote(s: str) -> str:
    """Remove surrounding quotes from a string."""
    if isinstance(s, Token):
        s = str(s)
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


class BlockTransformer(Transformer):
    """Transform block diagram parse tree to BlockDiagram."""

    def block_id(self, items: list) -> str:
        """Return block identifier."""
        return str(items[0])

    def block_label(self, items: list) -> str:
        """Return unquoted block label."""
        return _unquote(items[0])

    def block_stmt(self, items: list) -> block_models.Block:
        """Build a block."""
        block_id = str(items[0])
        block_label = str(items[1])
        return block_models.Block(id=block_id, label=block_label)

    def connection_stmt(self, items: list) -> block_models.Connection:
        """Build a connection."""
        source = str(items[0])
        arrow_type = str(items[1])
        target = str(items[2])
        label = str(items[3]) if len(items) > 3 else None
        return block_models.Connection(
            source=source,
            target=target,
            arrow_type=arrow_type,
            label=label
        )

    def column_stmt(self, items: list) -> int:
        """Return column count."""
        return int(items[0])

    def space_stmt(self, items: list) -> str:
        """Return space marker."""
        return "space"

    def statement(self, items: list) -> object:
        """Return statement item (pass through)."""
        return items[0] if items else None

    def diagram(self, items: list) -> block_models.BlockDiagram:
        """Build block diagram."""
        columns = None
        blocks = []
        connections = []

        for item in items:
            if isinstance(item, int):
                columns = item
            elif isinstance(item, block_models.Block):
                blocks.append(item)
            elif isinstance(item, block_models.Connection):
                connections.append(item)
            elif item == "space":
                # Ignore space statements
                pass

        return block_models.BlockDiagram(
            columns=columns,
            blocks=blocks,
            connections=connections
        )

    def start(self, items: list) -> block_models.BlockDiagram:
        """Return the diagram."""
        return items[0]


def parse_block(source: str) -> block_models.BlockDiagram:
    """
    Parse Block diagram source text.

    Args:
        source: Mermaid block-beta diagram text

    Returns:
        BlockDiagram AST

    Raises:
        Exception: If parse fails
    """
    from lark import Lark
    import os

    grammar_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "grammars",
        "block.lark"
    )

    with open(grammar_path) as f:
        grammar = f.read()

    parser = Lark(grammar, parser="lalr", start="start")
    tree = parser.parse(source)
    transformer = BlockTransformer()
    return transformer.transform(tree)
