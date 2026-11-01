"""Check a Beaver workspace: every record fits its schema, every ID it points to
exists, and every [[wikilink]] matches a page. Deterministic and offline: no model.

    beaver validate <workspace>          # or: python tools/validate.py <workspace>
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from beaver.records import RECORD_LOCATIONS, RECORD_TYPES, WORKSPACE_FOLDERS, Registry, split_frontmatter

ID = re.compile(r"[a-z]+\.[a-z0-9][a-z0-9-]*")
RESOLVABLE = set(RECORD_TYPES) | {"project"}  # domains, notes and reviews have no records yet
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


@dataclass(frozen=True, order=True)
class Problem:
    file: str
    kind: str  # schema | unresolved-id | broken-wikilink | duplicate-id
    ref: str  # the field, ID or wikilink involved
    message: str


@dataclass
class Report:
    problems: list[Problem] = field(default_factory=list)
    checked: int = 0

    def render(self):
        if not self.problems:
            return f"All {self.checked} records check out." if self.checked else "No records yet."
        files = len({p.file for p in self.problems})
        lines = [f"{p.file}: {p.message}" for p in self.problems]
        lines.append(f"{len(self.problems)} problem{'s' * (len(self.problems) != 1)} in {files} "
                     f"file{'s' * (files != 1)}. Fix the first one and run it again.")
        return "\n".join(lines)


def record_files(root):
    for location in RECORD_LOCATIONS:
        target = root / location
        if target.is_file():
            yield target
        elif target.is_dir():
            yield from sorted(target.rglob("*.md"))


def schema_problems(rel, error):
    problems = []
    for e in error.errors():
        where = ".".join(str(part) for part in e["loc"])
        if e["type"] == "missing":
            message = f"needs {where}"
        elif e["type"] == "extra_forbidden":
            message = f"has an unknown key {where} (a typo?)"
        else:
            message = (f"{where}: " if where else "") + e["msg"].removeprefix("Value error, ")
        problems.append(Problem(rel, "schema", where, message))
    return problems


def references(data):
    """Every value that is exactly a `type.slug` ID, except the record's own id."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key != "id":
                yield from references(value)
    elif isinstance(data, list):
        for item in data:
            yield from references(item)
    elif isinstance(data, str) and ID.fullmatch(data):
        yield data


def validate_workspace(root):
    root = Path(root)
    report, ids, linking = Report(), {}, []

    for path in record_files(root):
        rel = path.relative_to(root).as_posix()
        report.checked += 1
        try:
            data, _body = split_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError:
            report.problems.append(Problem(rel, "schema", "frontmatter", "needs a --- YAML frontmatter block at the top"))
            continue
        own_id = str(data.get("id", ""))
        if ID.fullmatch(own_id):  # register it even if the record is invalid, so one bad file doesn't cascade
            if own_id in ids:
                report.problems.append(Problem(rel, "duplicate-id", own_id, f"uses {own_id}, already used by {ids[own_id]}"))
            else:
                ids[own_id] = rel
        kind = own_id.split(".", 1)[0]
        if kind not in RECORD_TYPES:
            report.problems.append(Problem(rel, "schema", "id", f"has an id of unknown type: {own_id or 'none'}"))
            continue
        try:
            RECORD_TYPES[kind].model_validate(data)
        except ValidationError as error:
            report.problems.extend(schema_problems(rel, error))
        linking.append((rel, data))

    registry = root / "projects" / "registry.yaml"
    if registry.is_file():
        rel = "projects/registry.yaml"
        report.checked += 1
        data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
        try:
            Registry.model_validate(data)
        except ValidationError as error:
            report.problems.extend(schema_problems(rel, error))
        for project in data.get("projects") or []:
            if isinstance(project, dict) and ID.fullmatch(str(project.get("id", ""))):
                ids.setdefault(project["id"], rel)
        linking.append((rel, data))

    for rel, data in linking:
        for ref in sorted(set(references(data))):
            if ref.split(".", 1)[0] in RESOLVABLE and ref not in ids:
                report.problems.append(Problem(rel, "unresolved-id", ref, f"points to {ref}, which doesn't exist"))

    pages = [p for folder in WORKSPACE_FOLDERS if (root / folder).is_dir() for p in sorted((root / folder).rglob("*.md"))]
    names = {p.stem for p in pages}
    for path in sorted(pages):
        for target in sorted({t.strip() for t in WIKILINK.findall(path.read_text(encoding="utf-8"))}):
            if target.split("/")[-1] not in names:
                rel = path.relative_to(root).as_posix()
                report.problems.append(Problem(rel, "broken-wikilink", target, f"[[{target}]] doesn't match any page"))

    report.problems.sort()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check every record, ID and [[wikilink]] in a Beaver workspace.")
    parser.add_argument("workspace", nargs="?", default=".", type=Path)
    report = validate_workspace(parser.parse_args(argv).workspace)
    print(report.render())
    return 1 if report.problems else 0


if __name__ == "__main__":
    sys.exit(main())
