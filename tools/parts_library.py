"""Turn a submitted list of LEGO design numbers into a .parts library Sangala Blocks can import.

The format is the one specified in Documents\\Adding LEGO Blocks: a plain text file goes in, one part
to a line - the design number, then a quantity and a color if they are known - and a .parts file
comes out, JSON in the same shape as the .block file the application already writes.

    python tools/parts_library.py "Projects/Starter Set.txt"
    python tools/parts_library.py "Projects/Starter Set.txt" -o "Projects/Starter Set.parts"

EVERY FIELD BUT COLOR AND QUANTITY IS DERIVED FROM LDRAW, never from the submitted line. The number
is resolved through any redirection (3040 answers "~Moved to 3040b"), the name is the part file's
own first line, the footprint and height are measured, and the color is matched against
LDConfig.ldr. A line that cannot be resolved is REPORTED AND LEFT OUT, so a mistyped number shows up
as a line to correct rather than as a part that does not exist.

TWO MEASUREMENTS NEED CARE. A measured height includes the stud - a brick is 28 LDU, being 24 of
body and 4 of stud - and the application's own size table records the BODY, so the stud is subtracted
from anything that has one. And a part is stored under the number that was SUBMITTED, because that
is the number a builder orders by; the redirection matters only for reading the geometry.

Where the specification and this script differ, and the difference is deliberate: the document says
shape is classified from the geometry. It is classified here from the part's own description, which
is the library's own authority on what a part is and is far steadier than inferring roundness from
triangles. The measurements still come from the geometry.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ldparts

ROOT = ldparts.ROOT
PLATE_LDU = 8.0
STUD_LDU = 4.0


def colors():
    """name (lowercased) -> (canonical name, code), from the library's own palette file."""
    out = {}
    path = os.path.join(ROOT, "LDConfig.ldr")
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"0 !COLOUR\s+(\S+)\s+CODE\s+(\d+)", line.strip())
        if m:
            name = m.group(1).replace("_", " ")
            out[name.lower()] = (name, int(m.group(2)))
            # LDRAW SPELLS IT GREY; THIS PROJECT WRITES GRAY, and so does the application's own
            # palette. Both spellings are registered so that a submitted list in either is matched
            # rather than reported as an unknown color.
            if "grey" in name.lower():
                out[name.lower().replace("grey", "gray")] = (name, int(m.group(2)))
            elif "gray" in name.lower():
                out[name.lower().replace("gray", "grey")] = (name, int(m.group(2)))
    return out


def has_stud(path, seen=None):
    """Does anything in this part reference a stud primitive? Decides whether to subtract one."""
    seen = seen if seen is not None else set()
    key = os.path.basename(path).lower()
    if key in seen:
        return False
    seen.add(key)
    for line in open(path, encoding="utf-8", errors="replace"):
        t = line.strip()
        if not t.startswith("1 "):
            continue
        bits = t.split()
        if len(bits) < 15:
            continue
        ref = bits[14].replace("\\", "/").split("/")[-1].lower()
        if ref.startswith("stud"):
            return True
        sub = ldparts.locate(ref)
        if sub and has_stud(sub, seen):
            return True
    return False


def classify(name):
    """kind and shape, from the part's own description."""
    n = name.lower()
    if "inverted" in n and "slope" in n:
        return "invslope", "wedge"
    if "slope" in n:
        return "slope", "wedge"
    if "cone" in n:
        return "cone", "round"
    if "round" in n:
        return "round", "round"
    if n.startswith("tile"):
        return "tile", "box"
    if n.startswith("plate") or "wing" in n:
        return "plate", "box"
    if n.startswith("brick"):
        return "brick", "box"
    return "other", "box"


def read_list(path):
    """One part to a line: number[, qty][, color]. Blank lines and # comments are ignored."""
    rows = []
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        bits = [b.strip() for b in line.split(",")]
        qty, color = None, None
        for b in bits[1:]:
            if not b:
                continue
            if b.isdigit():
                qty = int(b)
            else:
                color = b
        rows.append((n, bits[0], qty, color))
    return rows


def build(rows):
    pal = colors()
    parts, problems = [], []
    for lineno, number, qty, color in rows:
        path, target, name = ldparts.resolve(number)
        if not path:
            problems.append("line %d: %s could not be resolved in the parts library" % (lineno, number))
            continue
        box = ldparts.bbox(path)
        if not box:
            problems.append("line %d: %s has no measurable geometry" % (lineno, number))
            continue
        minx, maxx, miny, maxy, minz, maxz = box
        w = round((maxx - minx) / ldparts.STUD)
        dd = round((maxz - minz) / ldparts.STUD)
        tall = maxy - miny
        if has_stud(path):
            tall -= STUD_LDU
        h = int(round(tall / PLATE_LDU))
        kind, shape = classify(name)
        part = {"id": number, "name": " ".join(name.split()), "kind": kind,
                "w": max(1, w), "d": max(1, dd), "h": max(1, h), "shape": shape}
        if target.lower() != number.lower():
            part["geometry"] = target        # the file the measurements came from, when redirected
        if color:
            hit = pal.get(color.lower().replace("_", " "))
            if hit:
                # The CODE is the authority; the name is stored in this project's spelling, since
                # every Sangala surface writes American and LDraw's file writes Grey.
                part["color"] = hit[0].replace("Grey", "Gray")
                part["colorCode"] = hit[1]
            else:
                problems.append("line %d: color %r is not in LDConfig.ldr, so it was left off" % (lineno, color))
        if qty is not None:
            part["qty"] = qty
        parts.append(part)
    return parts, problems


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__.strip().split("\n\n")[1])
    src = argv[1]
    out = argv[argv.index("-o") + 1] if "-o" in argv else os.path.splitext(src)[0] + ".parts"
    rows = read_list(src)
    parts, problems = build(rows)
    lib = {"sangala": "parts", "version": 1,
           "name": os.path.splitext(os.path.basename(src))[0], "parts": parts}
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lib, f, indent=1)
        f.write("\n")
    print("read %d lines, wrote %d parts to %s" % (len(rows), len(parts), out))
    for p in problems:
        print("  " + p)
    for p in parts:
        print("  %-6s %-38s %s  %d x %d studs, %d plate%s%s"
              % (p["id"], p["name"], p["kind"].ljust(9), p["w"], p["d"], p["h"],
                 "" if p["h"] == 1 else "s",
                 "  x%d %s" % (p.get("qty", 0), p.get("color", "")) if "qty" in p else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
