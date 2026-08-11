"""Read the LDraw parts library and report what a part actually is.

Sangala Block Designer plans a LEGO kit, so every part it offers must carry a real
design number and a real footprint. Both are in the library sitting beside the
application - so they are READ, never typed from memory and never checked by hand.

    python tools/ldparts.py find "Wedge"          # search descriptions
    python tools/ldparts.py show 3005 3004 3023   # resolve, name and measure

What it knows about the format:
  * a part's FIRST line is its name:  "0 Brick  1 x  1"
  * a superseded number answers      "0 ~Moved to 3023b"  and must be followed
  * line type 1 is a sub-part reference: 1 <colour> x y z a b c d e f g h <file>
    with the 3x4 matrix in row-major order; line types 2-5 carry raw points
  * geometry is measured recursively through parts/, parts/s/, p/ and p/48/
  * 1 LDU = 0.4 mm, stud pitch 20 LDU, plate 8 LDU, brick 24 LDU; +Y is DOWN,
    so a part's own origin sits at the TOP of its body
"""
import os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LDraw", "ldraw")
SEARCH = ["parts", "p", os.path.join("parts", "s"), os.path.join("p", "48")]
LDU_MM, STUD, PLATE = 0.4, 20.0, 8.0


def locate(name):
    name = name.replace("\\", "/").split("/")[-1].lower()
    if not name.endswith(".dat"):
        name += ".dat"
    for d in SEARCH:
        p = os.path.join(ROOT, d, name)
        if os.path.exists(p):
            return p
    return None


def first_line(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("0 "):
                return line[2:].strip()
            if line:
                return ""
    return ""


def resolve(number, seen=None):
    """Follow ~Moved to / ~Renamed redirects to the file that holds the geometry."""
    seen = seen or set()
    path = locate(number)
    if not path or number.lower() in seen:
        return path, number, first_line(path) if path else ""
    seen.add(number.lower())
    desc = first_line(path)
    low = desc.lower()
    if low.startswith("~moved to") or low.startswith("~renamed to"):
        target = desc.split()[-1]
        return resolve(target, seen)
    return path, number, desc


def bbox(path, depth=0, seen=None):
    """Bounding box in LDU as (minx,maxx,miny,maxy,minz,maxz), or None."""
    seen = seen or set()
    key = os.path.normcase(path)
    if depth > 12 or key in seen:
        return None
    seen = seen | {key}
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3

    def take(x, y, z):
        for i, v in enumerate((x, y, z)):
            if v < lo[i]:
                lo[i] = v
            if v > hi[i]:
                hi[i] = v

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            t = line.split()
            if not t:
                continue
            if t[0] == "1" and len(t) >= 15:
                try:
                    v = [float(x) for x in t[2:14]]
                except ValueError:
                    continue
                sub = locate(" ".join(t[14:]))
                if not sub:
                    continue
                b = bbox(sub, depth + 1, seen)
                if not b:
                    continue
                x, y, z = v[0], v[1], v[2]
                m = v[3:]
                for cx in (b[0], b[1]):
                    for cy in (b[2], b[3]):
                        for cz in (b[4], b[5]):
                            take(x + m[0] * cx + m[1] * cy + m[2] * cz,
                                 y + m[3] * cx + m[4] * cy + m[5] * cz,
                                 z + m[6] * cx + m[7] * cy + m[8] * cz)
            elif t[0] in ("2", "3", "4", "5"):
                n = {"2": 2, "3": 3, "4": 4, "5": 4}[t[0]]
                try:
                    v = [float(x) for x in t[2:2 + 3 * n]]
                except ValueError:
                    continue
                for i in range(n):
                    take(v[3 * i], v[3 * i + 1], v[3 * i + 2])
    if lo[0] == float("inf"):
        return None
    return (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def show(numbers):
    print("%-9s %-10s %-38s %-14s %s" % ("asked", "geometry", "name", "studs (w x d)", "height"))
    for n in numbers:
        path, resolved, desc = resolve(n)
        if not path:
            print("%-9s %-10s NOT IN LIBRARY" % (n, "-"))
            continue
        got = os.path.basename(path)[:-4]
        b = bbox(path)
        if not b:
            print("%-9s %-10s %-38s %s" % (n, got, desc[:38], "no geometry"))
            continue
        w, d = (b[1] - b[0]) / STUD, (b[5] - b[4]) / STUD
        h = (b[3] - b[2]) / PLATE
        print("%-9s %-10s %-38s %-14s %.2f plates (%.1f mm)"
              % (n, got, desc[:38], "%.2f x %.2f" % (w, d), h, (b[3] - b[2]) * LDU_MM))


def find(term, limit=25):
    d = os.path.join(ROOT, "parts")
    hits = 0
    for name in sorted(os.listdir(d)):
        if not name.endswith(".dat"):
            continue
        desc = first_line(os.path.join(d, name))
        if term.lower() in desc.lower() and not desc.startswith("~"):
            print("  %-10s %s" % (name[:-4], desc))
            hits += 1
            if hits >= limit:
                print("  ... (more)")
                return


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
    elif sys.argv[1] == "find":
        find(" ".join(sys.argv[2:]))
    else:
        show(sys.argv[2:])
