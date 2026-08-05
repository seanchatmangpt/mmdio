"""Test the executable mmdio CLI surface."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mmdio.cli import app

runner = CliRunner()


def test_types_lists_all_39() -> None:
    result = runner.invoke(app, ["types"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["count"] == 39


def test_parse_and_validate_stdin() -> None:
    source = "cynefin-beta\n  clear\n    \"Known fix\"\n"
    parsed = runner.invoke(app, ["parse", "-"], input=source)
    assert parsed.exit_code == 0
    assert json.loads(parsed.stdout)["type"] == "cynefin"

    validated = runner.invoke(app, ["validate", "-"], input=source)
    assert validated.exit_code == 0
    assert json.loads(validated.stdout)["standing"] == "ALIVE"


def test_unknown_input_is_typed_refusal() -> None:
    result = runner.invoke(app, ["parse", "-"], input="not mermaid\n")
    assert result.exit_code == 2
    assert json.loads(result.stderr)["code"] == "MMDIO-TYPE-002"


def test_diff_and_merge_commands(tmp_path: Path) -> None:
    base = tmp_path / "base.mmd"
    left = tmp_path / "left.mmd"
    right = tmp_path / "right.mmd"
    base.write_text("timeline\n  2026 : base\n", encoding="utf-8")
    left.write_text("timeline\n  2026 : left\n", encoding="utf-8")
    right.write_text(base.read_text(encoding="utf-8"), encoding="utf-8")

    difference = runner.invoke(app, ["diff", str(base), str(left)])
    assert difference.exit_code == 0
    assert json.loads(difference.stdout)["changed"] is True

    merged = runner.invoke(app, ["merge", str(base), str(left), str(right)])
    assert merged.exit_code == 0
    assert json.loads(merged.stdout)["selected"] == "left"
