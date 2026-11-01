"""Record schemas (issue #25): the examples validate and every rule rejects what it should."""

from pathlib import Path

import pytest

from beaver.records import (
    Brief, Capability, Evidence, Inquiry, Registry, load_record, load_registry, schemas, split_frontmatter,
)

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = REPO / "core" / "ontology" / "examples"
SCHEMAS = REPO / "core" / "ontology" / "schemas"

ARTIFACT = [{"repo": "me/crm-sync", "ref": "4f2c1a9"}]


def evidence(**overrides):
    base = {"id": "evidence.x", "claim": "I can retry safely.", "supports": ["capability.api-integration"],
            "artifacts": ARTIFACT, "level": 2, "assistance": "pair"}
    return {**base, **overrides}


def brief(**overrides):
    base = {"id": "brief.x", "title": "t", "user": "ops lead", "outcome": "no duplicates",
            "practises": ["capability.api-integration"], "non_goals": ["deletes"], "done_when": "a test passes"}
    return {**base, **overrides}


@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*.md")), ids=lambda p: p.name)
def test_every_example_record_validates(path):
    assert load_record(path).id


def test_the_example_registry_validates():
    registry = load_registry(EXAMPLES / "registry.yaml")
    assert registry.limits.active_projects == 2 and registry.projects[0].id == "project.crm-sync"


def test_exported_schemas_match_the_models():
    committed = {p.name: p.read_text(encoding="utf-8") for p in SCHEMAS.glob("*.schema.json")}
    assert committed == schemas(), "run: python -m beaver.records export core/ontology/schemas"


@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*.md")), ids=lambda p: p.name)
def test_examples_also_validate_against_the_exported_json_schema(path):
    # For tools outside Python. Cross-field rules (levels, delegation) live only in the models.
    import json

    import jsonschema

    data, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    data = json.loads(json.dumps(data, default=str))  # YAML dates become ISO strings, as JSON has them
    kind = data["id"].split(".", 1)[0]
    jsonschema.validate(data, json.loads((SCHEMAS / f"{kind}.schema.json").read_text(encoding="utf-8")))


def test_delegated_work_stays_at_level_1():
    with pytest.raises(ValueError, match="delegated work stays at level 1"):
        Evidence.model_validate(evidence(assistance="delegate", level=2))
    Evidence.model_validate(evidence(assistance="delegate", level=1))


def test_a_level_needs_an_artifact():
    with pytest.raises(ValueError, match="needs at least one artifact"):
        Evidence.model_validate(evidence(level=1, artifacts=[]))
    Evidence.model_validate(evidence(level=0, artifacts=[]))  # a claim waits for an artifact


def test_level_3_needs_a_variation_or_another_person():
    with pytest.raises(ValueError, match="needs a variation task or another person"):
        Evidence.model_validate(evidence(level=3))
    Evidence.model_validate(evidence(level=3, reviewed_in="review.2026-11-20-variation"))


def test_evidence_points_at_a_capability():
    with pytest.raises(ValueError, match="supports or challenges"):
        Evidence.model_validate(evidence(supports=[]))


def test_a_brief_needs_non_goals_and_a_done_when():
    with pytest.raises(ValueError, match="non_goals"):
        Brief.model_validate(brief(non_goals=[]))
    with pytest.raises(ValueError, match="done_when"):
        Brief.model_validate({k: v for k, v in brief().items() if k != "done_when"})


def test_a_closed_question_says_how_it_closed():
    base = {"id": "inquiry.x", "question": "How long should a key live?", "opened": "2026-11-06"}
    with pytest.raises(ValueError, match="answered_by"):
        Inquiry.model_validate({**base, "status": "answered"})
    with pytest.raises(ValueError, match="evolved_into"):
        Inquiry.model_validate({**base, "status": "evolved"})


def test_ids_carry_their_own_type():
    with pytest.raises(ValueError, match="pattern"):
        Capability.model_validate({"id": "concept.api-integration", "title": "t"})
    with pytest.raises(ValueError, match="pattern"):
        Capability.model_validate({"id": "capability.API_Integration", "title": "t"})


def test_a_typo_in_a_key_is_caught():
    with pytest.raises(ValueError, match="requries"):
        Capability.model_validate({"id": "capability.x", "title": "t", "requries": ["concept.y"]})


def test_registry_ids_are_unique_and_limits_are_not_schema_errors():
    project = {"id": "project.a", "source": {"type": "local", "path": "~/a"}, "relationship": "existing"}
    with pytest.raises(ValueError, match="appears once"):
        Registry.model_validate({"projects": [project, project]})
    three_active = [{**project, "id": f"project.p{i}"} for i in range(3)]
    assert len(Registry.model_validate({"projects": three_active}).projects) == 3  # status flags it, not the schema


def test_loading_rejects_unknown_types_and_missing_frontmatter(tmp_path):
    odd = tmp_path / "odd.md"
    odd.write_text("---\nid: widget.x\n---\n")
    with pytest.raises(ValueError, match="unknown record type"):
        load_record(odd)
    with pytest.raises(ValueError, match="frontmatter"):
        split_frontmatter("no frontmatter here")
