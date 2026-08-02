"""Oracle test for Timeline diagram type.

Validates timeline rendering against real mermaid-js parser.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from mmdio.engine.types import timeline_models, timeline_render


def get_oracle_node_path() -> str:
    """Get absolute path to verify_mermaid.mjs, relative to this module."""
    this_dir = Path(__file__).parent.parent
    oracle_script = this_dir / "oracle" / "verify_mermaid.mjs"
    return str(oracle_script)


def check_node_available() -> bool:
    """Check if node is available and npm ci has been run in oracle dir."""
    # Check if node is available
    if shutil.which("node") is None:
        return False

    # Check if npm dependencies are installed
    oracle_dir = Path(get_oracle_node_path()).parent
    node_modules = oracle_dir / "node_modules"
    return node_modules.exists() and (node_modules / "mermaid").exists()


# Skip all tests if Node/npm not available
pytestmark = pytest.mark.skipif(
    not check_node_available(),
    reason="Node.js or npm dependencies not available (run: cd tests/oracle && npm ci)"
)


def validate_mermaid_source(mmd_source: str) -> None:
    """
    Validate a mermaid source string against the real mermaid-js parser.

    Args:
        mmd_source: Mermaid diagram source code as a string

    Raises:
        AssertionError: If the mermaid-js parser rejects the diagram
        subprocess.CalledProcessError: If the validation script fails
    """
    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.mmd',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(mmd_source)
        temp_path = f.name

    try:
        # Run the Node.js validator
        result = subprocess.run(
            ['node', get_oracle_node_path(), temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check the result
        if result.returncode != 0:
            raise AssertionError(
                f"Mermaid validation failed:\n{result.stdout}\n{result.stderr}"
            )
    finally:
        # Clean up temp file
        os.unlink(temp_path)


class TestOracleTimeline:
    """Test timeline diagram rendering."""

    def test_timeline_simple(self) -> None:
        """Test simple timeline with events."""
        diagram = timeline_models.TimelineDiagram(
            title="Project Timeline",
            events=[
                timeline_models.TimelineEvent(time="2024-01-01", description="Phase 1 Start"),
                timeline_models.TimelineEvent(time="2024-02-15", description="Milestone A"),
                timeline_models.TimelineEvent(time="2024-03-30", description="Phase 2 Start"),
            ]
        )
        source = timeline_render.render_timeline(diagram)
        validate_mermaid_source(source)

    def test_timeline_no_title(self) -> None:
        """Test timeline without title."""
        diagram = timeline_models.TimelineDiagram(
            events=[
                timeline_models.TimelineEvent(time="January", description="Planning"),
                timeline_models.TimelineEvent(time="February", description="Development"),
                timeline_models.TimelineEvent(time="March", description="Testing"),
            ]
        )
        source = timeline_render.render_timeline(diagram)
        validate_mermaid_source(source)

    def test_timeline_various_date_formats(self) -> None:
        """Test timeline with various date/time formats."""
        diagram = timeline_models.TimelineDiagram(
            title="Q1 2024",
            events=[
                timeline_models.TimelineEvent(time="2024-01", description="January Sprint"),
                timeline_models.TimelineEvent(time="2024-02-14", description="Valentine's Release"),
                timeline_models.TimelineEvent(time="March 2024", description="Spring Planning"),
                timeline_models.TimelineEvent(time="Week 13", description="Mid-quarter Review"),
            ]
        )
        source = timeline_render.render_timeline(diagram)
        validate_mermaid_source(source)
