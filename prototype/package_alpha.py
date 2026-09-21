#!/usr/bin/env python3
"""Package the playable-alpha career-mode build for playtesters."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from game.packaging import package_playable_alpha


def main():
    destination = None
    include_windows_runtime = False
    for arg in sys.argv[1:]:
        if arg in ("--windows-runtime", "--windows"):
            include_windows_runtime = True
        elif arg in ("-h", "--help"):
            print(
                "Usage: package_alpha.py [destination.zip] [--windows-runtime]\n"
                "  --windows-runtime  bundle Python 3.12 and Godot 4.4 for offline Windows play"
            )
            return 0
        elif not arg.startswith("-"):
            destination = arg
    result = package_playable_alpha(
        destination=destination,
        include_windows_runtime=include_windows_runtime,
    )
    print("Stock Car Commissioner %s" % result["version"])
    print("Save schema %s" % result["save_version"])
    print("Zip: %s" % result["zip_path"])
    print("Files: %s" % result["file_count"])
    print("Size: %s bytes" % result["size_bytes"])
    if result.get("windows_runtime"):
        print("Windows runtime: bundled (Python 3.12 + Godot 4.4)")
    print("Windows: double-click StockCarCommissioner.exe after unpacking.")
    print("Mac/Linux: ./play_ui.sh  |  Known issues: KNOWN_ISSUES.md")
    return result


if __name__ == "__main__":
    main()
