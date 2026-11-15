"""Build a test workspace: one Beaver home with three project repos around it.

    python tools/make_test_workspace.py [TARGET]     # default: .bench/test-workspace

    TARGET/home/                the Beaver home (a copy of core/examples, plus a registry)
    TARGET/repos/support-copilot   6 commits, 4 since the last review
    TARGET/repos/paper-notes       3 commits, never reviewed, one uncommitted file
    TARGET/repos/client-sync       marked confidential, so Beaver lists it and does not read it

Rebuilds from scratch each run. Then try:
    beaver --home TARGET/home            # what is waiting, and the next step
    beaver --home TARGET/home projects   # the repos around the home, read-only
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ENV = {**os.environ, "GIT_AUTHOR_NAME": "Sample Learner", "GIT_AUTHOR_EMAIL": "learner@example.com",
       "GIT_COMMITTER_NAME": "Sample Learner", "GIT_COMMITTER_EMAIL": "learner@example.com"}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=ENV).stdout.strip()


def make_repo(path, commits):
    """One commit per (file, text, message). Returns the hashes in order."""
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    hashes = []
    for name, text, message in commits:
        (path / name).parent.mkdir(parents=True, exist_ok=True)
        (path / name).write_text(text)
        git(path, "add", "-A")
        git(path, "commit", "-q", "-m", message)
        hashes.append(git(path, "rev-parse", "--short", "HEAD"))
    return hashes


def build(target):
    target = Path(target).resolve()
    if target.exists():
        if not (target / ".beaver-test-workspace").is_file():
            sys.exit(f"{target} exists and was not made by this script. Pick another folder.")
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / ".beaver-test-workspace").write_text("made by tools/make_test_workspace.py; safe to delete\n")

    copilot = make_repo(target / "repos" / "support-copilot", [
        ("README.md", "# Support copilot\nAnswers support tickets from the help centre.\n", "feat: start the support copilot"),
        ("evals/tickets.jsonl", '{"id": 1, "question": "How do I reset my password?"}\n', "test: add the first eval tickets"),
        ("evals/harness.py", "def score(answer, reference):\n    return answer.strip() == reference.strip()\n", "feat: score answers against references"),
        ("evals/judge.py", "PROMPT = 'Is the answer supported by the cited article? yes/no'\n", "feat: add an LLM judge for citations"),
        ("evals/harness.py", "def score(answer, reference):\n    return answer.strip().lower() == reference.strip().lower()\n", "fix: ignore case when scoring"),
        ("evals/labels.csv", "ticket,human,judge\n1,yes,yes\n", "test: start hand labels to compare with the judge"),
    ])
    make_repo(target / "repos" / "paper-notes", [
        ("README.md", "# Paper notes\nNotes on papers about LLM evaluation.\n", "docs: start the reading notes"),
        ("judging-llm-judges.md", "# Judging LLM-as-a-judge\nOpen question: how much agreement is enough?\n", "docs: notes on judge agreement"),
        ("eval-sets.md", "# Building eval sets\nSample from real tickets, not invented ones.\n", "docs: notes on eval sets"),
    ])
    (target / "repos" / "paper-notes" / "draft-calibration.md").write_text("# Calibration (draft)\n")
    make_repo(target / "repos" / "client-sync", [
        ("README.md", "# Client sync\nConfidential client work.\n", "chore: start"),
    ])

    home = target / "home"
    shutil.copytree(REPO / "core" / "examples", home)
    (home / "generated").mkdir(exist_ok=True)
    registry = {
        "limits": {"active_projects": 2, "ideas_under_evaluation": 5, "active_sprints": 1, "days_since_review": 30},
        "projects": [
            {"id": "project.support-copilot", "source": {"type": "local", "path": "../repos/support-copilot"},
             "relationship": "beaver-started", "state": "active", "practises": ["capability.llm-evaluation"],
             "brief": "brief.support-copilot-evals",
             "review": {"trigger": "manual", "last_reviewed_commit": copilot[1]},
             "privacy": {"classification": "private", "external_model_use": "allowed"}},
            {"id": "project.paper-notes", "source": {"type": "local", "path": "../repos/paper-notes"},
             "relationship": "existing", "state": "active", "practises": ["capability.llm-evaluation"],
             "review": {"trigger": "manual", "last_reviewed_commit": None},
             "privacy": {"classification": "public", "external_model_use": "allowed"}},
            {"id": "project.client-sync", "source": {"type": "local", "path": "../repos/client-sync"},
             "relationship": "existing", "state": "paused", "practises": [],
             "review": {"trigger": "manual", "last_reviewed_commit": None},
             "privacy": {"classification": "client-confidential", "external_model_use": "forbidden"}},
        ],
    }
    (home / "projects" / "registry.yaml").write_text(yaml.safe_dump(registry, sort_keys=False))
    return target


if __name__ == "__main__":
    built = build(sys.argv[1] if len(sys.argv) > 1 else REPO / ".bench" / "test-workspace")
    print(f"Built {built}\nTry:  beaver --home '{built}/home'\n      beaver --home '{built}/home' projects")
