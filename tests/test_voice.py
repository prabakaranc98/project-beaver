"""Learner-facing text follows core/principles/voice.md (issue #63)."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOICE = REPO / "core" / "principles" / "voice.md"


def words_to_drop():
    text = VOICE.read_text(encoding="utf-8")
    block = re.search(r"<!-- words-to-drop:start -->(.*?)<!-- words-to-drop:end -->", text, re.S).group(1)
    return [line[2:].strip().lower() for line in block.splitlines() if line.startswith("- ")]


def learner_facing_files():
    yield REPO / "AGENTS.md"
    yield REPO / "CLAUDE.md"
    for folder in ("core/principles", "core/templates", ".agents/skills"):
        yield from sorted((REPO / folder).rglob("*.md"))
    yield from sorted((REPO / "tests" / "golden").glob("*.txt"))  # what the CLI prints, as snapshotted


def test_the_list_parses():
    assert "consider" in words_to_drop() and len(words_to_drop()) >= 5


def test_learner_facing_text_avoids_the_words_to_drop():
    banned = words_to_drop()
    hits = []
    for path in learner_facing_files():
        text = path.read_text(encoding="utf-8")
        if path == VOICE:  # the list itself and its "sleepy" examples quote the words on purpose
            text = re.sub(r"<!-- words-to-drop:start -->.*?<!-- words-to-drop:end -->", "", text, flags=re.S)
            text = text.split("## Sleepy, plain, alive")[0]
        for phrase in banned:
            if re.search(rf"\b{re.escape(phrase)}\b", text, re.IGNORECASE):
                hits.append(f"{path.relative_to(REPO)}: {phrase!r}")
    assert hits == [], "sleepy words in learner-facing text: " + ", ".join(hits)


def test_the_moves_name_both_failure_modes():
    moves = (REPO / "core" / "principles" / "moves.md").read_text(encoding="utf-8")
    assert "Over-scaffolding" in moves and "Pushing for rigor" in moves
