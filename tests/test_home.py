"""Finding the learner's home (issue #57). Every test uses its own config dir."""

import pytest

from beaver.home import config_path, remember_home, resolve_home


def workspace(root):
    root.mkdir(parents=True, exist_ok=True)
    (root / "beaver.yaml").write_text("schema_version: 0\n")
    return root


@pytest.fixture
def env(tmp_path):
    return {"XDG_CONFIG_HOME": str(tmp_path / "config")}


def test_an_explicit_path_wins(tmp_path, env):
    ws = workspace(tmp_path / "ws")
    found = resolve_home(explicit=ws, start=tmp_path, env={**env, "BEAVER_HOME": str(tmp_path / "other")})
    assert found.path == ws.resolve() and found.found_by == "explicit"


def test_beaver_home_comes_next(tmp_path, env):
    ws = workspace(tmp_path / "ws")
    found = resolve_home(start=tmp_path, env={**env, "BEAVER_HOME": str(ws)})
    assert found.path == ws.resolve() and found.found_by == "BEAVER_HOME"


def test_the_nearest_workspace_above_the_current_folder(tmp_path, env):
    ws = workspace(tmp_path / "ws")
    nested = ws / "learning" / "concepts"
    nested.mkdir(parents=True)
    found = resolve_home(start=nested, env=env)
    assert found.path == ws.resolve() and found.found_by == "current folder"


def test_from_inside_a_child_repo_the_remembered_home_is_used(tmp_path, env):
    ws = workspace(tmp_path / "ws")
    child = tmp_path / "code" / "support-copilot" / "src"
    child.mkdir(parents=True)
    assert resolve_home(start=child, env=env) is None  # nothing remembered yet
    saved = remember_home(ws, env=env)
    assert saved == config_path(env) and saved.is_file()
    found = resolve_home(start=child, env=env)
    assert found.path == ws.resolve() and found.found_by == "config"


def test_only_a_workspace_can_be_remembered(tmp_path, env):
    with pytest.raises(ValueError, match="not a Beaver workspace"):
        remember_home(tmp_path / "not-a-workspace", env=env)
