#!/usr/bin/env python3
"""Turn on import site for a Windows embeddable Python folder."""

import sys
from pathlib import Path


def main():
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    count = 0
    for path in sorted(folder.glob("python*._pth")):
        text = path.read_text(encoding="utf-8")
        text = text.replace("#import site", "import site")
        if "import site" not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += "import site\n"
        path.write_text(text, encoding="utf-8")
        count += 1
    print("EMBED_SITE=%s" % count)
    return 0 if count else 1


if __name__ == "__main__":
    sys.exit(main())
