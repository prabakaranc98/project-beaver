"""The validator (issue #27) against the expectations in tests/golden/.

Rendered output is snapshotted in tests/golden/<name>.validate.txt.
Regenerate after an intended change with: UPDATE_GOLDEN=1 pytest tests/test_validate.py
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from beaver.cli import app
from beaver.validate import validate_workspace

REPO = Path(__file__).resolve().parent.parent
GOLDEN = REPO / "tests" / "golden"
SPECS = sorted(GOLDEN.glob("*.yaml"))


def spec(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_problems_match_the_expectations(path):
    expected = spec(path)
    report = validate_workspace(REPO / expected["workspace"])
    found = {(p.file, p.kind, p.ref) for p in report.problems}
    wanted = {(e["file"], e["kind"], e.get("ref") or e.get("field")) for e in expected.get("validate", [])}
    assert found == wanted


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_rendered_output_matches_the_snapshot(path):
    rendered = validate_workspace(REPO / spec(path)["workspace"]).render() + "\n"
    snapshot = GOLDEN / f"{path.stem}.validate.txt"
    if os.environ.get("UPDATE_GOLDEN"):
        snapshot.write_text(rendered, encoding="utf-8")
    assert snapshot.read_text(encoding="utf-8") == rendered


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_duplicates_unknown_types_and_missing_frontmatter_are_caught(tmp_path):
    concept = "---\nid: concept.a\ntitle: A\n---\n"
    write(tmp_path, "learning/concepts/a.md", concept)
    write(tmp_path, "learning/concepts/a-copy.md", concept)
    write(tmp_path, "learning/concepts/widget.md", "---\nid: widget.x\n---\n")
    write(tmp_path, "learning/concepts/plain.md", "no frontmatter\n")
    kinds = {(p.file, p.kind) for p in validate_workspace(tmp_path).problems}
    assert ("learning/concepts/a.md", "duplicate-id") in kinds or ("learning/concepts/a-copy.md", "duplicate-id") in kinds
    assert ("learning/concepts/widget.md", "schema") in kinds
    assert ("learning/concepts/plain.md", "schema") in kinds


def test_an_invalid_record_still_counts_as_existing(tmp_path):
    # evidence.x fails its schema, but the capability pointing at it should not also report a missing ID
    write(tmp_path, "evidence/x.md", "---\nid: evidence.x\nsupports: [capability.a]\nlevel: 0\nassistance: pair\n---\n")
    write(tmp_path, "learner/capabilities/a.md", "---\nid: capability.a\ntitle: A\nevidence: [evidence.x]\n---\n")
    kinds = {(p.file, p.kind) for p in validate_workspace(tmp_path).problems}
    assert kinds == {("evidence/x.md", "schema")}


def test_the_beaver_command_passes_on_the_example_and_fails_on_broken_links():
    runner = CliRunner()
    ok = runner.invoke(app, ["validate", str(REPO / "core" / "examples")])
    assert ok.exit_code == 0 and "check out" in ok.output
    bad = runner.invoke(app, ["validate", str(REPO / "tests" / "fixtures" / "broken-links")])
    assert bad.exit_code == 1 and "concept.does-not-exist" in bad.output
    assert runner.invoke(app, ["--version"]).output.startswith("beaver ")
    assert "record, ID and wikilink" in runner.invoke(app, ["--help"]).output  # rich markup once ate [[...]]


def test_tools_validate_runs_as_a_script():
    script = REPO / "tools" / "validate.py"
    ok = subprocess.run([sys.executable, str(script), str(REPO / "core" / "examples")], capture_output=True, text=True)
    bad = subprocess.run([sys.executable, str(script), str(REPO / "tests" / "fixtures" / "broken-links")],
                         capture_output=True, text=True)
    assert ok.returncode == 0 and bad.returncode == 1
