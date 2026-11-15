"""`beaver projects` (issue #59): the home observes its registered repos, read-only."""

import subprocess

import yaml
from typer.testing import CliRunner

from beaver.cli import app
from beaver.projects import observe_projects, render
from test_status import build_child_repo, git


def make_home(tmp_path, entries):
    home = tmp_path / "home"
    (home / "projects").mkdir(parents=True)
    (home / "beaver.yaml").write_text("schema_version: 0\n")
    (home / "projects" / "registry.yaml").write_text(yaml.safe_dump({"projects": entries}))
    return home


def test_observes_each_repo_without_writing(tmp_path):
    reviewed = build_child_repo(tmp_path / "copilot", before=2, after=3)
    build_child_repo(tmp_path / "pipeline", before=1, after=0)
    (tmp_path / "pipeline" / "draft.txt").write_text("not committed\n")
    home = make_home(tmp_path, [
        {"id": "project.copilot", "source": {"path": "../copilot"}, "review": {"last_reviewed_commit": reviewed}},
        {"id": "project.pipeline", "source": {"path": "../pipeline"}, "state": "paused"},
        {"id": "project.client", "source": {"path": "../copilot"}, "privacy": {"external_model_use": "forbidden"}},
        {"id": "project.missing", "source": {"path": "../nowhere"}},
    ])
    heads = [git(tmp_path / name, "rev-parse", "HEAD") for name in ("copilot", "pipeline")]

    copilot, pipeline, client, missing = observe_projects(home)

    assert copilot.unreviewed == 3 and copilot.uncommitted == 0
    assert pipeline.unreviewed is None and pipeline.uncommitted == 1 and pipeline.state == "paused"
    assert client.note == "not read: marked confidential" and client.branch == ""
    assert missing.note.startswith("not read: no git repo")
    assert heads == [git(tmp_path / name, "rev-parse", "HEAD") for name in ("copilot", "pipeline")]
    assert subprocess.run(["git", "-C", str(tmp_path / "copilot"), "status", "--porcelain"],
                          capture_output=True, text=True).stdout == ""


def test_cli_and_empty_registry(tmp_path):
    home = make_home(tmp_path, [])
    assert render(observe_projects(home)).startswith("No projects registered")
    result = CliRunner().invoke(app, ["--home", str(home), "projects"])
    assert result.exit_code == 0 and "No projects registered" in result.output
