"""The progress check: what is waiting in a workspace, and the one next step.

Deterministic and offline: no model, zero tokens. It reads the workspace and the
local clones of registered projects (read-only), and never writes to them.
Set BEAVER_NOW (YYYY-MM-DD) to check a workspace as of a fixed day.
"""

import os
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from beaver.records import split_frontmatter

AGING_DAYS = 14  # docs/design.md: "inquiries open for more than 2 weeks"


@dataclass
class Status:
    as_of: date
    inbox_captures: int = 0
    aging_inquiries: list[str] = field(default_factory=list)
    days_since_reflection: int | None = None
    unreviewed_commits: dict[str, int] = field(default_factory=dict)
    over_limit: dict[str, dict] = field(default_factory=dict)
    next_step: str | None = None

    def waiting(self):
        """Lines for what is waiting, most actionable first, in plain words."""
        lines = []
        for inquiry in self.aging_inquiries:
            lines.append(("question", f"{inquiry} has been open more than {AGING_DAYS} days"))
        for project, count in self.unreviewed_commits.items():
            if count:
                lines.append(("review", f"{project}: {count} commit{'s' * (count != 1)} since the last review"))
        if self.inbox_captures:
            lines.append(("inbox", f"{self.inbox_captures} capture{'s' * (self.inbox_captures != 1)} to sort"))
        if self.days_since_reflection is not None and self.days_since_reflection > 7:
            lines.append(("reflection", f"last one {self.days_since_reflection} days ago"))
        for name, over in self.over_limit.items():
            label = name.replace("_", " ")
            lines.append(("limit", f"{over['count']} {label} (your limit is {over['limit']})"))
        return lines

    def render(self):
        out = [f"Waiting · {self.as_of:%a %b} {self.as_of.day}"]
        waiting = self.waiting()
        out += [f"  {kind:<11}{text}" for kind, text in waiting] or ["  Nothing waiting."]
        out.append("")
        out.append(f"Next: {self.next_step}" if self.next_step
                   else "Next: write one goal for this week in learner/now.md.")
        return "\n".join(out)


def today(env=None):
    env = os.environ if env is None else env
    return date.fromisoformat(env["BEAVER_NOW"]) if env.get("BEAVER_NOW") else date.today()


def frontmatter(path):
    try:
        return split_frontmatter(Path(path).read_text(encoding="utf-8"))[0]
    except (OSError, ValueError):
        return {}


def as_date(value):
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def commits_since(repo, ref):
    """Commits in a local clone since `ref` (all of them when ref is empty); None if unreadable."""
    span = f"{ref}..HEAD" if ref else "HEAD"
    run = subprocess.run(["git", "-C", str(repo), "rev-list", "--count", span], capture_output=True, text=True)
    return int(run.stdout.strip()) if run.returncode == 0 else None


def check_status(root, as_of=None):
    root = Path(root)
    status = Status(as_of=as_of or today())

    inbox = root / "learning" / "inbox.md"
    if inbox.is_file():
        status.inbox_captures = sum(1 for line in inbox.read_text(encoding="utf-8").splitlines()
                                    if line.lstrip().startswith("- "))

    for path in sorted((root / "learning" / "inquiries").glob("*.md")):
        data = frontmatter(path)
        if data.get("status", "open") == "open" and data.get("opened"):
            if (status.as_of - as_date(data["opened"])).days > AGING_DAYS:
                status.aging_inquiries.append(data["id"])

    dates = [as_date(d["date"]) for p in (root / "reflections").glob("*.md") if (d := frontmatter(p)).get("date")]
    if dates:
        status.days_since_reflection = (status.as_of - max(dates)).days

    registry_file = root / "projects" / "registry.yaml"
    registry = (yaml.safe_load(registry_file.read_text(encoding="utf-8")) or {}) if registry_file.is_file() else {}
    projects = [p for p in registry.get("projects") or [] if p.get("state", "active") == "active"]
    for project in projects:
        clone = (project.get("source") or {}).get("path")
        if clone:
            repo = Path(clone).expanduser()
            repo = repo if repo.is_absolute() else root / repo
            count = commits_since(repo, (project.get("review") or {}).get("last_reviewed_commit"))
            if count is not None:
                status.unreviewed_commits[project["id"]] = count

    limits = {"active_projects": 2, "active_sprints": 1, **(registry.get("limits") or {})}
    sprints = [p for p in (root / "sprints").glob("*.md") if frontmatter(p).get("status") == "active"]
    for name, count in (("active_projects", len(projects)), ("active_sprints", len(sprints))):
        if count > limits[name]:
            status.over_limit[name] = {"count": count, "limit": limits[name]}

    status.next_step = frontmatter(root / "learner" / "now.md").get("next_step")
    return status


def write_status(root, status):
    """Write generated/status.md, which AGENTS.md tells assistants to read first."""
    target = Path(root) / "generated" / "status.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("<!-- written by the beaver progress check; no model -->\n```text\n"
                      + status.render() + "\n```\n", encoding="utf-8")
    return target


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Show what is waiting in a Beaver workspace, and the next step.")
    parser.add_argument("workspace", nargs="?", default=".", type=Path)
    parser.add_argument("--write", action="store_true", help="also write generated/status.md")
    args = parser.parse_args(argv)
    status = check_status(args.workspace)
    if args.write:
        write_status(args.workspace, status)
    print(status.render())
    return 0
