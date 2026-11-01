"""Templates (issue #26): unfilled, they never pass as records; filled in, each validates."""

import re
from pathlib import Path

import pytest

from beaver.records import RECORD_TYPES, split_frontmatter

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = sorted((REPO / "core" / "templates").glob("*.md"))
PLACEHOLDER = re.compile(r"<([^<>]+)>")


def fill(text):
    """Replace each <placeholder> the way a learner would, by what its name asks for."""
    def value(match):
        name = match.group(1)
        if "slug" in name:
            return "sample"
        if name == "date":
            return "2026-11-03"
        if name == "help-level":
            return "pair"
        if name == "owner/repo":
            return "me/sample"
        if name == "commit":
            return "abc1234"
        return "Sample text"
    return PLACEHOLDER.sub(value, text)


def record(text):
    data, _ = split_frontmatter(text)
    return RECORD_TYPES[str(data["id"]).split(".", 1)[0]], data


def test_the_six_templates_exist():
    assert sorted(p.stem for p in TEMPLATES) == ["brief", "concept", "evidence", "inquiry", "now", "reflection"]


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda p: p.name)
def test_a_filled_template_validates(path):
    model, data = record(fill(path.read_text(encoding="utf-8")))
    model.model_validate(data)


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda p: p.name)
def test_an_unfilled_template_never_passes_as_a_record(path):
    model, data = record(path.read_text(encoding="utf-8"))
    with pytest.raises(ValueError):
        model.model_validate(data)
