"""Godot UI prototype helpers: snapshot JSON and engine launch."""

import json
import os
import shutil
import subprocess
from pathlib import Path

UI_VERSION = "0.1"
GODOT_MAJOR = 4


def project_root():
    """Return the repository root (parent of prototype/)."""

    return Path(__file__).resolve().parent.parent.parent


def godot_project_dir():
    """Return the Godot 4 project folder."""

    return project_root() / "godot"


def default_snapshot_path():
    """Return the snapshot file the Godot project reads at runtime."""

    return godot_project_dir() / "data" / "ui_snapshot.json"


def compose_ui_snapshot(payload):
    """Build the JSON document the Godot prototype renders."""

    payload = payload or {}
    dashboard = payload.get("dashboard") or {}
    settings = payload.get("settings") or {}
    menu_items = payload.get("menu_items") or []
    return {
        "game": "Stock Car Commissioner",
        "ui_version": UI_VERSION,
        "engine": "godot-4",
        "screen": payload.get("screen") or "menu",
        "series": payload.get("series") or "Stock Car Series",
        "settings_line": payload.get("settings_line") or "",
        "calendar": payload.get("calendar") or "",
        "menu_items": list(menu_items),
        "settings": {
            "difficulty": settings.get("difficulty") or "normal",
            "difficulty_label": settings.get("difficulty_label") or "Normal",
            "career_seasons": settings.get("career_seasons") or 3,
            "autosave": settings.get("autosave") or "off",
            "autosave_label": settings.get("autosave_label") or "Off",
        },
        "dashboard": dashboard,
        "decision": payload.get("decision"),
    }


def write_ui_snapshot_file(snapshot, path=None):
    """Write a UI snapshot JSON file for Godot to load."""

    path = Path(path) if path else default_snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=4)
    return path


def find_godot_binary():
    """Return a Godot 4 editor binary if one is on disk or PATH."""

    env_bin = os.environ.get("GODOT_BIN")
    candidates = []
    if env_bin:
        candidates.append(Path(env_bin))
    for name in ("godot", "godot4", "Godot_v4.4-stable_linux.x86_64"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    candidates.extend(
        [
            Path("/tmp/godot-engine/Godot_v4.4-stable_linux.x86_64"),
            Path("/usr/local/bin/godot"),
            Path("/usr/bin/godot"),
        ]
    )
    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def launch_godot_process(snapshot_path=None, headless=None, extra_args=None):
    """Spawn Godot against the UI project. Returns a result dict."""

    binary = find_godot_binary()
    project = godot_project_dir()
    if headless is None:
        headless = not (
            os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        )
    result = {
        "binary": str(binary) if binary else None,
        "project": str(project),
        "snapshot": str(snapshot_path) if snapshot_path else None,
        "headless": bool(headless),
        "returncode": None,
        "output": "",
    }
    if binary is None:
        result["output"] = (
            "Godot 4 was not found. Install Godot 4.4+ and open godot/project.godot, "
            "or set GODOT_BIN."
        )
        return result
    command = [str(binary), "--path", str(project)]
    if headless:
        command.extend(["--headless", "--quit-after", "3"])
    if extra_args:
        command.extend(list(extra_args))
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    result["returncode"] = completed.returncode
    result["output"] = (completed.stdout or "") + (completed.stderr or "")
    return result
