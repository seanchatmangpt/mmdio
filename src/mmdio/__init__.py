"""
mmdio: Mermaid Diagrams as Universal IO.

Core module: provides detect_diagram_type() without heavy dependencies.
Full engine (parse, render, ops, models) available via mmdio.engine or mmdio[all] extra.
"""

from __future__ import annotations

from mmdio.detect import detect_diagram_type

__all__ = [
    "detect_diagram_type",
]
