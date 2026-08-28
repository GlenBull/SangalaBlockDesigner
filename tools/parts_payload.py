r"""Measure what it costs to SHIP the parts a student actually needs.

The repository carries every LDraw primitive (p/) but only 39 part files, so a collaborator's
copy can draw the 39 curated parts and nothing else. This works out the real payload: every
part the application can represent, plus the transitive closure of the sub-parts and
primitives those parts reference, and what that weighs on disk and compressed.

    python tools\parts_payload.py
"""
import os
import re
import sys
import time
import zipfile
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from designnum import resolve

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "LDraw", "ldraw")
SEARCH = ["parts", os.path.join("parts", "s"), "p", os.path.join("p", "48"),
          os.path.join("p", "8")]
REF = re.compile(r"^\s*1\s+\S+(?:\s+\S+){12}\s+(\S+)", re.M)


def locate(name):
    name = name.replace("\\", "/").lower()
    for d in SEARCH:
        p = os.path.join(BASE, d, *name.split("/"))
        if os.path.exists(p):
            return p
    return None


def main():
    t0 = time.time()
    top = [f[:-4] for f in os.listdir(os.path.join(BASE, "parts"))
           if f.lower().endswith(".dat")]
    keep = [d for d in top if "error" not in resolve(d)]
    print("parts the application can represent : %d of %d" % (len(keep), len(top)))

    # walk every reference, so nothing a part depends on is left behind
    need, queue = set(), [d + ".dat" for d in keep]
    while queue:
        name = queue.pop()
        key = name.replace("\\", "/").lower()
        if key in need:
            continue
        path = locate(key)
        if path is None:
            continue
        need.add(key)
        with io.open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        for sub in REF.findall(text):
            if sub.lower().endswith(".dat"):
                queue.append(sub)

    total = 0
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for key in sorted(need):
            path = locate(key)
            if not path:
                continue
            total += os.path.getsize(path)
            z.write(path, key)

    print("files needed, closure included     : %d" % len(need))
    print("on disk                            : %.1f MB" % (total / 1048576.0))
    print("as a zip                           : %.1f MB" % (len(buf.getvalue()) / 1048576.0))
    print("measured in                        : %.1f seconds" % (time.time() - t0))


if __name__ == "__main__":
    main()
