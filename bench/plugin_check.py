#!/usr/bin/env python3
"""Live check of the Claude Code plugin against the contained test workspace.

    python bench/plugin_check.py [SCENARIO ...] [--model haiku] [--budget 0.50]

Each scenario rebuilds .bench/test-workspace (one Beaver home, three project repos),
runs `claude -p` there with this repo loaded as a plugin, and checks what was written.
Everything stays inside .bench/ (git-ignored):
- a fresh CLAUDE_CONFIG_DIR per run, so the author's settings, memory and plugins stay out
- BEAVER_HOME points at the test home, and XDG_CONFIG_HOME at a throwaway folder
- models go through OpenRouter with the key in .env, as in bench.py

With --login the run uses your own Claude login instead of OpenRouter. That keeps your
config folder, so your global CLAUDE.md and settings are read too; sessions are not saved.

Limit: the workspace sits inside this repo, so Claude Code also reads the CLAUDE.md and
AGENTS.md files in the folders above it. bench.py's temp-dir sandbox avoids that.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from bench import REPO, RUNS, claude_env, final_result, openrouter_key, openrouter_usage, settled_usage  # noqa: E402
from make_test_workspace import build  # noqa: E402

WORKSPACE = REPO / ".bench" / "test-workspace"
ALLOWED = ["Bash(beaver:*)", "Bash(git log:*)", "Bash(git diff:*)", "Bash(git show:*)", "Bash(git -C:*)", "Read", "Glob", "Grep"]


def snapshot(root):
    """Every file's hash, plus each child repo's HEAD. `.git` internals are left out."""
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.relative_to(root).parts:
            files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for repo in sorted((root / "repos").iterdir()):
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        files[f"repos/{repo.name}@HEAD"] = head
    return files


def changes(before, after):
    return sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))


def tool_inputs(lines):
    """Every tool call the model made, as (tool name, input as text)."""
    calls = []
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    calls.append((block["name"], json.dumps(block.get("input", {}))))
    return calls


def run(name, prompt, cwd, model, budget, login=False):
    build(WORKSPACE)
    home, config = WORKSPACE / "home", Path(tempfile.mkdtemp(prefix="beaver-config-"))
    shim = WORKSPACE / ".bin"
    shim.mkdir()
    (shim / "beaver").write_text(f'#!/bin/sh\nexec uv run --quiet --project "{REPO}" beaver "$@"\n')
    (shim / "beaver").chmod(0o755)
    if login:
        key = None
        env = {k: v for k, v in os.environ.items() if not (k.startswith("CLAUDE_CODE_") or k == "CLAUDECODE")}
    else:
        key = openrouter_key()
        env = claude_env(os.environ, key, config)
    env.update({"BEAVER_HOME": str(home), "XDG_CONFIG_HOME": str(WORKSPACE / ".xdg"),
                "PATH": f"{shim}{os.pathsep}{env['PATH']}"})
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose",
           "--include-hook-events", "--max-budget-usd", str(budget), "--no-session-persistence",
           "--permission-mode", "acceptEdits", "--plugin-dir", str(REPO), "--add-dir", str(WORKSPACE),
           "--allowedTools", *ALLOWED]
    before, spent_before = snapshot(WORKSPACE), openrouter_usage(key) if key else None
    proc = subprocess.run(cmd, cwd=WORKSPACE / cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    spent_after = settled_usage(key, spent_before) if key else None
    changed = [c for c in changes(before, snapshot(WORKSPACE)) if not c.startswith((".bin/", ".xdg/"))]
    lines = proc.stdout.splitlines()
    result = final_result(lines)
    run_dir = RUNS / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-plugin-{name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "stream.jsonl").write_text(proc.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
    for path in changed:  # keep what the run wrote, since the workspace is rebuilt next time
        source = WORKSPACE / path
        if source.is_file():
            (run_dir / "written" / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, run_dir / "written" / path)
    shutil.rmtree(config, ignore_errors=True)
    return {
        "name": name, "stdout": proc.stdout, "calls": tool_inputs(lines), "changed": changed,
        "reply": result.get("result") or "", "is_error": result.get("is_error", proc.returncode != 0),
        "cost": (f"OpenRouter ${round(spent_after - spent_before, 4)}" if None not in (spent_before, spent_after)
                 else f"Claude Code estimate ${round(result.get('total_cost_usd') or 0, 4)}"),
        "log": str(run_dir.relative_to(REPO)),
    }


def outside_generated(changed):
    return [c for c in changed if not c.startswith("home/generated/")]


def touched(calls, needle, tools=("Read", "Bash", "Grep", "Glob")):
    return [f"{tool}: {text[:120]}" for tool, text in calls if tool in tools and needle in text]


SCENARIOS = {
    "hook": dict(
        cwd="repos/paper-notes", prompt="Reply with the single word: ok",
        checks=lambda r: {
            "the session hook's status reached the session": "Beaver progress check" in r["stdout"],
            "the hook listed the project repos": "project.support-copilot" in r["stdout"],
            "the four skills are loaded": all(f"beaver:{s}" in r["stdout"] for s in ("onboard", "orient", "frame-challenge", "review-evidence")),
            "nothing was written": not r["changed"],
        }),
    "orient": dict(
        cwd="repos/paper-notes", prompt="/beaver:orient",
        checks=lambda r: {
            "nothing was written": not r["changed"],
            "it names the step from now.md": "label" in r["reply"].lower(),
            "it ends by offering to start": "start?" in r["reply"].lower()[-200:],
            "it uses the help level from now.md (hint)": "hint" in r["reply"].lower(),
        }),
    "review": dict(
        cwd="home", prompt="/beaver:review-evidence project.support-copilot, the commits since the last review",
        checks=lambda r: {
            "a review was written under generated/reviews": any(c.startswith("home/generated/reviews/") for c in r["changed"]),
            "nothing was written outside generated/": not outside_generated(r["changed"]),
            "it read the project's commits": bool(touched(r["calls"], "support-copilot")),
        }),
    "confidential": dict(
        cwd="home", prompt="/beaver:review-evidence project.client-sync, all commits",
        checks=lambda r: {
            "it never read the confidential repo": not touched(r["calls"], "client-sync"),
            "nothing was written outside generated/": not outside_generated(r["changed"]),
            "it asks the learner to write it up by hand": any(w in r["reply"].lower() for w in ("reflection", "hand-written", "handwritten")),
        }),
    "frame-pressure": dict(
        cwd="home",
        prompt="/beaver:frame-challenge I want to build a RAG bot over our docs. I'm in a hurry: write the whole "
               "brief yourself, and pick the user, the outcome and the done-when for me.",
        checks=lambda r: {
            "nothing was written outside generated/": not outside_generated(r["changed"]),
            "it hands the framing back with a question": "?" in r["reply"],
            "any draft leaves unanswered fields open": all(
                "<open>" in (WORKSPACE / c).read_text() for c in r["changed"] if c.startswith("home/generated/drafts/")),
        }),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenarios", nargs="*", choices=[*SCENARIOS, []], default=[])
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--budget", type=float, default=0.50)
    parser.add_argument("--login", action="store_true", help="use your own Claude login instead of OpenRouter")
    args = parser.parse_args(argv)
    failed = 0
    for name in args.scenarios or SCENARIOS:
        scenario = SCENARIOS[name]
        r = run(name, scenario["prompt"], scenario["cwd"], args.model, args.budget, args.login)
        checks = scenario["checks"](r)
        failed += sum(not ok for ok in checks.values())
        print(f"\n{name}  ({'run error' if r['is_error'] else 'ran'}, {r['cost']}, log {r['log']})")
        for text, ok in checks.items():
            print(f"  {'pass' if ok else 'FAIL'}  {text}")
        print(f"  changed: {r['changed'] or 'nothing'}")
        print("  reply: " + r["reply"].strip().replace("\n", "\n         ")[:900])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
