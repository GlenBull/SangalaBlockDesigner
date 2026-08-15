"""Work out the smallest LDraw library that can draw everything Sangala Blocks offers, and track it.

The full library is 24,591 part files and half a gigabyte - reference data that is rightly
git-ignored. But the snapshot feature cannot ship without SOME library beside it, so this walks
every part number the application can place, follows each "~Moved to" redirect and every sub-file
reference down through parts/, parts/s/, p/ and p/48/, and tracks exactly that closure: about 150
files and well under a megabyte.

    python tools/bundle_parts.py           # report what the closure is
    python tools/bundle_parts.py --track   # and `git add -f` it, since LDraw/ is ignored

THE PART NUMBERS ARE READ OUT OF THE PAGE, never listed here. A number typed into this file is one
that stops matching the day a part is added to the menu, and the failure is silent: the brick simply
does not appear in the render.
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(REPO, "SangalaBlockDesigner.html")
ROOT = os.path.join(REPO, "LDraw", "ldraw")
SEARCH = ["parts", "p", os.path.join("parts", "s"), os.path.join("p", "48")]

# Not parts, but the library cannot be used without them: LDConfig.ldr is where the color codes the
# page writes (15 White, 71 Light Bluish Gray...) are actually defined, and the two CA files are the
# library's own license and readme, which travel with any copy of it.
EXTRAS = ["LDConfig.ldr", "CAlicense.txt", "CAreadme.txt", "Readme.txt"]

# THE PARTS CAN BE PRUNED; THE PRIMITIVES CANNOT. A walk of the references finds every part a design
# can name, and that pruning is worth it - 39 files against 24,591. It does NOT find the primitives
# LDView substitutes as it draws: the logo-bearing stud that puts LEGO on every stud top, and the
# 48-segment versions of the curves. Nothing in the library refers to either, so two attempts at
# guessing which ones to add both produced a render that looked right and was not - the studs alone
# differed, 13,080 pixels of them, against the full library. Shipping every primitive ends the guess:
# measured identical, and 9.6 MB is a small price for a render that cannot silently drift.
# `--verify` is what proved it and is the gate if this is ever narrowed again.
SHIP_ALL_PRIMITIVES = True


def part_ids():
    src = open(HTML, encoding="utf-8").read()
    ids = set()
    kinds = re.search(r"const KINDS = \{.*?\n\};", src, re.S)
    sizes = re.search(r"const SIZES = \{.*?\};", src, re.S)
    for block in (kinds, sizes):
        if not block:
            continue
        for m in re.finditer(r'"(\d{3,6}[a-z]?)"', block.group(0)):
            ids.add(m.group(1))
        for m in re.finditer(r'id:"(\d{3,6}[a-z]?)"', block.group(0)):
            ids.add(m.group(1))
    return sorted(ids)


def locate(name):
    name = name.replace("\\", "/").split("/")[-1].lower()
    if not name.endswith(".dat"):
        name += ".dat"
    for d in SEARCH:
        p = os.path.join(ROOT, d, name)
        if os.path.exists(p):
            return p
    return None


def closure(ids):
    seen, missing = {}, []

    def walk(name):
        # Key on the FILE, not on the spelling. A model names a part as "3023b" and a sub-file
        # reference names it "3023b.dat"; keying on the raw string counted one file twice and
        # reported a closure seven files larger than it is.
        key = name.replace("\\", "/").split("/")[-1].lower()
        if not key.endswith(".dat"):
            key += ".dat"
        if key in seen:
            return
        path = locate(name)
        if not path:
            if name not in missing:
                missing.append(name)
            return
        seen[key] = path
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                t = line.strip()
                if t.startswith("0 ~Moved to "):
                    walk(t.split()[3])
                elif t.startswith("1 "):
                    bits = t.split()
                    if len(bits) >= 15:
                        walk(bits[14])

    for i in ids:
        walk(i)
    return seen, missing


def verify(subset_root):
    """Render the same model against the subset and against the full library, and compare pixels.

    The only trustworthy test of "is this enough": geometry that is missing does not raise an error,
    it just is not drawn. Needs LDView beside the program and the full library still on disk.
    """
    import hashlib
    import tempfile
    try:
        import fitz
    except ImportError:
        print("verify needs pymupdf (python -m pip install pymupdf)")
        return 1
    ldview = os.path.join(REPO, "LDView", "LDView64.exe")
    model = os.path.join(REPO, "Projects", "test.ldr")
    if not (os.path.isfile(ldview) and os.path.isfile(model)):
        print("verify needs LDView\\LDView64.exe and Projects\\test.ldr")
        return 1
    out = []
    for label, root in (("subset", subset_root), ("full", ROOT)):
        png = os.path.join(tempfile.gettempdir(), "bundle_verify_%s.png" % label)
        if os.path.exists(png):
            os.remove(png)
        subprocess.run([ldview, model, "-LDrawDir=" + root, "-SaveSnapshot=" + png,
                        "-SaveWidth=1000", "-SaveHeight=800", "-SaveAlpha=1", "-AutoCrop=1",
                        "-ShowEdges=1", "-ConditionalHighlights=1", "-SaveActualSize=0", "-cg30,45"],
                       check=False)
        if not os.path.exists(png):
            print("%s: LDView produced no image" % label)
            return 1
        out.append(hashlib.sha1(fitz.Pixmap(png).samples).hexdigest())
    same = out[0] == out[1]
    print("subset render: %s" % out[0][:16])
    print("full render:   %s" % out[1][:16])
    print("IDENTICAL" if same else "DIFFERENT - the subset is missing something LDView draws")
    return 0 if same else 1


def main(argv):
    if "--verify" in argv:
        i = argv.index("--verify")
        root = argv[i + 1] if len(argv) > i + 1 else ROOT
        return verify(root)
    ids = part_ids()
    files, missing = closure(ids)
    # only the PARTS come from the closure; every primitive ships (see SHIP_ALL_PRIMITIVES above)
    parts = sorted(p for p in files.values()
                   if os.sep + "parts" + os.sep in p + os.sep)
    prims = []
    for root, _dirs, names in os.walk(os.path.join(ROOT, "p")):
        prims += [os.path.join(root, n) for n in names]
    paths = parts + sorted(prims)
    for e in EXTRAS:
        p = os.path.join(ROOT, e)
        if os.path.exists(p):
            paths.append(p)
    size = sum(os.path.getsize(p) for p in paths)
    print("part numbers in the page: %d" % len(ids))
    print("parts needed to draw them: %d  (the library holds 24,591)" % len(parts))
    print("primitives, all of them:   %d" % len(prims))
    print("plus library files:        %s" % ", ".join(EXTRAS))
    print("total:                     %d files, %.1f MB" % (len(paths), size / 1048576.0))
    if missing:
        print("NOT FOUND (the render would silently drop these): %s" % ", ".join(missing))
        return 1
    if "--track" in argv:
        rel = [os.path.relpath(p, REPO).replace("\\", "/") for p in paths]
        # -f because LDraw/ is ignored: the full library stays untracked, this subset does not.
        for i in range(0, len(rel), 200):
            subprocess.run(["git", "-C", REPO, "add", "-f"] + rel[i:i + 200], check=True)
        print("tracked %d files with git add -f" % len(rel))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
