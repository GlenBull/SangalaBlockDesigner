r"""List the LDraw files that must SHIP with Sangala Blocks, for git to add.

The repository carried every primitive but only 39 part files, so a collaborator's copy could
draw the curated menu and nothing else - a curved bow came back empty and the application fell
back to a stand-in shape. This writes the list of files that have to travel: every part the
application can represent, plus the transitive closure of everything those parts reference.

    python tools\ship_parts.py > parts-to-ship.txt
    git add -f --pathspec-from-file=parts-to-ship.txt

Re-run it whenever the application learns to represent a new family of parts; the set is
derived, never hand-extended.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from designnum import resolve

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = os.path.join(ROOT, "LDraw", "ldraw")
SEARCH = ["parts", os.path.join("parts", "s"), "p", os.path.join("p", "48"),
          os.path.join("p", "8")]
REF = re.compile(r"^\s*1\s+\S+(?:\s+\S+){12}\s+(\S+)", re.M)


def locate(name):
    for d in SEARCH:
        p = os.path.join(BASE, d, *name.split("/"))
        if os.path.exists(p):
            return p
    return None


def main():
    top = [f[:-4] for f in os.listdir(os.path.join(BASE, "parts"))
           if f.lower().endswith(".dat")]
    keep = [d for d in top if "error" not in resolve(d)]

    seen, queue, paths = set(), [d + ".dat" for d in keep], []
    while queue:
        key = queue.pop().replace("\\", "/").lower()
        if key in seen:
            continue
        path = locate(key)
        if path is None:
            continue                      # a reference this library does not carry
        seen.add(key)
        paths.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        with io.open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        for sub in REF.findall(text):
            if sub.lower().endswith(".dat"):
                queue.append(sub)

    sys.stderr.write("parts represented: %d    files to ship: %d\n" % (len(keep), len(paths)))
    for p in sorted(paths):
        print(p)


if __name__ == "__main__":
    main()
