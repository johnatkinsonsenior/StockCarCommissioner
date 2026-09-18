#!/usr/bin/env python3
"""Tests for the Windows one-click desktop runtime."""

import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from game.desktop_runtime import (
    GODOT_WIN_EXE,
    bundled_godot_candidates,
    enable_embedded_python,
    ensure_godot_binary,
    extract_zip,
    first_godot_in,
    is_windows_apps_alias,
    install_godot,
    tools_dir,
)


def _fail(errors, cond, message):
    if not cond:
        errors.append(message)


def test_store_stub(errors):
    _fail(
        errors,
        is_windows_apps_alias(
            r"C:\Users\Pat\AppData\Local\Microsoft\WindowsApps\python.exe"
        ),
        "WindowsApps python.exe should be treated as a stub",
    )
    _fail(
        errors,
        is_windows_apps_alias(
            "C:/Users/Pat/AppData/Local/Microsoft/WindowsApps/python.exe"
        ),
        "forward-slash WindowsApps path should still be a stub",
    )
    _fail(
        errors,
        not is_windows_apps_alias(r"C:\Python312\python.exe"),
        "real python.exe should not look like a stub",
    )
    _fail(
        errors,
        not is_windows_apps_alias(""),
        "blank path is not a stub",
    )


def test_extract_and_ensure(errors, tmp):
    fake_exe = GODOT_WIN_EXE
    archive = tmp / "godot.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr(fake_exe, b"fake-godot")
    folder = tmp / "godot"
    extract_zip(archive, folder)
    found = first_godot_in(folder)
    _fail(errors, found is not None, "extracted zip should contain a Godot binary")
    _fail(
        errors,
        found.name == fake_exe,
        "preferred Godot exe name should win, got %s" % (found,),
    )

    def fetch(_url):
        return archive.read_bytes()

    binary = install_godot(root=tmp, fetch=fetch, url="http://example.test/godot.zip")
    _fail(errors, binary is not None, "install_godot should return a binary")
    _fail(errors, binary.is_file(), "installed Godot should exist on disk")
    again = ensure_godot_binary(root=tmp, download=False)
    _fail(errors, again is not None, "ensure should find the bundled copy without download")
    names = [path.name for path in bundled_godot_candidates(tmp)]
    _fail(errors, fake_exe in names, "bundled candidates should list the win64 editor")


def test_embed_pth(errors, tmp):
    python_dir = tmp / "python"
    python_dir.mkdir()
    pth = python_dir / "python312._pth"
    pth.write_text("python312.zip\n.\n#import site\n", encoding="utf-8")
    updated = enable_embedded_python(python_dir)
    text = pth.read_text(encoding="utf-8")
    _fail(errors, updated == [pth], "should rewrite the embed ._pth")
    _fail(errors, "import site" in text, "import site must be enabled")
    _fail(errors, "#import site" not in text, "commented import site must be gone")


def test_tools_dir(errors, tmp):
    _fail(
        errors,
        tools_dir(tmp) == tmp / "tools",
        "tools/ lives next to the launchers",
    )


def main():
    import tempfile

    errors = []
    test_store_stub(errors)
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        test_extract_and_ensure(errors, tmp)
        test_embed_pth(errors, tmp)
        test_tools_dir(errors, tmp)
    if errors:
        print("LAUNCHER_OK=0")
        for item in errors:
            print("LAUNCHER_ERROR=%s" % item)
        return 1
    print("LAUNCHER_OK=1")
    print("STUB_SKIP=1")
    print("GODOT_EXTRACT=1")
    print("EMBED_SITE=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
