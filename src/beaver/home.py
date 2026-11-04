"""Find the learner's Beaver home: the one workspace every client reads.

Order, first match wins:
1. an explicit path (`beaver --home PATH`) or the BEAVER_HOME environment variable
2. the nearest folder at or above the current one that holds a beaver.yaml
3. the home remembered in ~/.config/beaver/config.yaml (XDG_CONFIG_HOME respected),
   so `beaver` works from inside a child project repo too
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

MARKER = "beaver.yaml"


@dataclass(frozen=True)
class Home:
    path: Path
    found_by: str  # "explicit" | "BEAVER_HOME" | "current folder" | "config"


def config_path(env=None):
    env = os.environ if env is None else env
    base = Path(env["XDG_CONFIG_HOME"]) if env.get("XDG_CONFIG_HOME") else Path.home() / ".config"
    return base / "beaver" / "config.yaml"


def is_workspace(path):
    return (Path(path) / MARKER).is_file()


def resolve_home(explicit=None, start=None, env=None):
    """The learner's home, or None when nothing points to one."""
    env = os.environ if env is None else env
    if explicit:
        return Home(Path(explicit).expanduser().resolve(), "explicit")
    if env.get("BEAVER_HOME"):
        return Home(Path(env["BEAVER_HOME"]).expanduser().resolve(), "BEAVER_HOME")
    here = Path(start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if is_workspace(folder):
            return Home(folder, "current folder")
    config = config_path(env)
    if config.is_file():
        remembered = (yaml.safe_load(config.read_text(encoding="utf-8")) or {}).get("home")
        if remembered:
            return Home(Path(remembered).expanduser().resolve(), "config")
    return None


def remember_home(path, env=None):
    """Record `path` as the learner's home in the config file; returns the config path."""
    path = Path(path).expanduser().resolve()
    if not is_workspace(path):
        raise ValueError(f"{path} is not a Beaver workspace (no {MARKER})")
    config = config_path(env)
    config.parent.mkdir(parents=True, exist_ok=True)
    data = (yaml.safe_load(config.read_text(encoding="utf-8")) or {}) if config.is_file() else {}
    data["home"] = str(path)
    config.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return config
