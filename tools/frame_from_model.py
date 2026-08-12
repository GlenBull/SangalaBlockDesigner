"""Rebuild Block Designer's built-in frame from a Sangala Studio .model file.

The frame has to be BAKED INTO the application: a page opened from the file system cannot
fetch a local file, and Sangala Block Designer is opened by double-clicking it. So the
built-in crane is generated from Studio's own model rather than redrawn by hand - which is
how the two drifted apart in the first place, the baked copy being an older crane with no
Frame, no Bill and a gray wing.

    python tools/frame_from_model.py "D:\\Code Projects\\Silhouette Tools\\Projects\\Crane (Relief 8).model"

Each region carries what Studio holds for it: its name, its colour, its outline, and its
DEPTH and BASE converted from millimetres to plates (3.2 mm = 1 plate, 3 plates = 1 brick),
which are the numbers Studio's own Parts panel shows.
"""
import json, io, os, re, sys

PLATE_MM = 3.2
APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "SangalaBlockDesigner.html")


def regions(model_path):
    d = json.load(io.open(model_path, encoding="utf-8"))
    out = []
    for o in d["state"]["objs"]:
        a = dict(o.get("attrs", []))
        poly = o.get("poly")
        if not poly:
            continue
        z = float(a.get("data-z") or 0)
        z0 = float(a.get("data-z0") or 0)
        out.append({
            "name": a.get("data-name") or "",
            "fill": a.get("data-fill") or "#a0a5a9",
            "depth": int(round(z / PLATE_MM)),
            "base": int(round(z0 / PLATE_MM)),
            "poly": [[round(p[0], 2), round(p[1], 2)] for p in poly],
            # A region can be pierced: the crane's Legs are ONE outline with the gap between the
            # two legs as a hole. Dropping these renders the legs as a solid trunk - which is
            # exactly what happened when this script first ran.
            "holes": [[[round(p[0], 2), round(p[1], 2)] for p in h] for h in (o.get("holes") or [])],
        })
    return out


def main(model_path):
    rs = regions(model_path)
    js = "const CRANE = " + json.dumps(rs, separators=(",", ":")) + ";"
    src = io.open(APP, encoding="utf-8").read()
    new, n = re.subn(r"(?m)^const CRANE = .*?;$", js.replace("\\", "\\\\"), src, count=1)
    if n != 1:
        raise SystemExit("could not find the CRANE constant to replace")
    io.open(APP, "w", encoding="utf-8", newline="\n").write(new)
    print("%s -> %d regions" % (os.path.basename(model_path), len(rs)))
    for r in rs:
        print("  %-8s %-9s depth %2d  base %2d  %3d points"
              % (r["name"][:8], r["fill"], r["depth"], r["base"], len(r["poly"])))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         r"D:\Code Projects\Silhouette Tools\Projects\Crane (Relief 8).model")
