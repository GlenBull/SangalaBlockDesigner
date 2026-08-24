"""Builds 'Assembling the Sangala Crane' - building instructions, one picture per piece.

THE PICTURES ARE THE APPLICATION'S OWN SNAPSHOTS. Each step is posted to the bridge's /snapshot
route - the same call the Snapshot button makes - so Sangala Blocks must be running. The camera is
held at one angle for every picture, so the model never appears to jump between steps and each new
piece can be seen against what is already there.

WHY A PROFILE AND NOT A THREE-QUARTER VIEW. Glen, 2026-08-20: "this side view in some ways is better
for assembly instructions than the 3D view." It is: nothing hides behind anything and where a piece
goes is unambiguous. The camera globe's LONGITUDE 0 looks along the bird's depth, which is the
profile - longitude 90 looks along its length and shows the bill end-on, which is not it. A few
degrees of latitude keep the shading, and at longitude 0 the bird faces right, as it does in the
workspace.

    set PYTHONUTF8=1
    python "D:\\Code Projects\\Block Tools\\tools\\docs\\make_crane_instructions.py"
"""
import json
import os
import sys
import urllib.request

BLOCKS = r"D:\Code Projects\Block Tools"
STUDIO = r"D:\Code Projects\Silhouette Tools"
sys.path.insert(0, os.path.join(BLOCKS, "tools"))
sys.path.insert(0, os.path.join(STUDIO, "tools"))
import ldr_export                                                    # noqa: E402
from makedocx import Doc, _pixel_size                                # noqa: E402

SRC = os.path.join(BLOCKS, "Projects", "Crane (for export).block")
WORK = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making"
        r"\_Drafts\Working\Crane Instructions")
DRAFTS = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

BRIDGE = "http://localhost:8830"
ANGLE, WIDE, TALL = "10,0", 900, 750
MAX_W_IN, MAX_H_IN = 2.9, 2.0

LDCOLOR = {15: "White", 71: "Light Bluish Gray", 72: "Dark Bluish Gray", 0: "Black",
           14: "Yellow", 4: "Red", 2: "Green", 1: "Blue", 70: "Reddish Brown", 19: "Tan"}


def caption_for(design, i):
    """A caption names the piece the picture just placed. Naming the section instead would print
    the same words under every figure in it, which says nothing thirty-five times."""
    b = design["bricks"][i]
    return "The %s %s in Place" % (LDCOLOR.get(b["color"], "").strip(), b["name"])


def gname(b):
    g = b.get("gnames") or []
    return g[0] if g and g[0] else None


def groups(design):
    bs = design["bricks"]

    def pick(pred):
        return [i for i, b in enumerate(bs) if pred(b)]

    g = {
        "head":  pick(lambda b: gname(b) == "Head"),
        "beak":  pick(lambda b: gname(b) is None and b["id"] == "3040"),
        "eyes":  pick(lambda b: gname(b) == "Eyes"),
        "crown": pick(lambda b: gname(b) == "Crown"),
        "body":  pick(lambda b: gname(b) == "Body"),
        "back":  pick(lambda b: gname(b) == "Back"),
        "wingL": pick(lambda b: gname(b) == "Wing (left)"),
        "wingR": pick(lambda b: gname(b) == "Wing (right)"),
        "legs":  pick(lambda b: gname(b) == "Legs"),
        "neck":  pick(lambda b: gname(b) == "Neck"),
        "base":  pick(lambda b: b["id"] == "92438"),
    }
    g["head_all"] = g["head"] + g["beak"] + g["eyes"] + g["crown"]
    g["body_all"] = g["body"] + g["back"]
    g["wings_all"] = g["wingL"] + g["wingR"]
    g["torso"] = g["body_all"] + g["wingL"] + g["wingR"]
    return g


def shot(design, pieces, stem):
    sub = dict(design)
    sub["bricks"] = [design["bricks"][i] for i in pieces]
    text = ldr_export.to_ldr(sub)
    png = os.path.join(WORK, stem + ".png")
    url = "%s/snapshot?angle=%s&w=%d&h=%d" % (BRIDGE, ANGLE, WIDE, TALL)
    req = urllib.request.Request(url, data=text.encode("utf-8"),
                                 headers={"Content-Type": "text/plain"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            blob = r.read()
    except Exception as e:
        sys.exit("The snapshot route did not answer (%s). Sangala Blocks must be running: start "
                 "it from its own icon, so the renderer travels with it." % e)
    open(png, "wb").write(blob)
    return png


def fit_width(png):
    """Sized by height as well as width: a snapshot is auto-cropped, so a tall sub-assembly and a
    wide one come back very different shapes, and a figure that no longer fits is pushed whole onto
    the next page with the gap cascading through the document."""
    w, h = _pixel_size(png)
    if not w or not h:
        return MAX_W_IN
    return round(min(MAX_W_IN, MAX_H_IN * (float(w) / float(h))), 2)


# Each entry: the sentence, then which piece it places. A step that carries a whole group instead
# names it with a count of pieces rather than one index.
SECTIONS = [
    ("1. Build the Head", "restart", [
        ("The head is a single black Brick 1 x 2. Everything in this section is added to it.",
         ("head", 0)),
        ("Lay the black Plate 1 x 3 across the top of the brick. It is longer than the brick and "
         "overhangs at the back; that overhang is what the crown will stand on.", ("head", 1)),
        ("Press the red Slope Brick 45 2 x 1 against the front of the head, its slope falling away "
         "and forward. This is the bill.", ("beak", 0)),
        ("Add a white Plate 1 x 1 Round to the near side of the head, just behind the bill. This "
         "is the eye.", ("eyes", 0)),
        ("Add the second white Plate 1 x 1 Round to the far side, in the same place. The two sit "
         "opposite each other, so from this side the second is hidden behind the head.",
         ("eyes", 1)),
    ]),
    ("2. Add the Crown", "carry", [
        ("The crown is three yellow pieces, each standing on a single stud of the black plate. "
         "Begin with an inverted slope at the back, wide end uppermost.", ("crown", 0)),
        ("Stand the Cone 1 x 1 on the middle stud.", ("crown", 1)),
        ("Add the second inverted slope at the front, facing the other way, so the two lean apart "
         "with the cone between them. The head is finished; set it aside until the last step.",
         ("crown", 2)),
    ]),
    ("3. Build the Body", "restart", [
        ("Start with a Brick 2 x 4 x 2 with Studs on Sides. The studs on its face are what the "
         "wings will attach to later, so that face looks outward.", ("body", 0)),
        ("Lay a Plate 2 x 4 against the front of it.", ("body", 1)),
        ("Lay the second Plate 2 x 4 against the back.", ("body", 2)),
        ("Add a Plate 2 x 3 behind that, half a stud in, which sets the depth of the body's back.",
         ("body", 3)),
        ("Add the second side-stud brick beside the first. The body is now two bricks deep, with a "
         "studded face on each side.", ("body", 4)),
        ("Add the last Plate 2 x 3 at the front, mirroring the one at the back.", ("body", 5)),
    ]),
    ("4. Shape the Back", "carry", [
        ("The back of the crane is a run of slopes stepping down towards the tail. Begin with the "
         "Brick 2 x 4 on top of the body.", ("back", 0)),
        ("Add a Slope Brick 45 2 x 1 at the front of that course.", ("back", 1)),
        ("Add a Slope Brick 33 3 x 1 behind it. The shallower slope is what gives the back its "
         "long line.", ("back", 2)),
        ("Step back and down: a second Slope Brick 33 3 x 1, one course lower.", ("back", 3)),
        ("A third, lower again. The three together make the curve of the back.", ("back", 4)),
        ("The same three slopes are repeated on the far side of the body, so the back reads the "
         "same from either side. Add the first of them.", ("back", 5)),
        ("Add the second.", ("back", 6)),
        ("Add the third.", ("back", 7)),
        ("Close the top course at the front with the second Slope Brick 45 2 x 1. The body is "
         "finished.", ("back", 8)),
    ]),
    ("5. Build the Wings", "restart", [
        ("Each wing is three pieces. Begin with a Slope Brick 45 2 x 2, which closes the wing "
         "where it will meet the body.", ("wingL", 0)),
        ("Add the second Slope Brick 45 2 x 2 below it.", ("wingL", 1)),
        ("Add the Wedge 6 x 4 Triple Curved. Its curve is the trailing edge of the wing.",
         ("wingL", 2)),
        ("Build the second wing as the mirror of the first rather than a copy, so the curves sweep "
         "the same way when both are on the bird. Its first slope goes here.", ("wingR", 0)),
        ("Add its second slope.", ("wingR", 1)),
        ("Add its wedge. The wings are now a matched pair.", ("wingR", 2)),
    ]),
    ("6. Attach the Wings to the Body", "set", [
        ("Press the first wing onto the studs on the side of the body, its straight inner edge "
         "against the body and its curve trailing behind.", ["body_all", "wingL"]),
        ("Fit the second wing to the other side at the same height. Seen from here the far wing is "
         "hidden exactly behind the near one, which is how you know the pair are level.",
         ["torso"]),
    ]),
    ("7. Add the Legs and Stand the Crane Up", "set", [
        ("The legs are two black Brick 1 x 1 x 3, and they are not side by side: one stands a "
         "little in front of the other, as a wading bird's legs do. Press both into the underside "
         "of the body.", ["torso", "legs"]),
        ("Stand the crane on the green Plate 8 x 16 and press both legs down onto it. The bird "
         "faces along the length of the plate, with room in front of it and behind.",
         ["torso", "legs", "base"]),
    ]),
    ("8. Add the Neck, then the Head", "set", [
        ("Set the Plate 1 x 2 on top of the body, on the midline, and stand the Brick 1 x 1 x 5 on "
         "it. The neck rises from the front of the body rather than from its center.",
         ["torso", "legs", "base", "neck"]),
        ("Lower the head onto the top of the neck, with the bill pointing forward and the crown "
         "upright above it. The crane is finished.",
         ["torso", "legs", "base", "neck", "head_all"]),
    ]),
]


def main():
    os.makedirs(WORK, exist_ok=True)
    design = json.load(open(SRC, encoding="utf-8"))
    g = groups(design)

    d = Doc()
    d.title("Assembling the Sangala Crane")
    d.body("The crane is thirty-four pieces. It is built as three sub-assemblies \u2014 the head "
           "with its crown, the body, and a pair of wings \u2014 which are then brought together. "
           "The head is made first and fitted last, so that it is not in the way while the wings, "
           "the legs and the neck are placed.")
    d.body("Each step places one piece, and the picture beneath it shows the work with that piece "
           "in place. Every picture is taken from the same side, so a new piece can always be seen "
           "against what is already there. Where a piece has a twin on the far side of the model, "
           "the second is hidden behind the first; the text says so where that matters.")

    fig, carried = 0, []
    for title, mode, steps in SECTIONS:
        d.heading(title)
        if mode == "restart":
            carried = []
        for text, what in steps:
            if mode == "set":
                pieces = []
                for k in what:
                    pieces += g[k]
            else:
                key, n = what
                carried = carried + [g[key][n]]
                pieces = carried
            fig += 1
            png = shot(design, pieces, "s%02d" % fig)
            d.body(text)
            d.image(png, width_in=fit_width(png))
            cap = (title.split(". ", 1)[1] if mode == "set"
                   else caption_for(design, carried[-1]))
            d.caption("Figure %d. %s" % (fig, cap))
            print("figure %2d  %-36s %2d pieces" % (fig, title, len(pieces)))

    print(d.save(DRAFTS, "Assembling the Sangala Crane"))


if __name__ == "__main__":
    main()
