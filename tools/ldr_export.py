"""Turn a Sangala Blocks design into an LDraw model, and render it the way LEGO documentation looks.

    python tools/ldr_export.py "Projects/Crane (head).block"            # writes the .ldr beside it
    python tools/ldr_export.py "Projects/Crane (head).block" --render   # and renders a PNG

WHY THIS EXISTS. Glen, 2026-08-14: the build snapshots must be "comparable in quality to that found
in the official LEGO documentation" - not a capture of this application's own 3D view. That look
comes from an LDraw renderer, so the design is written as an LDraw model and LDView draws it: flat
brick colors with black edge lines, and no gray background.

THE COLORS COME THROUGH FOR FREE. The application's palette already carries LDraw color codes
(15 White, 71 Light Bluish Gray, 0 Black, 14 Yellow, 4 Red...), so a brick's `color` field is written
straight into the model with no mapping table.

THE UNITS, which are the part worth getting right:
  * 1 LDU = 0.4 mm. A stud is 20 LDU, a plate 8 LDU, a brick 24 LDU (three plates).
  * The application counts in studs across and plates up, on the same 8 mm pitch, so the conversion
    is exact: one Blocks stud = 20 LDU, one Blocks plate = 8 LDU.
  * LDraw's +Y points DOWN. Height above the plate is therefore NEGATIVE y.
  * A part's origin sits at the TOP of its body, not the bottom - so a brick whose base is at height
    b and whose body is h plates tall has its origin at -(b + h) plates.
  * A part's origin is also at the CENTER of its footprint in x and z, so a w x d part placed at
    column c, row r sits at the middle of the cells it covers.

Both facts about the origin were established on 2026-08-06 and got written down precisely because
they are the ones that look plausible when wrong.
"""
import json
import os
import subprocess
import sys

LDU_PER_STUD = 20.0
LDU_PER_PLATE = 8.0
LDVIEW = os.path.join(os.path.expanduser("~"), "UVa Lab School Dropbox", "AI Sandbox",
                      "Design through Making", "_Drafts", "Working", "LDView", "LDView64.exe")
LDRAWDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LDraw", "ldraw")


def to_ldr(design):
    """One line-type-1 per brick: colour, a 3x4 matrix, and the part file.

    THE TWO WAYS OF BUILDING NEED DIFFERENT ARITHMETIC, and mixing them up is the mistake that looks
    plausible until the picture is rendered:

      RELIEF  - the design is seen face on. `col` is across and `row` is DEPTH, both in studs; `base`
                is how many plates the piece stands proud. So row feeds Z and base feeds height.
      STANDING - the design is seen from the side. `col` is across in studs, and `row` is a vertical
                COURSE counted in plates from the top of the page downward. So row feeds height and
                there is no depth: everything sits in one layer.

    Screen rows increase downward while LDraw height increases upward, so a standing row is measured
    from the foot of the page. The page is the 32 x 32 stud baseplate unless the file says otherwise,
    which is 80 plates tall.
    """
    mode = design.get("mode", "standing")
    # The page, in the application's own numbers, so "parked" here means what it means on screen.
    page_mm = {"baseplate": (256.0, 256.0), "letter": (215.9, 279.4), "square12": (304.8, 304.8)}
    pw, ph = page_mm.get(design.get("pageSize") or "baseplate", (256.0, 256.0))
    plate_cols = round(pw / 8.0)
    plate_rows = round(ph / (8.0 if mode == "relief" else 3.2))
    out = ["0 " + design.get("name", "Sangala Blocks design"),
           "0 Name: sangala.ldr",
           "0 Author: Sangala Blocks",
           "0 !LDRAW_ORG Unofficial_Model",
           "0 // built in %s mode" % mode,
           ""]
    skipped = 0
    for b in design.get("bricks", []):
        w, d = float(b.get("w", 1)), float(b.get("d", 1))
        h = float(b.get("h", 1))                       # the part's own height, in plates
        col, row = float(b.get("col", 0)), float(b.get("row", 0))
        # A brick parked on the cork beside the plate is a candidate the builder is trying for fit,
        # not part of the design - the application leaves it out of the parts list and the 3D view,
        # so it stays out of the model too. Same test as the page's `parked`: no overlap with the plate.
        rows_of = h if mode != "relief" else d
        if col + w <= 0 or col >= plate_cols or row + rows_of <= 0 or row >= plate_rows:
            skipped += 1
            continue
        base = float(b.get("base", 0) or 0)            # relief only: plates proud of the frame
        x = (col + w / 2.0) * LDU_PER_STUD             # across, centred on the footprint
        if mode == "relief":
            z = (row + d / 2.0) * LDU_PER_STUD
            y = -(base + h) * LDU_PER_PLATE            # origin at the TOP of the body; up is -Y
        else:
            z = 0.0                                    # one layer: a side elevation has no depth
            y = -(plate_rows - row) * LDU_PER_PLATE    # row counts DOWN the page, height counts UP
        colour = int(b.get("color", 0))
        part = str(b.get("id", "3005")) + ".dat"
        # A flipped part is TURNED, not mirrored: mirroring a slope makes a part that does not exist.
        # 180 degrees about the vertical axis, which in LDraw's downward Y is (-1,0,0 / 0,1,0 / 0,0,-1).
        a, i = (-1.0, -1.0) if b.get("flip") else (1.0, 1.0)
        out.append("1 %d %g %g %g %g 0 0 0 1 0 0 0 %g %s" % (colour, x, y, z, a, i, part))
    out.append("0")
    return "\n".join(out) + "\n"


def render(ldr_path, png_path, width=1000, height=800, angle=None):
    """LDView, in the configuration that gives the instruction look: edges on, no background."""
    if not os.path.isfile(LDVIEW):
        sys.exit("LDView is not where this expects it:\n  %s" % LDVIEW)
    cmd = [LDVIEW, ldr_path,
           "-LDrawDir=" + LDRAWDIR,
           "-SaveSnapshot=" + png_path,
           "-SaveWidth=%d" % width, "-SaveHeight=%d" % height,
           "-SaveAlpha=1",            # transparent, so no gray background anywhere
           "-AutoCrop=1",
           "-ShowEdges=1",
           "-ConditionalHighlights=1",
           "-SaveActualSize=0"]
    if angle:                          # camera globe: latitude,longitude - the LEGO three-quarter view
        cmd.append("-cg%s" % angle)
    subprocess.run(cmd, check=False)
    return os.path.isfile(png_path)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__.strip().split("\n\n")[1])
    src = argv[1]
    with open(src, encoding="utf-8") as f:
        design = json.load(f)
    if design.get("sangala") != "block":
        sys.exit("%s is not a Sangala Blocks design" % src)

    ldr = os.path.splitext(src)[0] + ".ldr"
    with open(ldr, "w", encoding="utf-8", newline="\n") as f:
        f.write(to_ldr(design))
    print("wrote %s  (%d bricks)" % (ldr, len(design.get("bricks", []))))

    if "--render" in argv:
        png = os.path.splitext(src)[0] + ".png"
        ok = render(ldr, png, angle="30,45")
        print(("rendered %s" % png) if ok else "LDView produced no image")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
