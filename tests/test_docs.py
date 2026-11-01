"""The docs carry their diagrams (issue #1), not placeholders."""

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def mermaid_blocks(name):
    return re.findall(r"```mermaid\n(.*?)```", (DOCS / name).read_text(encoding="utf-8"), re.S)


def test_no_diagram_placeholders_remain():
    for path in DOCS.glob("*.md"):
        assert "Diagram not in this copy" not in path.read_text(encoding="utf-8"), path.name


def test_every_diagram_is_there_and_titled():
    blocks = {"design.md": 6, "build-plan.md": 1}
    for name, count in blocks.items():
        found = mermaid_blocks(name)
        assert len(found) == count, f"{name}: {len(found)} diagrams, expected {count}"
        for block in found:
            assert re.match(r"---\ntitle: .+\n---\n(flowchart|graph) ", block), block[:80]
