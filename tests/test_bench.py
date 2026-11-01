"""Unit tests for the deterministic parts of bench/bench.py. No network, no model calls."""

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("bench", Path(__file__).parent.parent / "bench" / "bench.py")
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def test_load_env_handles_comments_quotes_and_export(tmp_path):
    env = tmp_path / ".env"
    env.write_text('# a comment\n\nOPENROUTER_API_KEY="sk-or-123"\nexport OTHER=\'x=y\'\nNOT A PAIR\n')
    assert bench.load_env(env) == {"OPENROUTER_API_KEY": "sk-or-123", "OTHER": "x=y"}


def test_load_env_missing_file_is_empty(tmp_path):
    assert bench.load_env(tmp_path / "absent.env") == {}


def test_claude_env_routes_through_openrouter_with_a_fresh_config(tmp_path):
    base = {"PATH": "/usr/bin", "ANTHROPIC_API_KEY": "sk-ant-personal", "ANTHROPIC_MODEL": "opus",
            "CLAUDECODE": "1", "CLAUDE_CODE_ENTRYPOINT": "cli", "CLAUDE_CONFIG_DIR": "/home/me/.claude"}
    env = bench.claude_env(base, "sk-or-123", tmp_path)
    assert env["PATH"] == "/usr/bin"
    assert env["ANTHROPIC_BASE_URL"] == "https://openrouter.ai/api"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "sk-or-123"
    assert env["ANTHROPIC_API_KEY"] == ""  # never the personal key
    assert env["CLAUDE_CONFIG_DIR"] == str(tmp_path)
    assert "ANTHROPIC_MODEL" not in env and "CLAUDECODE" not in env and "CLAUDE_CODE_ENTRYPOINT" not in env


def test_claude_env_carries_no_other_dotenv_keys(tmp_path):
    env = bench.claude_env({"PATH": "/usr/bin"}, "sk-or-123", tmp_path)
    assert not any("TYPESAFE" in key for key in env)


def test_instruction_files_above_finds_parent_claude_md(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# parent instructions\n")
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert str(tmp_path / "CLAUDE.md") in bench.instruction_files_above(nested)


def test_sandbox_reports_changes_and_boundary_violations(tmp_path):
    workspace = tmp_path / "ws"
    (workspace / "notes").mkdir(parents=True)
    (workspace / "notes" / "a.md").write_text("seed\n")
    sandbox = bench.make_sandbox(workspace)
    assert (sandbox / "notes" / "a.md").read_text() == "seed\n"
    assert bench.changed_files(sandbox) == []

    (sandbox / "generated").mkdir()
    (sandbox / "generated" / "review.md").write_text("ok\n")
    (sandbox / "notes" / "a.md").write_text("edited by a skill\n")
    changed = bench.changed_files(sandbox)
    assert changed == ["generated/review.md", "notes/a.md"]
    assert bench.outside_generated(changed) == ["notes/a.md"]


def test_sandbox_never_receives_env_files(tmp_path):
    workspace = tmp_path / "ws"
    (workspace / "sub").mkdir(parents=True)
    for name in (".env", ".env.local", ".env.example", "sub/.env", "notes.md"):
        (workspace / name).write_text("x\n")
    (workspace / ".bench" / "runs").mkdir(parents=True)
    sandbox = bench.make_sandbox(workspace)
    copied = sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob("*") if ".git" not in p.parts)
    assert copied == [".env.example", "notes.md", "sub"]


def test_final_result_takes_the_last_result_event():
    lines = ["not json", json.dumps({"type": "system"}), json.dumps({"type": "result", "result": "first"}),
             json.dumps({"type": "result", "result": "ok", "total_cost_usd": 0.01})]
    assert bench.final_result(lines)["result"] == "ok"
    assert bench.final_result([]) == {}
