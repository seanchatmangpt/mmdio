"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_fixtures.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonModel / mer:PythonField)

One example_{id}() builder per top-level diagram model, replacing the
hand-built sample AST each tests/oracle_types/test_oracle_{id}.py used to
construct inline. Two-level nesting limit, same as the render-body
template: a list/nested-ref field's element type gets exactly one example
instance built from that element model's own SCALAR fieldExampleValue
facts only — a list-kind field one level further in (e.g. KanbanSection's
own `cards` list, nested inside KanbanDiagram's `sections` list) is left
at its Pydantic default (empty list) rather than populated, so the
generated example stays valid without needing three-level recursion.
"""

from mmdio.engine._generated_pydantic_models import (

    Block,

    BlockDiagram,

    Connection,

    KanbanCard,

    KanbanDiagram,

    KanbanSection,

    PieChart,

    PieSlice,

    SankeyDiagram,

    SankeyFlow,

    TimelineDiagram,

    TimelineEvent,

)
from mmdio.engine._generated_enums import *  # noqa: F401,F403 — enum literals referenced below









def example_block() -> BlockDiagram:
    """One representative BlockDiagram, built from ontology.ttl example values."""

    return BlockDiagram(





        blocks=[Block(


            id="A",



            label="Module A",


        )],




        connections=[Connection(


            source="A",



            target="B",






        )],


    )








def example_kanban() -> KanbanDiagram:
    """One representative KanbanDiagram, built from ontology.ttl example values."""

    return KanbanDiagram(



        sections=[KanbanSection(


            name="To Do",




        )],


    )






def example_pie() -> PieChart:
    """One representative PieChart, built from ontology.ttl example values."""

    return PieChart(


        title="Sales",




        slices=[PieSlice(


            label="Marketing",



            value=42.5,


        )],


    )






def example_sankey() -> SankeyDiagram:
    """One representative SankeyDiagram, built from ontology.ttl example values."""

    return SankeyDiagram(



        flows=[SankeyFlow(


            source="A",



            target="B",



            value=100,


        )],


    )






def example_timeline() -> TimelineDiagram:
    """One representative TimelineDiagram, built from ontology.ttl example values."""

    return TimelineDiagram(


        title="Project Timeline",




        events=[TimelineEvent(


            time="2024-01-01",



            description="Phase 1 Start",


        )],


    )





