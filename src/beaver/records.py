"""Beaver's records: one object per Markdown file, YAML frontmatter, `type.slug` IDs.

These models are the single definition of each record type (docs/design.md,
"Learning ontology and knowledge format"). The validator (#27), the progress
check (#30), the CLI, the UI and the agent all read records through them, and
`core/ontology/schemas/` holds their JSON Schema export for any other tool.

    python -m beaver.records export core/ontology/schemas
"""

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

SLUG = r"[a-z0-9][a-z0-9-]*"


def ref(*types):
    """A `type.slug` reference to a record of one of `types`."""
    return Annotated[str, Field(pattern=rf"^({'|'.join(types)})\.{SLUG}$")]


CapabilityRef = ref("capability")
ConceptRef = ref("concept")
EvidenceRef = ref("evidence")
BriefRef = ref("brief")

LEVELS = {0: "Claimed", 1: "Produced", 2: "Explained", 3: "Varied", 4: "Maintained", 5: "Delivered"}
Assistance = Literal["socratic", "hint", "example", "pair", "delegate"]


class Record(BaseModel):
    # Unknown keys are errors, so a typo such as `requries` is caught, not ignored.
    model_config = ConfigDict(extra="forbid")


class Capability(Record):
    """Something the learner wants to be able to do. Lives in learner/capabilities/."""

    id: ref("capability")
    title: str
    domain: ref("domain") | None = None
    requires: list[ConceptRef] = []
    evidence: list[EvidenceRef] = []
    status: Literal["exploring", "practising", "demonstrated"] = "exploring"


class Concept(Record):
    """Knowledge that supports a capability, in the learner's words. Lives in learning/concepts/."""

    id: ConceptRef
    title: str
    prerequisites: list[ConceptRef] = []
    related: list[ConceptRef] = []
    resources: list[str] = []


class Inquiry(Record):
    """A question the learner is pursuing. Lives in learning/inquiries/."""

    id: ref("inquiry")
    question: str = Field(min_length=1)
    opened: date
    status: Literal["open", "answered", "evolved", "dropped"] = "open"
    about: list[ConceptRef] = []
    answered_by: list[ref("note", "evidence")] = []
    evolved_into: ref("inquiry") | None = None

    @model_validator(mode="after")
    def closed_questions_say_how(self):
        if self.status == "answered" and not self.answered_by:
            raise ValueError("an answered inquiry names what answered it (answered_by)")
        if self.status == "evolved" and not self.evolved_into:
            raise ValueError("an evolved inquiry names the question it became (evolved_into)")
        return self


class Artifact(Record):
    """Code, a diagram or a write-up, referenced in its project repo, never copied."""

    repo: str
    ref: str
    path: str | None = None


class Evidence(Record):
    """An artifact interpreted against a claim. Lives in evidence/."""

    id: EvidenceRef
    claim: str = Field(min_length=1)
    supports: list[CapabilityRef] = []
    challenges: list[CapabilityRef] = []
    artifacts: list[Artifact] = []
    level: int = Field(ge=0, le=5, description="0 Claimed, 1 Produced, 2 Explained, 3 Varied, 4 Maintained, 5 Delivered")
    assistance: Assistance
    reviewed_in: ref("review") | None = None

    @model_validator(mode="after")
    def levels_are_earned(self):
        if not (self.supports or self.challenges):
            raise ValueError("evidence supports or challenges at least one capability")
        if self.level >= 1 and not self.artifacts:
            raise ValueError(f"level {self.level} ({LEVELS[self.level]}) needs at least one artifact")
        if self.assistance == "delegate" and self.level > 1:
            raise ValueError("delegated work stays at level 1 until the learner explains it")
        if self.level >= 3 and not self.reviewed_in:
            raise ValueError(f"level {self.level} ({LEVELS[self.level]}) needs a variation task or another person (reviewed_in)")
        return self


class Brief(Record):
    """A bounded challenge: who it is for, the outcome, what it is not, and when it is done."""

    id: BriefRef
    title: str
    user: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    practises: list[CapabilityRef] = Field(min_length=1)
    constraints: list[str] = []
    non_goals: list[str] = Field(min_length=1)
    done_when: str = Field(min_length=1)


class Sprint(Record):
    """A fixed budget of deep-work hours on one brief. Lives in sprints/."""

    id: ref("sprint")
    brief: BriefRef
    budget_hours: float = Field(gt=0, le=80)
    goal: str = Field(min_length=1)
    practises: list[CapabilityRef] = []
    status: Literal["planned", "active", "closed"] = "planned"


class Reflection(Record):
    """What changed in understanding and what remains open. Written by the learner. Lives in reflections/."""

    id: ref("reflection")
    date: date
    links: list[ref("brief", "sprint", "project", "capability", "concept", "inquiry", "evidence")] = []
    next_action: str = Field(min_length=1)


class Now(Record):
    """learner/now.md: the single session entry point; assistants follow only what it links."""

    id: ref("now")
    mode: Assistance = "hint"
    focus: BriefRef | None = None
    capabilities: list[CapabilityRef] = Field(default=[], max_length=3)
    questions: list[ref("inquiry")] = []
    next_step: str = Field(min_length=1)


class Source(Record):
    type: Literal["github", "local"]
    repository: str | None = None
    path: str | None = None

    @model_validator(mode="after")
    def points_somewhere(self):
        if self.type == "github" and not self.repository:
            raise ValueError("a github source names its repository (owner/name)")
        if self.type == "local" and not self.path:
            raise ValueError("a local source names its path")
        return self


class Review(Record):
    trigger: Literal["manual", "scheduled"] = "manual"
    last_reviewed_commit: str | None = None


class Privacy(Record):
    classification: Literal["public", "private", "client-confidential"] = "private"
    external_model_use: Literal["allowed", "approval-required", "forbidden"] = "allowed"


class Project(Record):
    """A concrete body of work in its own repo, connected by a registry entry, read-only."""

    id: ref("project")
    source: Source
    relationship: Literal["beaver-started", "existing"]
    access: Literal["read-only"] = "read-only"
    state: Literal["active", "paused", "closed"] = "active"
    practises: list[CapabilityRef] = []
    brief: BriefRef | None = None
    review: Review = Review()
    privacy: Privacy = Privacy()


class Limits(Record):
    """Work-in-progress limits the learner can change (docs/design.md, "Registry limits")."""

    active_projects: int = Field(default=2, ge=1)
    ideas_under_evaluation: int = Field(default=5, ge=1)
    active_sprints: int = Field(default=1, ge=1)
    days_since_review: int = Field(default=30, ge=1)


class Registry(Record):
    """projects/registry.yaml: the limits plus every connected project.

    Going over a limit is not a schema error; the progress check flags it.
    """

    limits: Limits = Limits()
    projects: list[Project] = []

    @model_validator(mode="after")
    def ids_are_unique(self):
        ids = [p.id for p in self.projects]
        if len(ids) != len(set(ids)):
            raise ValueError("each project id appears once in the registry")
        return self


RECORD_TYPES = {
    "capability": Capability,
    "concept": Concept,
    "inquiry": Inquiry,
    "evidence": Evidence,
    "brief": Brief,
    "sprint": Sprint,
    "reflection": Reflection,
    "now": Now,
}

# Where records live in a workspace (docs/design.md, "Repository structure").
RECORD_LOCATIONS = ["learner/now.md", "learner/capabilities", "learning/concepts", "learning/inquiries",
                    "projects/briefs", "sprints", "evidence", "reflections"]

# The learner's own folders: where their pages and [[wikilinks]] live. Method, docs and
# tests in the same repo are not part of the workspace.
WORKSPACE_FOLDERS = ["learner", "learning", "projects", "sprints", "evidence", "reflections"]


def split_frontmatter(text):
    """(frontmatter dict, body) from a Markdown file that starts with a `---` YAML block."""
    match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    if not match:
        raise ValueError("a record starts with a --- YAML frontmatter block")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def load_record(path):
    """Read and validate one record file; its type comes from the prefix of its id."""
    data, _body = split_frontmatter(Path(path).read_text(encoding="utf-8"))
    kind = str(data.get("id", "")).split(".", 1)[0]
    if kind not in RECORD_TYPES:
        raise ValueError(f"unknown record type {kind!r}; expected one of {', '.join(RECORD_TYPES)}")
    return RECORD_TYPES[kind].model_validate(data)


def load_registry(path):
    return Registry.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {})


def schemas():
    """JSON Schema for every record type and the registry, keyed by file name."""
    models = {**RECORD_TYPES, "registry": Registry}
    return {f"{name}.schema.json": json.dumps(model.model_json_schema(), indent=2) + "\n" for name, model in models.items()}


def export_schemas(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in schemas().items():
        (folder / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:2] != ["export"] or len(sys.argv) != 3:
        sys.exit("usage: python -m beaver.records export <folder>")
    export_schemas(sys.argv[2])
