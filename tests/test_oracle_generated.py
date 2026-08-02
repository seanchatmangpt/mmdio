"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""
import pytest
from mmdio.engine.fixtures import *
from mmdio.engine.render_dispatch import render_diagram

@pytest.mark.parametrize("factory", [example_flowchart,example_sequence,example_class,example_state,example_er,example_gantt,example_pie,example_git,example_c4,example_mindmap,example_sankey])
def test_generated_render_smoke(factory):
    assert render_diagram(factory()).strip()
