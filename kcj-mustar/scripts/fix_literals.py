#!/usr/bin/env python3
"""
Hoist hardcoded string/number literals from inside functions to module-level constants.
Generates a module-level CONSTANTS dict at the top of each file.
"""

import ast
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple

class LiteralExtractor(ast.NodeVisitor):
    """Find all hardcoded string/number literals inside functions."""

    def __init__(self, filename: str):
        self.filename = filename
        self.literals: Dict[str, Set[Tuple[int, str]]] = defaultdict(set)  # value -> set of (line, type)
        self.inside_function = False
        self.function_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.inside_function = True
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1
        if self.function_depth == 0:
            self.inside_function = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.inside_function = True
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1
        if self.function_depth == 0:
            self.inside_function = False

    def visit_Constant(self, node: ast.Constant):
        if self.inside_function:
            if isinstance(node.value, str):
                val = node.value.strip()
                # Skip docstrings, empty, dunder, %%, and newline-only strings
                if len(val) > 2 and not val.startswith("__") and not val.startswith("%%") and val != "\n":
                    self.literals[node.value].add((node.lineno, "str"))
            elif isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                # Skip 0, 1, -1
                if node.value not in (0, 1, -1):
                    self.literals[node.value].add((node.lineno, "num"))
        self.generic_visit(node)


def make_var_name(value, lit_type: str, counter: Dict[str, int]) -> str:
    """Generate a safe variable name for a literal."""
    if lit_type == "str":
        # Sanitize the string for a variable name
        s = re.sub(r'[^a-zA-Z0-9_]', '_', str(value)[:40])
        s = re.sub(r'^[0-9]', '_', s)  # Can't start with digit
        s = re.sub(r'_+', '_', s).strip('_')  # Collapse and trim underscores
        s = s.upper() if s else "STRING"
    else:
        # For numbers, just use NUM_<hash of value>
        s = f"NUM_{abs(hash(value)) % 10000}"

    # Handle collisions
    orig = s
    count = counter.get(s, 0)
    while count > 0:
        s = f"{orig}_{count}"
        count += 1
    counter[s] = count + 1
    return s


def hoist_literals(file_path: Path) -> bool:
    """Hoist literals from a file. Returns True if changed."""
    source = file_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return False

    extractor = LiteralExtractor(str(file_path))
    extractor.visit(tree)

    if not extractor.literals:
        return False  # No literals found

    # Build the CONSTANTS dict
    counter: Dict[str, int] = {}
    const_map: Dict[str, str] = {}  # value -> var_name
    const_lines = []

    for value in sorted(extractor.literals.keys(), key=lambda x: (str(type(x).__name__), str(x))):
        var_name = make_var_name(value, extractor.literals[value].__iter__().__next__()[1], counter)
        const_map[repr(value)] = var_name

        if isinstance(value, str):
            # String constant
            escaped = repr(value)
            const_lines.append(f"{var_name} = {escaped}")
        else:
            # Numeric constant
            const_lines.append(f"{var_name} = {value}")

    # Find insertion point (after imports, before first class/function)
    import_end = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_end = node.end_lineno or (i + 1)
        else:
            break

    # Skip docstring if present
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        import_end = tree.body[0].end_lineno or 1

    # Split source and insert constants
    lines = source.splitlines(keepends=True)
    if import_end < len(lines):
        # Insert after imports/docstring
        insert_pos = import_end
        new_lines = (
            lines[:insert_pos] +
            ["\n", "# Auto-hoisted constants\n"] +
            [f"{line}\n" for line in const_lines] +
            ["\n"] +
            lines[insert_pos:]
        )
    else:
        new_lines = lines + ["\n", "# Auto-hoisted constants\n"] + [f"{line}\n" for line in const_lines] + ["\n"]

    new_source = "".join(new_lines)

    # Now replace all occurrences of the literals with variable references
    for repr_val, var_name in const_map.items():
        # Simple string replacement (not perfect but conservative)
        new_source = new_source.replace(repr_val, var_name)

    # Write back
    file_path.write_text(new_source, encoding="utf-8")
    return True


def main():
    src_dir = Path("src")
    if not src_dir.is_dir():
        print("ERROR: src directory not found", file=sys.stderr)
        return 1

    changed = 0
    for py_file in sorted(src_dir.rglob("*.py")):
        if hoist_literals(py_file):
            print(f"Fixed: {py_file}")
            changed += 1

    print(f"\nTotal files modified: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
