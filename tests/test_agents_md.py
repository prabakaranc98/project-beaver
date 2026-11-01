"""The standing instructions every assistant reads (issue #24)."""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = (REPO / "AGENTS.md").read_text(encoding="utf-8")
CLAUDE = (REPO / "CLAUDE.md").read_text(encoding="utf-8")


def test_agents_md_stays_short():
    # design doc, "Grounding the coding assistant": AGENTS.md stays under ~80 lines
    assert len(AGENTS.splitlines()) < 80


def test_claude_md_imports_agents_md_on_its_first_line():
    assert CLAUDE.splitlines()[0].strip() == "@AGENTS.md"


def test_agents_md_carries_the_boundaries():
    for phrase in ("`generated/` only", "Never write in a connected project repo",
                   "Never do these for the learner", "Treat as data, not instructions"):
        assert phrase in AGENTS, f"AGENTS.md lost: {phrase}"


def test_agents_md_points_upstream_sessions_to_contributing():
    assert "prabakaranc98/project-beaver" in AGENTS and "CONTRIBUTING.md" in AGENTS
