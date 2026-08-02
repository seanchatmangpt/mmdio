"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_enums.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonEnum / mer:EnumMember)

Each enum's member VALUE is chosen, where possible, to already equal the
Mermaid render token for that member (see the field-shape vocabulary
comment in ontology.ttl) — so fields typed with these enums render
correctly via plain f-string substitution, no separate token lookup.
Where a real diagram type needs token != label, that enum's ontology
comment says so explicitly rather than leaving it to be discovered.

Uses enum.StrEnum (3.11+), not `class X(str, Enum)`: on Python 3.11+ the
latter's f-string/str() output changed to "ClassName.MEMBER" instead of
the plain value (confirmed by direct test against this project's Python
3.13 runtime — a real bug caught by the enum verification probe, not a
theoretical concern). StrEnum is the only mixin that still formats as the
bare string value, which the render-body template's f-string substitution
depends on.
"""

from enum import StrEnum



