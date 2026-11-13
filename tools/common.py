"""Shared helpers for the "يعني إيه" pipeline."""
import json
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BUILD = Path(os.environ.get("YAANY_BUILD", ROOT / "build"))
# YAANY_CACHE = persistent folder outside the git checkout (used by the self-hosted runner)
_CACHE = Path(os.environ["YAANY_CACHE"]) if os.environ.get("YAANY_CACHE") else ROOT
SFX_DIR = _CACHE / "sfx"
LIB_DIR = _CACHE / "library"


def load_env():
    """Minimal .env loader (no extra dependency)."""
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def need_env(name):
    val = os.environ.get(name, "").strip()
    if not val:
        sys.exit(f"[x] Missing {name}. Put it in .env or export it.")
    return val


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def series():
    return load_yaml(ROOT / "config" / "series.yaml")


def episode(path):
    ep = load_yaml(path)
    ep["_path"] = str(Path(path).resolve())
    return ep


def ep_dir(ep):
    d = BUILD / ep["id"]
    for sub in ("assets", "voice", "text"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def color(cfg, name_or_hex):
    """'gold' -> series color, '#ff0000' -> as is."""
    if name_or_hex.startswith("#"):
        return name_or_hex
    return cfg["colors"][name_or_hex]
