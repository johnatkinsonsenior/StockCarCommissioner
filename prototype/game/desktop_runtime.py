"""Find or fetch a desktop runtime so Windows can double-click to play.

The office needs Python 3.10+ and Godot 4.4. Testers should not have to
hunt for either. This module installs both under tools/ on first launch
and skips the Microsoft Store python.exe stub that looks installed but
cannot run a script.
"""

from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen

GODOT_VERSION = "4.4-stable"
GODOT_WIN_EXE = "Godot_v4.4-stable_win64.exe"
GODOT_WIN_ZIP_URL = (
    "https://github.com/godotengine/godot/releases/download/"
    "4.4-stable/Godot_v4.4-stable_win64.exe.zip"
)
PYTHON_EMBED_VERSION = "3.12.10"
PYTHON_EMBED_URL = (
    "https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
)


def project_root(start=None):
    """Return the repository / unpacked-zip root."""

    if start is not None:
        return Path(start)
    return Path(__file__).resolve().parent.parent.parent


def tools_dir(root=None):
    """Return tools/ next to the launchers (not inside the zip forever)."""

    return project_root(root) / "tools"


def bundled_godot_dir(root=None):
    return tools_dir(root) / "godot"


def bundled_python_dir(root=None):
    return tools_dir(root) / "python"


def is_windows_apps_alias(path):
    """Return True for the Microsoft Store python.exe stub.

    That stub is on PATH as python, opens the Store, and makes a
    double-clicked .bat flash closed. It is not a real interpreter.
    """

    text = str(path or "").replace("/", "\\").lower()
    return "windowsapps" in text


def _godot_looks_runnable(path):
    if path is None:
        return False
    path = Path(path)
    if not path.is_file():
        return False
    name = path.name.lower()
    if "godot" not in name:
        return False
    if sys.platform.startswith("win") or name.endswith(".exe"):
        return True
    return os.access(path, os.X_OK)


def bundled_godot_candidates(root=None):
    """Return Godot binaries previously downloaded into tools/godot."""

    folder = bundled_godot_dir(root)
    rows = [
        folder / GODOT_WIN_EXE,
        folder / "Godot_v4.4.1-stable_win64.exe",
        folder / "Godot.exe",
        folder / "godot.exe",
        folder / "Godot_v4.4-stable_linux.x86_64",
        folder / "godot",
    ]
    if folder.is_dir():
        try:
            rows.extend(sorted(folder.glob("Godot*")))
            rows.extend(sorted(folder.glob("godot*")))
        except OSError:
            pass
    return rows


def fetch_url(url, dest, fetch=None):
    """Download url to dest. fetch(url) -> bytes is injectable for tests."""

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if fetch is None:
        with urlopen(url, timeout=120) as handle:
            data = handle.read()
    else:
        data = fetch(url)
    dest.write_bytes(data)
    return dest


def extract_zip(archive, dest_dir):
    """Extract a zip into dest_dir and return extracted paths."""

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    written = []
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(dest_dir)
        written = [dest_dir / name for name in bundle.namelist()]
    return written


def first_godot_in(folder):
    """Return the first Godot binary under folder, or None."""

    folder = Path(folder)
    if not folder.is_dir():
        return None
    preferred = [
        folder / GODOT_WIN_EXE,
        folder / "Godot_v4.4-stable_linux.x86_64",
    ]
    for path in preferred:
        if _godot_looks_runnable(path):
            return path
    try:
        matches = sorted(folder.rglob("*"))
    except OSError:
        matches = []
    for path in matches:
        if path.is_file() and "godot" in path.name.lower() and _godot_looks_runnable(path):
            return path
    return None


def enable_embedded_python(python_dir):
    """Turn on import site so PYTHONPATH works in the embeddable runtime."""

    python_dir = Path(python_dir)
    updated = []
    for path in sorted(python_dir.glob("python*._pth")):
        text = path.read_text(encoding="utf-8")
        text = text.replace("#import site", "import site")
        if "import site" not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += "import site\n"
        path.write_text(text, encoding="utf-8")
        updated.append(path)
    return updated


def should_download_godot():
    """Windows downloads Godot on first play. Linux only if asked."""

    if os.environ.get("SCC_SKIP_GODOT_DOWNLOAD"):
        return False
    if sys.platform.startswith("win"):
        return True
    return os.environ.get("SCC_DOWNLOAD_GODOT") == "1"


def install_godot(root=None, fetch=None, url=None):
    """Download Godot 4.4 into tools/godot. Return the binary path."""

    root = project_root(root)
    folder = bundled_godot_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    url = url or GODOT_WIN_ZIP_URL
    archive = folder / "godot-download.zip"
    print("Downloading Godot 4.4 into tools/godot (one time)...")
    fetch_url(url, archive, fetch=fetch)
    extract_zip(archive, folder)
    try:
        archive.unlink()
    except OSError:
        pass
    binary = first_godot_in(folder)
    if binary is None:
        raise FileNotFoundError("Godot zip extracted but no editor binary was inside.")
    return binary


def ensure_godot_binary(root=None, download=None, fetch=None, finder=None):
    """Return a Godot binary, downloading on Windows if needed."""

    if finder is not None:
        found = finder()
        if found:
            return Path(found)
    for candidate in bundled_godot_candidates(root):
        if _godot_looks_runnable(candidate):
            return candidate
    if download is None:
        download = should_download_godot()
    if not download:
        return None
    return install_godot(root=root, fetch=fetch)
