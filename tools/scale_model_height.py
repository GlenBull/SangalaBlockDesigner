"""Scale a Sangala Studio .model's HEIGHT by one factor, width untouched.

The tile-to-plate step of the mosaic-to-brick-figure workflow (see "Mosaic to Brick
Figure Workflow" in _Drafts): a mosaic tile is 8 x 8 mm, a tile read as one stud by
two plates is 8 x 6.4, so the figure's height comes down to eight-tenths of its
width. This applies that one multiplication and nothing else - every y in every
outline, hole, and points attribute, scaled about the design origin. Depth
(data-z, data-z0), placement (offx, offy), and all other fields pass through
untouched. Refuses to overwrite an existing output file.

    python tools\\scale_model_height.py <in.model> <factor> <out.model>
"""
import io
import json
import sys


def scale_height(path_in, factor, path_out):
    d = json.load(io.open(path_in, encoding="utf-8"))
    sy = lambda v: round(v * factor, 2)
    for o in d["state"]["objs"]:
        if o.get("poly"):
            o["poly"] = [[p[0], sy(p[1])] for p in o["poly"]]
        if o.get("holes"):
            o["holes"] = [[[p[0], sy(p[1])] for p in h] for h in o["holes"]]
        attrs = o.get("attrs")
        if isinstance(attrs, list):
            for pair in attrs:
                if pair[0] == "points":
                    pts = [q.split(",") for q in pair[1].split()]
                    pair[1] = " ".join("%g,%g" % (float(x), sy(float(y))) for x, y in pts)
    io.open(path_out, "x", encoding="utf-8", newline="\n").write(
        json.dumps(d, separators=(",", ":")))
    print("%s x %g height -> %s" % (path_in.split("\\")[-1], factor, path_out))
    for o in d["state"]["objs"]:
        a = dict(o.get("attrs") or [])
        ys = [p[1] for p in (o.get("poly") or [])]
        if ys:
            print("  %-8s y %g..%g" % (a.get("data-name") or "?", min(ys), max(ys)))


if __name__ == "__main__":
    scale_height(sys.argv[1], float(sys.argv[2]), sys.argv[3])
