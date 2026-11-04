"""The progress check (issue #30) against the expectations in tests/golden/.

Rendered output is snapshotted in tests/golden/<name>.status.txt.
Regenerate after an intended change with: UPDATE_GOLDEN=1 pytest tests/test_status.py
"""

import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from beaver.cli import app
from beaver.status import check_status, write_status

REPO = Path(__file__).resolve().parent.parent
GOLDEN = REPO / "tests" / "golden"
WITH_STATUS = [p for p in sorted(GOLDEN.glob("*.yaml")) if "status" in yaml.safe_load(p.read_text())]


def git(repo, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=env).stdout.strip()


def build_child_repo(path, before, after):
    """`before` commits (the last one is the reviewed one), then `after` more. Returns the reviewed hash."""
    path.mkdir(parents=True)
    git(path, "init", "-q")
    for i in range(before + after):
        (path / "log.txt").write_text(f"change {i}\n")
        git(path, "add", "-A")
        git(path, "commit", "-q", "-m", f"change {i}")
        if i == before - 1:
            reviewed = git(path, "rev-parse", "HEAD")
    return reviewed


def prepared(spec, tmp_path):
    """A copy of the fixture workspace, with any child repos it describes built in it."""
    workspace = tmp_path / "ws"
    shutil.copytree(REPO / spec["workspace"], workspace)
    if spec.get("child_repos"):
        registry_file = workspace / "projects" / "registry.yaml"
        registry = yaml.safe_load(registry_file.read_text())
        for project in registry["projects"]:
            plan = spec["child_repos"].get(project["id"])
            if plan:
                reviewed = build_child_repo(workspace / project["source"]["path"],
                                            plan["commits_before_review"], plan["commits_after_review"])
                project["review"]["last_reviewed_commit"] = reviewed
        registry_file.write_text(yaml.safe_dump(registry, sort_keys=False))
    return workspace


@pytest.mark.parametrize("path", WITH_STATUS, ids=lambda p: p.stem)
def test_status_matches_the_expectations(path, tmp_path):
    spec = yaml.safe_load(path.read_text())
    status = check_status(prepared(spec, tmp_path), as_of=spec["as_of"])
    for key, expected in spec["status"].items():
        assert getattr(status, key) == expected, key


@pytest.mark.parametrize("path", WITH_STATUS, ids=lambda p: p.stem)
def test_rendered_status_matches_the_snapshot(path, tmp_path):
    spec = yaml.safe_load(path.read_text())
    rendered = check_status(prepared(spec, tmp_path), as_of=spec["as_of"]).render() + "\n"
    snapshot = GOLDEN / f"{path.stem}.status.txt"
    if os.environ.get("UPDATE_GOLDEN"):
        snapshot.write_text(rendered, encoding="utf-8")
    assert snapshot.read_text(encoding="utf-8") == rendered


def test_an_empty_workspace_asks_for_one_goal(tmp_path):
    rendered = check_status(tmp_path, as_of=date(2026, 11, 10)).render()
    assert "Nothing waiting." in rendered and "learner/now.md" in rendered


def test_write_status_lands_in_generated(tmp_path):
    target = write_status(tmp_path, check_status(tmp_path, as_of=date(2026, 11, 10)))
    assert target == tmp_path / "generated" / "status.md" and "Waiting" in target.read_text()


def test_bare_beaver_shows_the_next_step_and_writes_the_status_file(tmp_path):
    workspace = tmp_path / "ws"
    shutil.copytree(REPO / "core" / "examples", workspace)
    runner = CliRunner()
    result = runner.invoke(app, ["--home", str(workspace)], env={"BEAVER_NOW": "2026-11-10"})
    assert result.exit_code == 0 and "Next: Hand-label 20 tickets" in result.output
    assert (workspace / "generated" / "status.md").is_file()
    quiet = tmp_path / "quiet"
    shutil.copytree(REPO / "core" / "examples", quiet)
    assert runner.invoke(app, ["--home", str(quiet), "status"]).exit_code == 0
    assert not (quiet / "generated" / "status.md").exists()  # `beaver status` writes nothing


def test_init_then_doctor_from_anywhere(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    shutil.copytree(REPO / "core" / "examples", workspace)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.delenv("BEAVER_HOME", raising=False)
    env = {"XDG_CONFIG_HOME": str(tmp_path / "config")}
    runner = CliRunner()
    assert runner.invoke(app, [], env=env).exit_code == 1  # no home yet
    assert runner.invoke(app, ["init", str(tmp_path / "elsewhere")], env=env).exit_code == 1  # not a workspace
    assert runner.invoke(app, ["init", str(workspace)], env=env).exit_code == 0
    doctor = runner.invoke(app, ["doctor"], env=env)
    assert doctor.exit_code == 0 and "found by config" in doctor.output and "Records  12" in doctor.output
