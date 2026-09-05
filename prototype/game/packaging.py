"""Build a playable-alpha zip for career-mode playtesting."""

import json
import os
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path

GAME_NAME = "Stock Car Commissioner"
GAME_VERSION = "0.1.0-alpha"
SAVE_SCHEMA_VERSION = "0.0.39"
PACKAGE_SLUG = "stock-car-commissioner"
UI_ENGINE = "godot-4.4"

INCLUDE_PATHS = (
    "prototype",
    "godot",
    "docs",
    "ROADMAP.md",
    "README.md",
    "PLAYTEST.md",
    "VERSION",
    "play.sh",
    "play_ui.sh",
)

REQUIRED_PATHS = (
    "prototype/run_season.py",
    "prototype/package_alpha.py",
    "play.sh",
    "play_ui.sh",
    "PLAYTEST.md",
    "VERSION",
    "README.md",
)

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".godot",
    "saves",
    ".venv",
    "dist",
    ".cursor",
}

SKIP_FILE_NAMES = {
    ".DS_Store",
    ".gitignore",
}

SKIP_SUFFIXES = {".pyc", ".pyo", ".zip"}

EXECUTABLE_NAMES = {
    "play.sh",
    "play_ui.sh",
    "package_alpha.py",
    "run_season.py",
    "run_ui.py",
}


def project_root():
    """Return the repository root (parent of prototype/)."""

    return Path(__file__).resolve().parent.parent.parent


def package_prefix(version=None):
    """Return the top-level folder name inside the zip."""

    return "%s-%s" % (PACKAGE_SLUG, version or GAME_VERSION)


def default_zip_path(root=None, version=None):
    """Return dist/<slug>-<version>.zip under the project root."""

    root = Path(root) if root else project_root()
    name = "%s.zip" % package_prefix(version)
    return root / "dist" / name


def read_game_version(root=None):
    """Read VERSION from disk, falling back to the packaged constant."""

    path = (Path(root) if root else project_root()) / "VERSION"
    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text
    return GAME_VERSION


def _should_skip_file(path):
    if path.name in SKIP_FILE_NAMES:
        return True
    if path.suffix in SKIP_SUFFIXES:
        return True
    if path.parent.name == "season_reports" and path.suffix == ".json":
        return True
    return False


def iter_package_files(root=None):
    """Yield (absolute path, archive-relative path) pairs for the alpha zip."""

    root = Path(root) if root else project_root()
    seen = set()
    for rel in INCLUDE_PATHS:
        src = root / rel
        if not src.exists():
            continue
        if src.is_file():
            if _should_skip_file(src):
                continue
            arc = Path(rel).as_posix()
            if arc not in seen:
                seen.add(arc)
                yield src, arc
            continue
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = sorted(
                name for name in dirnames if name not in SKIP_DIR_NAMES
            )
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if _should_skip_file(path):
                    continue
                arc = path.relative_to(root).as_posix()
                if arc in seen:
                    continue
                seen.add(arc)
                yield path, arc


def resolve_zip_path(destination=None, root=None, version=None):
    """Return the zip path for an optional destination file or folder."""

    root = Path(root) if root else project_root()
    if destination is None:
        return default_zip_path(root, version)
    dest = Path(destination)
    if dest.suffix.lower() == ".zip":
        return dest
    return dest / ("%s.zip" % package_prefix(version))


def _unix_file_mode(path):
    mode = stat.S_IFREG | 0o644
    if path.name in EXECUTABLE_NAMES or os.access(path, os.X_OK):
        mode = stat.S_IFREG | 0o755
    return mode


def _zipinfo(arcname, mode, date_time=None):
    info = zipfile.ZipInfo(arcname)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = mode << 16
    info.create_system = 3
    if date_time is not None:
        info.date_time = date_time
    return info


def build_manifest(root=None, file_count=0, version=None):
    """Describe the packaged playable-alpha build."""

    version = version or read_game_version(root)
    return {
        "game": GAME_NAME,
        "version": version,
        "save_schema": SAVE_SCHEMA_VERSION,
        "packaged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": "3.10+",
        "career_loop": "./play.sh",
        "optional_ui": "./play_ui.sh",
        "ui_engine": UI_ENGINE,
        "file_count": file_count,
        "notes": (
            "The Python career loop is the playable alpha. "
            "Godot 4.4 is an optional UI prototype and is not required."
        ),
    }


def package_playable_alpha(destination=None, root=None):
    """Copy the career-mode tree into a playtester zip under dist/."""

    root = Path(root) if root else project_root()
    version = read_game_version(root)
    missing = [
        rel for rel in REQUIRED_PATHS if not (root / rel).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Cannot package playable alpha; missing: %s" % ", ".join(missing)
        )

    files = list(iter_package_files(root))
    zip_path = resolve_zip_path(destination, root, version)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()

    prefix = package_prefix(version)
    stamped = datetime.now().timetuple()[:6]
    manifest = build_manifest(root, file_count=len(files) + 1, version=version)

    with zipfile.ZipFile(zip_path, "w") as archive:
        for src, arc in files:
            info = _zipinfo(
                "%s/%s" % (prefix, arc),
                _unix_file_mode(src),
                stamped,
            )
            with src.open("rb") as handle:
                archive.writestr(info, handle.read())
        manifest_info = _zipinfo(
            "%s/MANIFEST.json" % prefix,
            stat.S_IFREG | 0o644,
            stamped,
        )
        archive.writestr(
            manifest_info,
            json.dumps(manifest, indent=4) + "\n",
        )

    return {
        "game": GAME_NAME,
        "version": version,
        "save_version": SAVE_SCHEMA_VERSION,
        "zip_path": str(zip_path),
        "prefix": prefix,
        "file_count": len(files) + 1,
        "size_bytes": zip_path.stat().st_size,
        "included": [arc for _src, arc in files] + ["MANIFEST.json"],
    }
