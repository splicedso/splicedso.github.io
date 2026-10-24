"""Every internal link on every built page points at something that exists.

    python check_links.py

Relative links are resolved from the page's own directory, root-relative ones from the site
root. External links, anchors and mailto are skipped.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SKIP = ("http://", "https://", "mailto:", "#", "javascript:", "data:")


def target(page, href):
    href = href.split("#")[0].split("?")[0]
    path = (HERE / href.lstrip("/")) if href.startswith("/") else (page.parent / href)
    path = path.resolve()
    return path / "index.html" if path.is_dir() or href.endswith("/") else path


def main():
    pages = [p for p in HERE.rglob("*.html") if not any(part in (".git", "src", "render", "brand") for part in p.relative_to(HERE).parts)]
    broken = []
    for page in pages:
        for href in re.findall(r'(?:href|src)="([^"]+)"', page.read_text()):
            if href.startswith(SKIP) or "{{" in href:
                continue
            if not target(page, href).exists():
                broken.append(f"{page.relative_to(HERE)} -> {href}")
    print(f"{len(pages)} pages checked, {len(broken)} broken links")
    for b in broken:
        print("  " + b)
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
