#!/usr/bin/env python3
"""Package the playable-alpha career-mode build for playtesters."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from game.packaging import package_playable_alpha


def main():
    destination = sys.argv[1] if len(sys.argv) > 1 else None
    result = package_playable_alpha(destination=destination)
    print("Stock Car Commissioner %s" % result["version"])
    print("Save schema %s" % result["save_version"])
    print("Zip: %s" % result["zip_path"])
    print("Files: %s" % result["file_count"])
    print("Size: %s bytes" % result["size_bytes"])
    print("Play the career loop with ./play.sh after unpacking.")
    return result


if __name__ == "__main__":
    main()
