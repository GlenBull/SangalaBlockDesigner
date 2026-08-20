"""Builds 'Assembling the Sangala Crane' - a sample set of building instructions.

Glen's order, 2026-08-20: head and crown, body, wings, wings onto the body, legs, baseplate, neck,
and the head placed on the neck last. The three sub-assemblies are shown on their own; the five
steps after them are cumulative, so each picture is the model as it stands at the end of that step.

THE PICTURES ARE THE APPLICATION'S OWN SNAPSHOTS. Glen, 2026-08-20: "isn't this what we built the
snapshot feature for?" - and it is. Each step is posted to the bridge's /snapshot route, which is
exactly what the Snapshot button does, at exactly the angle it uses, so these are the pictures a
student pressing Snapshot after each step would get. Sangala Blocks must be running for this to work.

The written instructions are added to the document afterward, which is the division Glen specified
for the feature: "students will be able to save the completed list of images in a Word file, where
written instructions should be added."

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
from makedocx import Doc                                             # noqa: E402

SRC = os.path.join(BLOCKS, "Projects", "Crane (for export).block")
WORK = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making"
        r"\_Drafts\Working\Crane Instructions")
DRAFTS = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

# The Snapshot button's own settings, so a step looks the way it would look if the button were
# pressed after building it. The camera stays put for every step, so the model never appears to jump.
BRIDGE = "http://localhost:8830"
ANGLE, WIDE, TALL = "30,45", 1000, 800

HEAD = ["Head", "Eyes", "Crown", None]          # None = the loose beak, which is in no group
BODY = ["Body", "Back"]
WINGS = ["Wing (left)", "Wing (right)"]

# Each step names the groups whose bricks are IN the picture. A sub-assembly stands alone; a
# cumulative step carries everything placed before it.
STEPS = [
    dict(n=1, title="Assemble the Head and Crown", groups=HEAD, alone=True),
    dict(n=2, title="Assemble the Body", groups=BODY, alone=True),
    dict(n=3, title="Assemble the Wings", groups=WINGS, alone=True),
    dict(n=4, title="Attach the Wings to the Body", groups=BODY + WINGS, alone=True),
    dict(n=5, title="Add the Legs to the Body", groups=BODY + WINGS + ["Legs"], alone=True),
    dict(n=6, title="Place the Crane on the Baseplate", groups=BODY + WINGS + ["Legs"], base=True),
    dict(n=7, title="Add the Neck", groups=BODY + WINGS + ["Legs", "Neck"], base=True),
    dict(n=8, title="Place the Crown and Head on the Neck",
         groups=BODY + WINGS + ["Legs", "Neck"] + HEAD, base=True),
]


def gname(b):
    g = b.get("gnames") or []
    return g[0] if g and g[0] else None


def load():
    with open(SRC, encoding="utf-8") as f:
        return json.load(f)


def subset(design, step):
    """The design as it stands at this step: only the bricks the step has placed."""
    want = set(step["groups"])
    keep = []
    for b in design["bricks"]:
        nm = gname(b)
        if b["id"] == "92438":                       # the baseplate arrives at its own step
            if step.get("base"):
                keep.append(b)
            continue
        if nm in want or (nm is None and None in want):
            keep.append(b)
    out = dict(design)
    out["bricks"] = keep
    return out


def picture(design, step):
    os.makedirs(WORK, exist_ok=True)
    stem = os.path.join(WORK, "step%d" % step["n"])
    with open(stem + ".block", "w", encoding="utf-8") as f:
        json.dump(design, f)
    ldr = stem + ".ldr"
    text = ldr_export.to_ldr(design)
    with open(ldr, "w", encoding="utf-8") as f:
        f.write(text)
    png = stem + ".png"
    if os.path.exists(png):
        os.remove(png)
    url = "%s/snapshot?angle=%s&w=%d&h=%d" % (BRIDGE, ANGLE, WIDE, TALL)
    req = urllib.request.Request(url, data=text.encode("utf-8"),
                                 headers={"Content-Type": "text/plain"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            if r.status != 200:
                return None
            blob = r.read()
    except Exception as e:
        sys.exit("The snapshot route did not answer (%s). Sangala Blocks must be running: start "
                 "it from its own icon, so the renderer travels with it." % e)
    with open(png, "wb") as f:
        f.write(blob)
    return png


MAX_W_IN, MAX_H_IN = 4.6, 3.5


def fit_width(png):
    """The width that keeps a picture inside both limits, whatever shape it came back."""
    from makedocx import _pixel_size
    w, h = _pixel_size(png)
    if not w or not h:
        return MAX_W_IN
    return round(min(MAX_W_IN, MAX_H_IN * (float(w) / float(h))), 2)


def tally(design):
    """What this step places, as a reader would read it: part, color, how many."""
    seen = {}
    order = []
    for b in design["bricks"]:
        k = (b["name"], b["color"])
        if k not in seen:
            seen[k] = 0
            order.append(k)
        seen[k] += 1
    return [(nm, col, seen[(nm, col)]) for nm, col in order]


# A caption says what the picture SHOWS. Repeating the heading underneath it says nothing twice.
CAPTION = {
    1: "The Head and Crown, Built as One Piece",
    2: "The Body, with the Back Sloping Away to the Tail",
    3: "The Two Wings, Built as a Mirrored Pair",
    4: "Both Wings Attached to the Body",
    5: "The Legs Set into the Underside of the Body",
    6: "The Crane Standing on the Baseplate",
    7: "The Neck Rising from the Front of the Body",
    8: "The Finished Crane",
}
COUNT = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
         9: "Nine", 10: "Ten"}

COLORS = {15: "white", 71: "light bluish gray", 72: "dark bluish gray", 0: "black",
          14: "yellow", 4: "red", 2: "green", 1: "blue", 70: "reddish brown", 19: "tan"}

WORDS = {
    1: ["The head is two black pieces with a red beak and two white eyes, and the crown sits on "
        "top of it. Build it on its own; it is placed on the neck at the very end, once the rest "
        "of the crane is standing.",
        "Begin with the black Brick 1 x 2 that forms the head. Lay the black Plate 1 x 3 across "
        "its top, overhanging at the back, and press the red Slope Brick 45 2 x 1 onto the front "
        "of the head to make the beak. Add a white Plate 1 x 1 Round to each side of the head for "
        "the eyes, one facing each way.",
        "The crown is three yellow pieces standing on the black plate: an inverted slope, a cone, "
        "and a second inverted slope facing the other way. Each stands on a single stud, and the "
        "two slopes overhang the plate at either end."],
    2: ["The body is the largest sub-assembly and everything else is added to it. It is built from "
        "two side-stud bricks, which carry the wings later, with plates closing the front and back "
        "and a stack of slopes forming the curve of the crane's back.",
        "Place the two dark bluish gray Brick 2 x 4 x 2 with Studs on Sides side by side, so the "
        "studded faces look outward on both sides. Close the front and back with the blue Plate 2 "
        "x 4 and the yellow Plate 2 x 3.",
        "Build the back on top: the Brick 2 x 4 first, then the slopes above and behind it, "
        "stepping back in courses so the line of the back falls away towards the tail."],
    3: ["Each wing is three pieces and the two are mirror images, so build them as a pair and keep "
        "them the right way round. The curved wedge is the wing itself; the two slopes behind it "
        "close the wing where it meets the body.",
        "For each wing, lay the light bluish gray Wedge 6 x 4 Triple Curved flat, with its curve "
        "trailing backwards. Add a Slope Brick 45 2 x 2 at each end of its inner edge, one above "
        "and one below, so the wing has a straight face to sit against the body.",
        "Set the second wing out as the mirror of the first rather than a copy of it: the curves "
        "must sweep the same way when both are on the bird."],
    4: ["The wings snap onto the studs on the sides of the body. This is what the two side-stud "
        "bricks in the body were for.",
        "Hold the body with a studded face towards you and press the first wing onto it, its "
        "straight inner edge against the body and its curve trailing behind. Turn the body round "
        "and add the second wing to the other side, at the same height, so the pair are level."],
    5: ["The legs are two black bricks, and they are not side by side: one stands a little in "
        "front of the other, as a wading bird's legs do.",
        "Press a black Brick 1 x 1 x 3 into the underside of the body towards the front, and the "
        "second a few studs behind it. Check that both reach the same depth, or the crane will "
        "not stand level."],
    6: ["The baseplate is what the crane stands on, and it is added now rather than at the start, "
        "so that the body can be turned over freely while the legs are fitted.",
        "Stand the crane on the green Plate 8 x 16 and press both legs down onto it. The bird "
        "faces along the length of the plate, with room in front of it and behind."],
    7: ["The neck is a single tall brick with a plate at its foot, and it goes on after the crane "
        "is standing so that it is not in the way while the wings and legs are fitted.",
        "Set the light bluish gray Plate 1 x 2 on the top of the body, on the midline, and stand "
        "the Brick 1 x 1 x 5 on it. The neck rises from the front of the body, not its center."],
    8: ["The head and crown, built in the first step, go on last.",
        "Lower the head onto the top of the neck so that the beak points forward and the crown "
        "stands upright above it. The crane is finished."],
}


def main():
    design = load()
    made = []
    for step in STEPS:
        sub = subset(design, step)
        png = picture(sub, step)
        made.append((step, sub, png))
        print("step %d: %2d bricks -> %s" % (step["n"], len(sub["bricks"]),
                                             os.path.basename(png) if png else "NO PICTURE"))

    d = Doc()
    d.title("Assembling the Sangala Crane")
    d.body("The crane is built as three sub-assemblies \u2014 the head and crown, the body, and "
           "the pair of wings \u2014 which are then brought together. The head is made first and "
           "fitted last, so that it is not in the way while the wings, the legs and the neck are "
           "being placed. Thirty-four pieces in all.")
    d.body("Each step lists the pieces it places, by the design number printed in the parts list, "
           "and the picture beneath it shows the work at the end of that step.")

    fig = 0
    for step, sub, png in made:
        d.heading("%d. %s" % (step["n"], step["title"]))
        for para in WORDS[step["n"]]:
            d.body(para)
        rows = tally(sub) if step["n"] <= 3 else None
        if rows:
            d.body("Pieces used in this step:", before_list=True)
            for nm, col, n in rows:
                # "One Brick 1 x 2", not "1 x Brick 1 x 2" - a numeral before a part whose own name
                # is "1 x 2" reads as part of the part
                d.item("%s %s. " % (COUNT.get(n, str(n)), nm), "In %s." % COLORS.get(col, "its color"))
        if png and os.path.exists(png):
            fig += 1
            # SIZE BY HEIGHT, NOT WIDTH. A render is auto-cropped to its content, so a tall
            # sub-assembly and a wide one come back at very different shapes; a fixed WIDTH made the
            # tall ones over six inches high, and an inline figure that no longer fits is pushed
            # whole onto the next page, leaving the bottom of the one before it empty. Capping the
            # HEIGHT keeps every figure on the page its text is on.
            d.image(png, width_in=fit_width(png))
            d.caption("Figure %d. %s" % (fig, CAPTION[step["n"]]))
    print(d.save(DRAFTS, "Assembling the Sangala Crane"))


if __name__ == "__main__":
    main()
