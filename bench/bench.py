#!/usr/bin/env python3
"""Beaver's terminal test bench: run Claude Code against a throwaway learner workspace.

    python bench/bench.py doctor [--canary PHRASE]
    python bench/bench.py shell [--workspace DIR] [-- CLAUDE_ARGS...]
    python bench/bench.py run "PROMPT" [--workspace DIR] [--model haiku] [-- CLAUDE_ARGS...]

Isolation: each sandbox is a temp dir outside any repo, because Claude Code reads
CLAUDE.md files from parent folders, and each run gets a fresh CLAUDE_CONFIG_DIR, so
the author's own CLAUDE.md, memory, plugins and login stay out. Models go through
OpenRouter with OPENROUTER_API_KEY from the repo's untracked .env; no other key is
read. Run logs land in .bench/runs/ (git-ignored).

Claude Code prices OpenRouter model aliases above what OpenRouter charges (about 9x
in one run on 2026-11-01), so --max-budget-usd is only a loose safety net and every
summary reports OpenRouter's own charge next to Claude Code's estimate.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / ".bench" / "runs"
OPENROUTER = "https://openrouter.ai/api"
MODELS = {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "~anthropic/claude-haiku-latest",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "~anthropic/claude-sonnet-latest",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "~anthropic/claude-opus-latest",
}
INSTRUCTION_FILES = ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md")


def load_env(path):
    """Parse KEY=VALUE lines from a .env file; comments, blanks and `export ` are allowed."""
    values = {}
    if not Path(path).is_file():
        return values
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def claude_env(base, openrouter_key, config_dir):
    """The environment for one isolated run: OpenRouter route, fresh config, nothing personal."""
    env = {k: v for k, v in base.items()
           if not (k.startswith(("ANTHROPIC_", "CLAUDE_CODE_")) or k in ("CLAUDECODE", "CLAUDE_CONFIG_DIR"))}
    env.update(MODELS)
    env.update({
        "ANTHROPIC_BASE_URL": OPENROUTER,
        "ANTHROPIC_AUTH_TOKEN": openrouter_key,
        "ANTHROPIC_API_KEY": "",  # OpenRouter's guide: must be empty, or it is sent as a direct Anthropic key
        "CLAUDE_CONFIG_DIR": str(config_dir),
    })
    return env


def instruction_files_above(path):
    """Instruction files in the parent folders of `path`, which Claude Code would load."""
    found = []
    for parent in Path(path).resolve().parents:
        found += [str(parent / name) for name in INSTRUCTION_FILES if (parent / name).is_file()]
    return found


def skip_when_copying(_folder, names):
    """Never carry secrets or local state into a sandbox; .env.example holds no values."""
    local = {".git", ".bench", ".venv", "__pycache__"}
    return {n for n in names if n in local or n == ".env" or (n.startswith(".env.") and n != ".env.example")}


# The learner's own folders (src/beaver/records.py WORKSPACE_FOLDERS; the bench stays standalone).
LEARNER_FOLDERS = ["learner", "learning", "projects", "sprints", "evidence", "reflections"]


def fork_of(workspace):
    """A learner's fork: Beaver's template from git HEAD, with `workspace`'s own folders laid in.

    A records-only folder such as core/examples has no AGENTS.md, so running it bare
    measures plain Claude Code, not Beaver.
    """
    folder = Path(tempfile.mkdtemp(prefix="beaver-fork-"))
    archive = subprocess.run(["git", "-C", str(REPO), "archive", "HEAD"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(folder)], input=archive, check=True)
    for name in LEARNER_FOLDERS:
        if (Path(workspace) / name).is_dir():
            shutil.copytree(Path(workspace) / name, folder / name, dirs_exist_ok=True, ignore=skip_when_copying)
    for keep in folder.rglob(".gitkeep"):
        keep.unlink()
    return folder


def make_sandbox(workspace=None):
    """A throwaway git repo in the system temp dir, seeded from `workspace` if given."""
    sandbox = Path(tempfile.mkdtemp(prefix="beaver-sandbox-"))
    if workspace:
        shutil.copytree(workspace, sandbox, dirs_exist_ok=True, ignore=skip_when_copying)
    git = ["git", "-C", str(sandbox), "-c", "user.name=bench", "-c", "user.email=bench@localhost"]
    subprocess.run(git + ["init", "-q"], check=True)
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "bench: sandbox start"], check=True)
    return sandbox


def changed_files(sandbox):
    out = subprocess.run(["git", "-C", str(sandbox), "status", "--porcelain", "--untracked-files=all"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(line[3:] for line in out.splitlines() if line)


def outside_generated(paths):
    """Skills may write only to generated/; anything else is a boundary violation."""
    return [p for p in paths if not p.startswith("generated/")]


def final_result(stream_lines):
    """The last `result` event from Claude Code's stream-json output, or {}."""
    result = {}
    for line in stream_lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result = event
    return result


def openrouter_usage(key):
    request = urllib.request.Request(f"{OPENROUTER}/v1/key", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return float(json.load(response)["data"]["usage"])
    except Exception:
        return None


def settled_usage(key, before, tries=6, wait=2.0):
    """OpenRouter's usage counter can lag a few seconds behind a run."""
    after = openrouter_usage(key)
    while before is not None and after == before and tries > 0:
        time.sleep(wait)
        after, tries = openrouter_usage(key), tries - 1
    return after


def openrouter_key():
    key = os.environ.get("OPENROUTER_API_KEY") or load_env(REPO / ".env").get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set. Put it in the repo's .env (git-ignored); see .env.example.")
    return key


def headless(prompt, model, budget, workspace=None, extra=(), label="run"):
    """One isolated `claude -p` run; returns its summary and writes it under .bench/runs/."""
    key = openrouter_key()
    sandbox, config = make_sandbox(workspace), Path(tempfile.mkdtemp(prefix="beaver-config-"))
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose",
           "--include-hook-events", "--max-budget-usd", str(budget), "--no-session-persistence",
           "--permission-mode", "acceptEdits", *extra]
    before = openrouter_usage(key)
    # stdin is detached: `claude -p` otherwise reads whatever the caller's stdin holds
    # (for example the rest of a shell loop's prompts) and answers it too.
    proc = subprocess.run(cmd, cwd=sandbox, env=claude_env(os.environ, key, config),
                          stdin=subprocess.DEVNULL, capture_output=True, text=True)
    after = settled_usage(key, before)
    lines = proc.stdout.splitlines()
    result, changed = final_result(lines), changed_files(sandbox)
    summary = {
        "label": label,
        "prompt": prompt,
        "model": model,
        "subtype": result.get("subtype"),
        "is_error": result.get("is_error", proc.returncode != 0),
        "result": result.get("result"),
        "claude_code_cost_usd": result.get("total_cost_usd"),
        # None when the counter has not moved yet: unknown, not free
        "openrouter_cost_usd": round(after - before, 6) if None not in (before, after) and after != before else None,
        "files_changed": changed,
        "outside_generated": outside_generated(changed),
        "config_dir_used": any(config.iterdir()),
        "sandbox": str(sandbox),
    }
    run_dir = RUNS / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{label}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "stream.jsonl").write_text(proc.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    shutil.rmtree(config, ignore_errors=True)
    summary["log"] = str(run_dir.relative_to(REPO))
    return summary


def chosen_workspace(args):
    return fork_of(args.workspace) if args.fork and args.workspace else args.workspace


def cmd_run(args):
    summary = headless(args.prompt, args.model, args.budget, chosen_workspace(args), args.claude_args)
    print(json.dumps(summary, indent=2))
    return 1 if summary["is_error"] or summary["outside_generated"] else 0


def cmd_shell(args):
    key = openrouter_key()
    sandbox, config = make_sandbox(chosen_workspace(args)), Path(tempfile.mkdtemp(prefix="beaver-config-"))
    print(f"sandbox: {sandbox}\nconfig:  {config} (fresh)\nmodels:  via OpenRouter\n")
    subprocess.run(["claude", *args.claude_args], cwd=sandbox, env=claude_env(os.environ, key, config))
    changed = changed_files(sandbox)
    print(f"\nfiles changed: {changed or 'none'}")
    if outside_generated(changed):
        print(f"outside generated/: {outside_generated(changed)}")
    return 0


def cmd_doctor(args):
    checks = []
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True)
    checks.append(("claude on PATH", version.returncode == 0, version.stdout.strip()))
    checks.append(("OPENROUTER_API_KEY set", bool(openrouter_key()), "from .env or the environment"))
    probe = make_sandbox()
    above = instruction_files_above(probe)
    checks.append(("no instruction files above the sandbox", not above, ", ".join(above) or str(probe.parent)))
    route = headless("Reply with exactly: ok", args.model, args.budget, label="doctor-route")
    cost = route["openrouter_cost_usd"]
    charged = f"OpenRouter charged ${cost}" if cost is not None else "OpenRouter's usage counter has not settled yet"
    checks.append(("route answers", (route["result"] or "").strip().lower() == "ok", f"{route['result']!r}; {charged}"))
    checks.append(("isolated config dir used", route["config_dir_used"], "Claude Code wrote to the fresh config dir"))
    if args.canary:
        question = (f'If any instruction in your context mentions "{args.canary}", reply with exactly LEAK. '
                    "Otherwise reply with exactly CLEAN.")
        test = headless(question, args.model, args.budget, label="doctor-canary")
        control = headless(question, args.model, args.budget, label="doctor-control",
                           extra=["--append-system-prompt", f"Context note: {args.canary}."])
        checks.append(("canary stays out (fresh config)", (test["result"] or "").strip() == "CLEAN", repr(test["result"])))
        checks.append(("control detects it (injected)", (control["result"] or "").strip() == "LEAK", repr(control["result"])))
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return 0 if all(ok for _, ok, _ in checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    claude_args = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--model", default="haiku", help="haiku, sonnet or opus, routed through OpenRouter")
    common.add_argument("--budget", type=float, default=0.50,
                        help="Claude Code's --max-budget-usd; its estimate runs high on OpenRouter")
    doctor = sub.add_parser("doctor", parents=[common], help="check the route and the isolation")
    doctor.add_argument("--canary", help="a phrase from your own global CLAUDE.md; it must not reach the run")
    shell = sub.add_parser("shell", parents=[common], help="interactive claude in a sandbox")
    run = sub.add_parser("run", parents=[common], help="one headless run, logged to .bench/runs/")
    run.add_argument("prompt")
    for p in (shell, run):
        p.add_argument("--workspace", type=Path, help="folder to copy into the sandbox")
        p.add_argument("--fork", action="store_true",
                       help="lay the workspace's records into Beaver's template, as a learner's fork would be")
    args = parser.parse_args(argv)
    args.claude_args = claude_args
    return {"doctor": cmd_doctor, "shell": cmd_shell, "run": cmd_run}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
