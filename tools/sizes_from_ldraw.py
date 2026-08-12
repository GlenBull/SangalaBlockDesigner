"""Build the rows x columns -> design number table from the LDraw library.

A student should be able to ask for the brick they actually want - 2 x 3 is the commonest
brick there is - rather than pick from a short list somebody typed. That only works if the
design number can be LOOKED UP, which is what the library beside this application is for.

    python tools/sizes_from_ldraw.py            # rewrite the SIZES table in the application
    python tools/sizes_from_ldraw.py --print    # just show what it found

Only EXACT descriptions count: "Brick  2 x  3" yes, "Brick  2 x  3 with Holes" no, and a
"~Moved to" stub never. Where several files describe the same size, the shortest plain part
number wins (3002 over 3002p01), which is the one a person orders by.
"""
import os, re, io, sys, json

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LDraw", "ldraw")
APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "SangalaBlockDesigner.html")
KINDS = {"brick": "Brick", "plate": "Plate"}
PAT = re.compile(r"^(Brick|Plate)\s+(\d+)\s+x\s+(\d+)$")

# THE INVENTORY IS NOT THE CATALOGUE (Glen, 2026-08-11): "if it is rare and our students will
# never see it, let's not include it in our inventory." The library holds everything LEGO ever
# moulded - a 10 x 10 brick (733, first issued 1999) is a real brick and measures like one, but
# no student will have it. So the table is filtered to the sizes that are in an ordinary brick
# set, given as pairs (smaller, larger) and matched either way round.
# PROVISIONAL: replace this with the kit inventory once the list of what actually goes in the box
# is settled - the same list for Uganda and Virginia, so a design built at one site can be built
# at the other.
KEEP = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 6), (1, 8),
        (2, 2), (2, 3), (2, 4), (2, 6), (2, 8)}


def first_line(path):
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if s.startswith("0 "):
                return s[2:].strip()
            if s:
                return ""
    return ""


def scan():
    found = {k: {} for k in KINDS}
    d = os.path.join(ROOT, "parts")
    for name in sorted(os.listdir(d)):
        if not name.endswith(".dat"):
            continue
        stem = name[:-4]
        # 3002 yes, and 3023b too - a trailing letter is LDraw's own variant suffix, and the
        # number a person orders by is the digits (3023). Without this, Plate 1x2 vanishes from
        # the table, because plain 3023 is a "~Moved to 3023b" stub. Patterned parts (3002p01)
        # and unofficial ones (u9033) are not sizes and stay out.
        m0 = re.match(r"^(\d+)[a-z]?$", stem)
        if not m0:
            continue
        num = m0.group(1)
        m = PAT.match(first_line(os.path.join(d, name)))
        if not m:
            continue
        word, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        if (min(a, b), max(a, b)) not in KEEP:
            continue
        kind = "brick" if word == "Brick" else "plate"
        key = "%dx%d" % (a, b)
        prev = found[kind].get(key)
        if prev is None or (len(num), num) < (len(prev), prev):
            found[kind][key] = num
    return found


def main():
    found = scan()
    for k in found:
        print("%s: %d sizes" % (k, len(found[k])))
        row = sorted(found[k].items(), key=lambda kv: [int(n) for n in kv[0].split("x")])
        print("   " + ", ".join("%s=%s" % kv for kv in row[:14]) + (" ..." if len(row) > 14 else ""))
    if "--print" in sys.argv:
        return
    js = "const SIZES = " + json.dumps(found, separators=(",", ":"), sort_keys=True) + ";"
    src = io.open(APP, encoding="utf-8").read()
    new, n = re.subn(r"(?m)^const SIZES = .*?;$", js, src, count=1)
    if n != 1:
        raise SystemExit("could not find the SIZES table to replace - add a placeholder line first")
    io.open(APP, "w", encoding="utf-8", newline="\n").write(new)
    print("written into", os.path.basename(APP))


if __name__ == "__main__":
    main()
