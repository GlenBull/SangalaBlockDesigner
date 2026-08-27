r"""Resolve a LEGO Design Number to a Sangala Blocks library part.

Reads the LDraw parts library bundled beside the application (LDraw\ldraw\parts),
takes the part's declared name from the first line of its .dat file, and parses
that name into the fields a .library entry needs: kind, w, d, h, shape.

Offline. No network, no account, no key. Run:  python designnum.py 3001 3020 4477
"""
import io, os, re, sys, json

LDRAW = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "LDraw", "ldraw", "parts")

# Height is carried in PLATE units, the way the .library files already do it:
# a plate is 1, a brick is 3. A trailing "x N" in the name overrides it, in bricks.
KINDS = [
    (r"^Baseplate\b",            "other",    "rect",     1),
    (r"^Plate\b.*\bRound\b",     "round",    "round",    1),
    (r"^Plate\b",                "plate",    "rect",     1),
    (r"^Tile\b",                 "plate",    "rect",     1),
    (r"^Slope Brick\b.*\bInverted\b", "invslope", "invslope", 3),
    (r"^Slope Brick\b",          "slope",    "slope",    3),
    (r"^Wedge\b",                "wedge",    "wedge",    3),
    (r"^Cone\b",                 "cone",     "cone",     3),
    (r"^Brick\b.*\bRound\b",     "round",    "round",    3),
    (r"^Brick\b",                "brick",    "rect",     3),
]

def _dat(design):
    """First line of the part file, following any ~Moved to redirect."""
    for _ in range(5):
        p = os.path.join(LDRAW, design + ".dat")
        if not os.path.exists(p):
            return None, design
        with io.open(p, encoding="utf-8", errors="replace") as f:
            line = f.readline().strip()
        name = line[1:].strip() if line.startswith("0") else line
        m = re.match(r"~Moved to (\S+)", name)
        if not m:
            return name, design
        design = m.group(1)          # follow the redirect and try again
    return None, design

def resolve(design):
    """-> a dict ready to drop into a .library, or a dict with 'error'."""
    name, actual = _dat(design)
    if name is None:
        return {"id": design, "error": "no such design number in the LDraw library"}
    tidy = re.sub(r"\s+", " ", name).strip()

    kind = shape = None
    h = 3
    for pat, k, s, dh in KINDS:
        if re.match(pat, tidy, re.I):
            kind, shape, h = k, s, dh
            break
    if kind is None:
        return {"id": design, "name": tidy,
                "error": "name does not start with a family this parser knows"}

    nums = re.search(r"\b(\d+)\s*x\s*(\d+)(?:\s*x\s*(\d+(?:\.\d+)?))?", tidy, re.I)
    if not nums:
        return {"id": design, "name": tidy,
                "error": "no 'A x B' stud dimensions in the name"}
    a, b = int(nums.group(1)), int(nums.group(2))
    # Name order differs by family. "Plate 2 x 12" is depth 2, width 12; but a
    # slope's first number is its RUN, which the .library files store as width.
    if kind in ("slope", "invslope"):
        w, d = a, b
    else:
        d, w = a, b
    if nums.group(3):
        # Fractional on purpose: LDraw writes a two-plate slope as "x 0.667" of a brick,
        # so 3x the value is the height in PLATES. The leading digit alone gave zero.
        h = max(1, int(round(3 * float(nums.group(3)))))

    out = {"id": design, "name": tidy, "kind": kind,
           "w": w, "d": d, "h": h, "shape": shape}
    if actual != design:
        out["moved_to"] = actual     # the number LEGO now uses for this mould
    return out

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(json.dumps(resolve(arg), ensure_ascii=False))
