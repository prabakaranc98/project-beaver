"""The repo tree matches the design doc's "Repository structure" (issue #22).

Anything the doc lists but the repo does not have yet must say why, so a gap
is a visible decision rather than drift.
"""

import re
import tomllib
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent

DEFERRED_DIRS = {
    ".obsidian/": "Obsidian creates it on first open",
    ".claude-plugin/": "plugin and marketplace manifests land with #39",
    "companion/": "the companion comes after the MVP",
}
DEFERRED_FILES = {
    "CHARTER.md": "#23",
    "AGENTS.md": "#24",
    "CLAUDE.md": "#24",
    "learner/direction.md": "#31, onboard writes it",
    "learner/now.md": "#31, onboard writes it from core/templates/now.md",
    "learner/curriculum.md": "#31, onboard drafts the first curriculum",
    "learning/inbox.md": "#41, beaver capture appends to it",
    "learning/resources.yaml": "no MVP issue yet",
    "projects/registry.yaml": "#25, the registry schema",
    "generated/status.md": "#30, the progress check writes it",
    "generated/usage.jsonl": "no MVP issue yet: Beaver's own model spend",
    "generated/mentor-notes.md": "no MVP issue yet: mentor patterns",
}


def design_tree():
    """Paths from the ```text tree under "## Repository structure"; folders end in '/'."""
    doc = (REPO / "docs" / "design.md").read_text(encoding="utf-8")
    section = doc.split("## Repository structure", 1)[1]
    tree = re.search(r"```text\n(beaver/\n.*?)```", section, re.S).group(1)
    paths, stack = [], []
    for line in tree.splitlines()[1:]:
        m = re.match(r"^((?:│   |    )*)(?:├── |└── )(\S+)", line)
        if m:
            depth = len(m.group(1)) // 4
            stack = stack[:depth] + [m.group(2).rstrip("/")]
            paths.append("/".join(stack) + ("/" if m.group(2).endswith("/") else ""))
    return paths


def test_the_tree_parses():
    paths = design_tree()
    assert "core/ontology/" in paths and "generated/status.md" in paths
    assert len(paths) > 40


def test_every_folder_in_the_design_doc_exists():
    missing = [p for p in design_tree() if p.endswith("/") and p not in DEFERRED_DIRS and not (REPO / p).is_dir()]
    assert missing == [], f"folders in docs/design.md but not in the repo: {missing}"


def test_every_file_in_the_design_doc_exists_or_names_its_issue():
    missing = [p for p in design_tree()
               if not p.endswith("/") and p not in DEFERRED_FILES and not (REPO / p).is_file()]
    assert missing == [], f"files in docs/design.md with no file and no deferral: {missing}"


def test_deferrals_point_at_paths_the_doc_still_lists():
    paths = set(design_tree())
    stale = [p for p in [*DEFERRED_DIRS, *DEFERRED_FILES] if p not in paths]
    assert stale == [], f"deferred paths no longer in docs/design.md: {stale}"


def test_ownership_points_at_real_paths_and_no_path_has_two_owners():
    config = yaml.safe_load((REPO / "beaver.yaml").read_text(encoding="utf-8"))
    groups = {**config["ownership"], "maintainer_only": config["maintainer_only"]}
    seen = {}
    for owner, entries in groups.items():
        for entry in entries:
            assert entry not in seen, f"{entry} is owned by both {seen[entry]} and {owner}"
            seen[entry] = owner
            exists = (REPO / entry).is_dir() if entry.endswith("/") else (REPO / entry).is_file()
            assert exists or entry in DEFERRED_FILES, f"{owner}: {entry} does not exist"


def test_package_version_matches_pyproject():
    import beaver

    project = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["name"] == "project-beaver"
    assert beaver.__version__ == project["version"]
