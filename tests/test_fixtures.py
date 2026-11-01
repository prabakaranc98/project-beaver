"""Fixture workspaces (issue #29) and their expectations in tests/golden/.

Each tests/golden/<name>.yaml says what `validate` (#27) and `status` (#30)
must report for its workspace. These tests check the fixtures themselves:
every record parses except the ones planted to fail, and every expectation
points at real files. Resolving IDs and wikilinks is the validator's job.
"""

from pathlib import Path

import pytest
import yaml

from beaver.records import load_record, load_registry

REPO = Path(__file__).resolve().parent.parent
GOLDEN = sorted((REPO / "tests" / "golden").glob("*.yaml"))
RECORD_LOCATIONS = ["learner/now.md", "learner/capabilities", "learning/concepts", "learning/inquiries",
                    "projects/briefs", "sprints", "evidence", "reflections"]


def expectation(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def record_files(workspace):
    for location in RECORD_LOCATIONS:
        target = workspace / location
        if target.is_file():
            yield target
        elif target.is_dir():
            yield from sorted(target.rglob("*.md"))


def test_the_four_fixtures_have_expectations():
    assert sorted(p.stem for p in GOLDEN) == ["broken-links", "healthy", "over-limit", "stalled"]


@pytest.mark.parametrize("golden", GOLDEN, ids=lambda p: p.stem)
def test_expectations_point_at_real_files(golden):
    spec = expectation(golden)
    workspace = REPO / spec["workspace"]
    assert workspace.is_dir() and spec["as_of"]
    for problem in spec.get("validate", []):
        assert (workspace / problem["file"]).is_file(), problem


@pytest.mark.parametrize("golden", GOLDEN, ids=lambda p: p.stem)
def test_records_parse_except_the_ones_planted_to_fail(golden):
    spec = expectation(golden)
    workspace = REPO / spec["workspace"]
    planted = {p["file"]: p["field"] for p in spec.get("validate", []) if p["kind"] == "schema"}
    files = list(record_files(workspace))
    assert files, "a fixture holds at least one record"
    for path in files:
        rel = str(path.relative_to(workspace))
        if rel in planted:
            with pytest.raises(ValueError, match=planted[rel]):
                load_record(path)
        else:
            load_record(path)


@pytest.mark.parametrize("golden", GOLDEN, ids=lambda p: p.stem)
def test_registries_load(golden):
    registry = REPO / expectation(golden)["workspace"] / "projects" / "registry.yaml"
    if registry.is_file():
        load_registry(registry)  # over-limit loads too: the progress check flags limits, not the schema
