"""Check every part on the Full Parts List against the geometry in its own LDraw file.

Sangala Blocks works a part's footprint out from the WORDS of its declared name (dnParse in
SangalaBlockDesigner.html), while both views draw the part from its real mesh (ldrFlatten). Where
those two disagree a student gets a part that is the wrong size, or one that lies the wrong way
round on the grid. This reads the same files the application reads, does the same two things, and
prints where they differ.

    python check_parts.py            every part on the spreadsheet
    python check_parts.py 50950      just these numbers
"""
import os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LDRAW = os.path.join(ROOT, "LDraw", "ldraw")
SHEET = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making"
         r"\Sangala Tools\Sangala Blocks Files\Documents\Full Parts List.xlsx")

# The application's own family table, transcribed from SangalaBlockDesigner.html
DN_FAMILIES = [
    (r"^Baseplate\b", "other", "rect", 1),
    (r"^Plate\b.*\bRound\b", "round", "round", 1),
    (r"^Plate\b", "plate", "rect", 1),
    (r"^Tile\b", "tile", "rect", 1),
    (r"^Slope Brick\b.*\bInverted\b", "invslope", "invslope", 3),
    (r"^Slope Brick\b", "slope", "slope", 3),
    (r"^Wedge\b", "wedge", "wedge", 3),
    (r"^Cone\b", "cone", "cone", 3),
    (r"^Brick\b.*\bRound\b", "round", "round", 3),
    (r"^Brick\b", "brick", "rect", 3),
]


def dn_parse(name):
    """dnParse, line for line: the fields a .library entry gets from the declared name."""
    fam = None
    for f in DN_FAMILIES:
        if re.search(f[0], name, re.I):
            fam = f
            break
    if not fam:
        return None
    m = re.search(r"\b(\d+)\s*x\s*(\d+)(?:\s*x\s*(\d+(?:\.\d+)?))?", name, re.I)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    slope = fam[1] in ("slope", "invslope")
    w = a if slope else b
    d = b if slope else a
    h = max(1, round(3 * float(m.group(3)))) if m.group(3) else fam[3]
    return {"kind": fam[1], "shape": fam[2], "w": w, "d": d, "h": h}


# Reading the LDraw files, the way ldrRead does
_found = {}


def find(name):
    key = name.strip().replace("\\", "/").lower()
    if key in _found:
        return _found[key]
    hit = None
    for base in ("parts", "p", "models"):
        p = os.path.join(LDRAW, base, *key.split("/"))
        if os.path.isfile(p):
            hit = p
            break
    _found[key] = hit
    return hit


def read(name):
    p = find(name)
    if not p:
        return None
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def declared(pid):
    """The declared name, following a ~Moved to redirect, exactly as dnName does."""
    for _ in range(5):
        t = read(pid + ".dat")
        if t is None:
            return None, pid, "no file"
        first = (t.split("\n")[0] or "").strip()
        nm = (first[1:] if first[:1] == "0" else first).strip()
        mv = re.match(r"^~Moved to (\S+)", nm)
        if not mv:
            return re.sub(r"\s+", " ", nm).strip(), pid, None
        pid = mv.group(1)
    return None, pid, "redirects too many times"


def mul(M, S):
    r = [0.0] * 12
    for i in range(3):
        for j in range(3):
            r[i * 3 + j] = M[i * 3] * S[j] + M[i * 3 + 1] * S[3 + j] + M[i * 3 + 2] * S[6 + j]
        r[9 + i] = M[i * 3] * S[9] + M[i * 3 + 1] * S[10] + M[i * 3 + 2] * S[11] + M[9 + i]
    return r


def at(M, p):
    return (M[0] * p[0] + M[1] * p[1] + M[2] * p[2] + M[9],
            M[3] * p[0] + M[4] * p[1] + M[5] * p[2] + M[10],
            M[6] * p[0] + M[7] * p[1] + M[8] * p[2] + M[11])


IDENT = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]


def walk(name, M, box, depth, budget):
    """Fold every TRIANGLE into box. Line types 3 and 4 only, as LeoCAD and ldrFlatten both do:
    edges must not decide how big a part is."""
    if depth > 24 or budget[0] <= 0:
        return
    t = read(name)
    if t is None:
        return
    for line in t.split("\n"):
        f = line.strip().split()
        if len(f) < 2:
            continue
        if f[0] == "1" and len(f) >= 15:
            try:
                v = [float(x) for x in f[2:14]]
            except ValueError:
                continue
            S = [v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[0], v[1], v[2]]
            walk(" ".join(f[14:]), mul(M, S), box, depth + 1, budget)
        elif f[0] in ("3", "4"):
            n = 3 if f[0] == "3" else 4
            if len(f) < 2 + 3 * n:
                continue
            budget[0] -= 1
            for k in range(n):
                try:
                    p = [float(x) for x in f[2 + 3 * k:5 + 3 * k]]
                except ValueError:
                    continue
                q = at(M, p)
                for i in range(3):
                    if q[i] < box[i]:
                        box[i] = q[i]
                    if q[i] > box[3 + i]:
                        box[3 + i] = q[i]


def measure(pid):
    box = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9]
    walk(pid + ".dat", IDENT, box, 0, [400000])
    if box[0] > box[3]:
        return None
    return box


def studs(v):
    return round(v / 20.0, 2)


def plates(v):
    return round(v / 8.0, 2)


def sheet_parts():
    z = zipfile.ZipFile(SHEET)
    ss = z.read("xl/sharedStrings.xml").decode("utf-8")
    strs = ["".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))
            for si in re.findall(r"<si>(.*?)</si>", ss, re.S)]
    sh = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    out = []
    for rm in re.finditer(r'<row r="(\d+)"(.*?)</row>', sh, re.S):
        cells = {}
        for c in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', rm.group(2), re.S):
            vm = re.search(r"<v>(.*?)</v>", c.group(3) or "", re.S)
            val = vm.group(1) if vm else ""
            if 't="s"' in c.group(2) and val.isdigit():
                val = strs[int(val)]
            cells[c.group(1)] = val
        a, b = cells.get("A", "").strip(), cells.get("B", "").strip()
        if a and b and a != "Part":
            out.append((a, b))
    return out


ROW = "%-9s %-35s %-10s %-12s %-9s %s"


def main():
    parts = [(None, x) for x in sys.argv[1:]] if len(sys.argv) > 1 else sheet_parts()
    print(ROW % ("Number", "Declared name in the LDraw file", "From name", "Measured",
                 "Kind", "Verdict"))
    print("-" * 116)
    tally = {}

    def count(k):
        tally[k] = tally.get(k, 0) + 1

    for listed, pid in parts:
        name, real, err = declared(pid)
        if err:
            print(ROW % (pid, (listed or "")[:35], "", "", "", "MISSING - " + err))
            count("MISSING")
            continue
        p = dn_parse(name)
        box = measure(real)
        shown = pid if real == pid else pid + "->" + real
        if box is None:
            print(ROW % (shown, name[:35],
                         "%dx%dx%d" % (p["w"], p["d"], p["h"]) if p else "-",
                         "no triangles", p["kind"] if p else "-", "NO GEOMETRY"))
            count("NO GEOMETRY")
            continue
        wLD, dLD = studs(box[3] - box[0]), studs(box[5] - box[2])
        hLD = plates(max(box[4], 0.0))      # the studs fold onto the top face, as silOf does
        meas = "%gx%gx%g" % (wLD, dLD, hLD)
        if not p:
            print(ROW % (shown, name[:35], "no shape", meas, "-", "NOT OFFERED"))
            count("NOT OFFERED")
            continue
        rw, rd, rh = round(wLD), round(dLD), round(hLD)
        notes = []
        if sorted((rw, rd)) != sorted((p["w"], p["d"])):
            notes.append("FOOTPRINT")
        elif (rw, rd) != (p["w"], p["d"]) and rw != rd:
            notes.append("turned")
        if rh != p["h"]:
            notes.append("HEIGHT")
        if p["kind"] == "slope":
            pairs = re.findall(r"\d+\s*x\s*\d+", name)
            ramp = int(re.match(r"\d+", pairs[-1]).group(0)) if pairs else 2
            if ramp != p["w"]:
                notes.append("RAMP")
        print(ROW % (shown, name[:35], "%dx%dx%d" % (p["w"], p["d"], p["h"]),
                     meas, p["kind"], " + ".join(notes) if notes else "ok"))
        for n in (notes or ["ok"]):
            count(n)
    print("-" * 116)
    print("%d parts.  " % len(parts) + ",  ".join("%s %d" % (k, v) for k, v in sorted(tally.items())))



if __name__ == "__main__":
    main()
