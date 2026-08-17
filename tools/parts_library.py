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

THREE MEASUREMENTS NEED CARE. A measured height includes the stud - a brick is 28 LDU, being 24 of
body and 4 of stud - and the application's own size table records the BODY, so the stud is subtracted
from anything that has one. A measured footprint is the whole bounding box, which for a slope is
neither the way it lies nor what it rests on - see `footprint`, which is the correction. And a part
is stored under the number that was SUBMITTED, because that is the number a builder orders by; the
redirection matters only for reading the geometry.

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


IDENT = ([[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]], [0.0, 0.0, 0.0])


def compose(outer, inner):
    """Put a sub-file's own placement into its parent's frame: outer applied to inner."""
    (a, t), (b, u) = outer, inner
    m = [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    p = [a[i][0] * u[0] + a[i][1] * u[1] + a[i][2] * u[2] + t[i] for i in range(3)]
    return (m, p)


def side_studs(path, w, xf=IDENT, depth=0, seen=(), out=None):
    """Where a part carries studs on a FACE rather than on top, in the plan view's own units.

    A SNOT brick's side studs are the whole reason it is in a design - the wings hang on them - and
    the standing view is a profile, so those studs point straight at the viewer and belong on the
    drawing. Nothing in a .parts entry said they existed, so 2434 arrived as a plain block and Glen
    had to open the 3D view to see what it was for (2026-08-17: "I see the studs on the side in the
    3D view but not in the 2d view").

    MEASURED, NOT READ OFF THE NAME. "with Studs on Sides" says nothing about how many or where, and
    the four SNOT parts in the crane's library carry 8, 4, 2 and 1 of them. An LDraw stud primitive
    is a cylinder along its own +Y, so a type-1 reference maps that axis to the matrix's middle
    column; where the image of +Y is horizontal rather than vertical, the stud is on a face. The
    matrix may also SCALE (stud4 arrives 11x tall), so it is the dominant direction that decides,
    never the length.

    Returned as [across, down] per stud: `across` in studs from the part's left edge, `down` in
    plates from the top of its body - the two units the plan view already draws in. The LDraw origin
    sits at the top of the body and centred across it, which is the same convention the height
    measurement above depends on. Both faces are read and the positions DEDUPED: seen in profile the
    near and far studs land on the same spot, and the drawing shows a stud, not a count.
    """
    out = [] if out is None else out
    key = os.path.normcase(path)
    if depth > 12 or key in seen:
        return out
    seen = seen + (key,)
    for line in open(path, encoding="utf-8", errors="replace"):
        t = line.split()
        if not t or t[0] != "1" or len(t) < 15:
            continue
        try:
            v = [float(x) for x in t[2:14]]
        except ValueError:
            continue
        here = compose(xf, ([[v[3], v[4], v[5]], [v[6], v[7], v[8]], [v[9], v[10], v[11]]],
                            [v[0], v[1], v[2]]))
        ref = " ".join(t[14:]).replace("\\", "/").split("/")[-1].lower()
        if ref.startswith("stud"):
            ax, ay, az = here[0][0][1], here[0][1][1], here[0][2][1]     # image of the stud's +Y
            if abs(ay) >= max(abs(ax), abs(az)):
                continue                                                 # up or down: an ordinary stud
            across = (here[1][0] + w * ldparts.STUD / 2) / ldparts.STUD
            down = here[1][1] / PLATE_LDU
            pos = [round(across, 3), round(down, 3)]
            if pos not in out:
                out.append(pos)
            continue
        sub = ldparts.locate(ref)
        if sub:
            side_studs(sub, w, here, depth + 1, seen, out)
    return out


def top_studs(path, box, w, d):
    """Where a part's studs actually sit on its top, WHEN THEY DO NOT FILL IT.

    Glen, 2026-08-17, looking at a 4 x 4 wedge on the plan: the drawing put a stud in every cell of
    the footprint, so a part with two studs came out with sixteen and the ones past the taper sat
    outside its own outline. 6069 has exactly TWO, side by side at the wide end - which is what the
    LDraw file says and what Jo's photograph of the part shows.

    Measured the same way the side studs are: an upward stud is a reference to a stud primitive whose
    axis is vertical. The tubes UNDERNEATH are stud primitives too (stud3, stud4), so the test is the
    top face - a stud on top sits at the part's own origin plane, which LDraw puts at the top of the
    body, while the tubes hang below it.

    Returned as [across, down] per stud in STUDS, from the part's left edge and from the end that the
    plan view draws first. Measured off the box rather than assumed centred: a wedge's origin is not
    in the middle of its length (6069 runs -70 to +10 in z), so centring would place every stud on
    the wrong row.

    Omitted entirely when the studs DO fill the footprint, which is the ordinary case - an ordinary
    brick says nothing here and is drawn exactly as it always was.
    """
    minx, maxx, miny, maxy, minz, maxz = box
    out = []
    for name, pos, axis in _walk_studs(path):
        ax, ay, az = axis
        if abs(ay) < max(abs(ax), abs(az)):
            continue                                   # on a face: that is side_studs' business
        if pos[1] > miny + STUD_LDU + 0.5:
            continue                                   # a tube below the top face, not a stud on it
        across = (pos[0] - minx) / ldparts.STUD
        down = (maxz - pos[2]) / ldparts.STUD
        p = [round(across, 3), round(down, 3)]
        if p not in out:
            out.append(p)
    return out if 0 < len(out) < w * d else []


def _walk_studs(path, xf=IDENT, depth=0, seen=(), out=None):
    """Every stud primitive in a part, with where it sits and which way its axis points."""
    out = [] if out is None else out
    key = os.path.normcase(path)
    if depth > 12 or key in seen:
        return out
    seen = seen + (key,)
    for line in open(path, encoding="utf-8", errors="replace"):
        t = line.split()
        if not t or t[0] != "1" or len(t) < 15:
            continue
        try:
            v = [float(x) for x in t[2:14]]
        except ValueError:
            continue
        here = compose(xf, ([[v[3], v[4], v[5]], [v[6], v[7], v[8]], [v[9], v[10], v[11]]],
                            [v[0], v[1], v[2]]))
        ref = " ".join(t[14:]).replace("\\", "/").split("/")[-1].lower()
        if ref.startswith("stud"):
            out.append((ref, here[1], (here[0][0][1], here[0][1][1], here[0][2][1])))
            continue
        sub = ldparts.locate(ref)
        if sub:
            _walk_studs(sub, here, depth + 1, seen, out)
    return out


def classify(name):
    """kind and shape, from the part's own description.

    THE SHAPE MUST BE SPOKEN IN THE PAGE'S OWN VOCABULARY, which is rect, slope, invslope, round,
    cone and wedge - the names its drawing and its 3D build switch on. This wrote box/wedge/round
    instead, three words borrowed from the specification document, and the page has no idea what they
    mean: a cone arrived as "round" and was built as a cylinder with a stud on top (Glen, 2026-08-15,
    looking at one: "I don't know what that is, but it is not a cone"), and a slope would have arrived
    as a wedge plate. A vocabulary that only one side understands is not a vocabulary.
    """
    n = name.lower()
    if "inverted" in n and "slope" in n:
        return "invslope", "invslope"
    if "slope" in n:
        return "slope", "slope"
    if "cone" in n:
        return "cone", "cone"
    if "round" in n:
        return "round", "round"
    if n.startswith("tile"):
        return "tile", "rect"
    if "wedge" in n or "wing" in n:
        return "wedge", "wedge"
    if n.startswith("plate"):
        return "plate", "rect"
    if n.startswith("brick"):
        return "brick", "rect"
    return "other", "rect"


def footprint(shape, w, dd):
    """The measured bounding box -> what the part RESTS ON, which is what a .parts file states.

    A BOUNDING BOX CANNOT TELL YOU WHAT A PART STANDS ON, and writing it as though it could is what
    put the crest a stud too deep: dragging a part out of the Library panel builds it straight from
    the w and d written here, so an inverted slope arrived two studs deep, hung off the back edge of
    the plate it was standing on, and looked perfect from the front because the error ran straight
    away from the camera. The Part menu was right all along - it reads the application's own size
    table, which states these footprints outright. This makes the file say the same thing.

    Two corrections, and both are measured facts about 45-degree slopes rather than conventions:
      - THE RAMP RUNS ALONG THE PART'S OWN Z, on every one of them (3040, 3039, 3037, 3665, 3660).
        The standing view is the figure in profile and needs that ramp ACROSS the screen, so the
        ramped side takes the COLUMNS and the other side becomes the rows. That is a straight swap.
      - AN INVERTED SLOPE RESTS ON LESS THAN IT COVERS. Its underside is cut away, so it attaches to
        one stud along the ramp and the rest of the body hangs over the next; the footprint is one
        column short of the body, and the application adds that column back as the overhang. An
        ordinary slope rests on all of itself and is not shortened - the two are opposites, which is
        why no single rule about "how many columns a slope takes" can ever be right.

    Checked against the application's own table, which was measured independently: 3040 -> 2 x 1,
    3039 -> 2 x 2, 3037 -> 2 x 4, 3665 -> 1 x 1, 3660 -> 1 x 2. All five agree.
    """
    if shape in ("slope", "invslope"):
        w, dd = dd, w
        if shape == "invslope":
            w = max(1, w - 1)
    return w, dd


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
        raw_w = w
        w, dd = footprint(shape, w, dd)
        part = {"id": number, "name": " ".join(name.split()), "kind": kind,
                "w": max(1, w), "d": max(1, dd), "h": max(1, h), "shape": shape}
        # Only where the footprint was left as it was measured. A slope's w and d are SWAPPED above
        # to turn the ramp across the screen, and a stud position measured in the part's own frame
        # would then be stated against the wrong edge - so a sloped SNOT part, if one is ever
        # ordered, says nothing rather than something misplaced.
        if shape == "rect":
            face = side_studs(path, raw_w)
            if face:
                part["side"] = face
        top = top_studs(path, box, part["w"], part["d"])
        if top:
            part["top"] = top
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
