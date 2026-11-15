"""Observe the registered project repos from the Beaver home, read-only.

Beaver is the hub: `projects/registry.yaml` lists the repos around it. This reads
each local clone with git and never writes to one. A project whose privacy says
`external_model_use: forbidden` is listed but not read (docs/design.md,
"Connecting projects"). Deterministic and offline: no model, zero tokens.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

from beaver.status import commits_since


@dataclass
class Project:
    id: str
    state: str
    practises: list
    note: str = ""            # why it was not read, in plain words
    branch: str = ""
    last_commit: str = ""     # "2026-11-10 fix the judge prompt"
    unreviewed: int | None = None
    uncommitted: int = 0

    def line(self):
        if self.note:
            return f"  {self.id:<28}{self.state:<9}{self.note}"
        review = "no review yet" if self.unreviewed is None else f"{self.unreviewed} since review"
        extra = f" · {self.uncommitted} uncommitted" if self.uncommitted else ""
        return f"  {self.id:<28}{self.state:<9}{self.branch} · {review}{extra} · last: {self.last_commit}"


def git(repo, *args):
    run = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return run.stdout.strip() if run.returncode == 0 else None


def observe_projects(root):
    """One Project per registry entry, in registry order."""
    root = Path(root)
    registry_file = root / "projects" / "registry.yaml"
    registry = (yaml.safe_load(registry_file.read_text(encoding="utf-8")) or {}) if registry_file.is_file() else {}
    seen = []
    for entry in registry.get("projects") or []:
        project = Project(id=entry["id"], state=entry.get("state", "active"), practises=entry.get("practises") or [])
        seen.append(project)
        if (entry.get("privacy") or {}).get("external_model_use") == "forbidden":
            project.note = "not read: marked confidential"
            continue
        clone = (entry.get("source") or {}).get("path")
        if not clone:
            project.note = "not read: no local path in the registry"
            continue
        repo = Path(clone).expanduser()
        repo = repo if repo.is_absolute() else root / repo
        if git(repo, "rev-parse", "--git-dir") is None:
            project.note = f"not read: no git repo at {clone}"
            continue
        project.branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "?"
        project.last_commit = git(repo, "log", "-1", "--format=%cs %s") or "no commits"
        reviewed = (entry.get("review") or {}).get("last_reviewed_commit")
        project.unreviewed = commits_since(repo, reviewed) if reviewed else None
        project.uncommitted = len((git(repo, "status", "--porcelain") or "").splitlines())
    return seen


def render(projects):
    if not projects:
        return "No projects registered yet. Add one to projects/registry.yaml."
    return "\n".join(["Projects"] + [p.line() for p in projects])
