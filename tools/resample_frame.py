"""Resample a Sangala Studio side-view frame onto the brick lattice at a kit's own footprint.

Glen's request (2026-08-21): "I would like to have a frame to import that approximates the
brick [crane] so that I can make a video in which I drag the bricks in blocks over the frame.
It doesn't have to be perfect, but it has to be close enough to support the narrative."

The proportion-true frame (Projects\\Crane.model) is about 40% larger than the crane actually
built of bricks, so kit pieces dragged over it never line up with it. This script makes the
frame KIT-SIZED: it fits the figure's bounding box to the built figure's own columns and rows,
rasterizes every region onto the 8 x 3.2 mm side-view lattice, and traces the filled cells
back into rectilinear outlines (with holes). Every edge of the result lies on a lattice line,
so a brick snapped to the lattice sits flush on the frame.

    python tools\\resample_frame.py [figure.model] [built.block] [out.model]

Defaults are the crane. The output is a Studio .model that Block Designer's Open button
imports as a frame (loadModel), landing exactly where the .block's bricks sit - same columns,
same rows, same placement on the plate - so the kit pieces land on it.

Two deliberate approximations, both inside Glen's "close enough" bar:
  - The built figure's extent is measured naively (col..col+w, row..row+h). Exact for upright
    parts; a turned part can reach further than h says, but never past the envelope the
    upright parts set on the crane (verified against Crane.block: cols 6-19, rows 24-62).
  - X and Y are fitted independently, so the figure's aspect follows the brick build's.

Ground regions (data-plane-name "Frame", the grass band) are NOT resampled through the figure
fit: the built figure's ground is its baseplate, so they are replaced by one rectangle at the
baseplate's own side profile, keeping the first ground region's name and fill.
"""
import io
import json
import sys

STUD = 8.0
PLATE = 3.2
SS = 16                      # supersamples per cell axis: 16 x 16 points per 8 x 3.2 mm cell
BASEPLATE_IDS = {"92438"}    # parts that are the ground, not the figure


# ---------- reading ------------------------------------------------------------------------

def read_regions(path):
    d = json.load(io.open(path, encoding="utf-8"))
    figure, ground = [], []
    for o in d["state"]["objs"]:
        a = o.get("attrs") or []
        a = dict(a) if isinstance(a, list) else dict(a.items())
        poly = o.get("poly")
        if not poly or len(poly) < 3:
            continue
        r = {
            "name": a.get("data-name") or "",
            "fill": a.get("data-fill") or "#a0a5a9",
            "z": float(a.get("data-z") or 0),
            "z0": float(a.get("data-z0") or 0),
            "poly": [[float(p[0]), float(p[1])] for p in poly],
            "holes": [[[float(p[0]), float(p[1])] for p in h] for h in (o.get("holes") or [])],
        }
        (ground if a.get("data-plane-name") == "Frame" else figure).append(r)
    return d, figure, ground


def read_build(path):
    d = json.load(io.open(path, encoding="utf-8"))
    lo_c = lo_r = 10 ** 9
    hi_c = hi_r = -(10 ** 9)
    plate = None
    for b in d.get("bricks") or []:
        if str(b.get("id")) in BASEPLATE_IDS:
            plate = b
            continue
        lo_c = min(lo_c, b["col"]);            hi_c = max(hi_c, b["col"] + b["w"])
        lo_r = min(lo_r, b["row"]);            hi_r = max(hi_r, b["row"] + b["h"])
    if hi_c < lo_c:
        raise SystemExit("no figure bricks in " + path)
    return d, (lo_c, hi_c, lo_r, hi_r), plate


# ---------- rasterizing --------------------------------------------------------------------

def in_ring(x, y, ring):
    """Even-odd ray cast, the page's own fill rule."""
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


def coverage(region, c, r):
    """Fraction of cell (c, r) the region covers, by midpoint supersampling."""
    hit = 0
    for j in range(SS):
        y = (r + (j + 0.5) / SS) * PLATE
        for i in range(SS):
            x = (c + (i + 0.5) / SS) * STUD
            if in_ring(x, y, region["poly"]) and not any(in_ring(x, y, h) for h in region["holes"]):
                hit += 1
    return hit / (SS * SS)


# ---------- tracing cells back to outlines --------------------------------------------------

def components(cells):
    """4-connected components of a set of (c, r) cells."""
    left, out = set(cells), []
    while left:
        seed = next(iter(left))
        comp, edge = {seed}, [seed]
        left.discard(seed)
        while edge:
            c, r = edge.pop()
            for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if n in left:
                    left.discard(n)
                    comp.add(n)
                    edge.append(n)
        out.append(comp)
    return out


def trace(comp):
    """Boundary loops of one component: one outer ring (positive shoelace area in the page's
    y-down coordinates) and any holes (negative). Interior kept on the travel's right, which
    is the winding the source .model files carry."""
    edges = {}
    for c, r in comp:
        if (c, r - 1) not in comp:
            edges.setdefault((c, r), []).append((c + 1, r))
        if (c + 1, r) not in comp:
            edges.setdefault((c + 1, r), []).append((c + 1, r + 1))
        if (c, r + 1) not in comp:
            edges.setdefault((c + 1, r + 1), []).append((c, r + 1))
        if (c - 1, r) not in comp:
            edges.setdefault((c, r + 1), []).append((c, r))
    loops = []
    while edges:
        start = next(iter(edges))
        loop = [start]
        prev = None
        at = start
        while True:
            nxts = edges[at]
            if len(nxts) == 1 or prev is None:
                nxt = nxts[0]
            else:
                # a pinch vertex: keep the loop simple by turning as sharply toward the
                # interior (the right-hand side of travel) as the free edges allow
                dx, dy = at[0] - prev[0], at[1] - prev[1]
                def turn(n):
                    ex, ey = n[0] - at[0], n[1] - at[1]
                    return dx * ey - dy * ex          # y-down: positive = right turn
                nxt = max(nxts, key=turn)
            nxts.remove(nxt)
            if not nxts:
                del edges[at]
            if nxt == start:
                loops.append(loop)
                break
            loop.append(nxt)
            prev, at = at, nxt
    return loops


def area2(loop):
    s = 0
    for i in range(len(loop)):
        x1, y1 = loop[i]
        x2, y2 = loop[(i + 1) % len(loop)]
        s += x1 * y2 - x2 * y1
    return s


def simplify(loop):
    out = []
    n = len(loop)
    for i in range(n):
        a, b, c = loop[i - 1], loop[i], loop[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0]):
            out.append(b)
    return out


def to_mm(loop):
    pts = [[round(c * STUD, 2), round(r * PLATE, 2)] for c, r in loop]
    return pts + [pts[0][:]]                  # the source files repeat the first point


# ---------- the resample ---------------------------------------------------------------------

def resample(model_in, block_in, model_out):
    src, figure, ground = read_regions(model_in)
    build, (c0, c1, r0, r1), plate = read_build(block_in)

    xs = [p[0] for g in figure for p in g["poly"]]
    ys = [p[1] for g in figure for p in g["poly"]]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    sx = (c1 - c0) * STUD / (bx1 - bx0)
    sy = (r1 - r0) * PLATE / (by1 - by0)
    fit = lambda p: [c0 * STUD + (p[0] - bx0) * sx, r0 * PLATE + (p[1] - by0) * sy]
    print("figure %s: %.1f x %.1f mm -> %d studs x %d plates at cols %d-%d, rows %d-%d (x%.3f, x%.3f)"
          % (model_in.split("\\")[-1], bx1 - bx0, by1 - by0, c1 - c0, r1 - r0, c0, c1, r0, r1, sx, sy))

    fitted = [{**g, "poly": [fit(p) for p in g["poly"]],
               "holes": [[fit(p) for p in h] for h in g["holes"]]} for g in figure]

    grid = [(c, r) for r in range(r0, r1) for c in range(c0, c1)]
    cov = [{cell: coverage(g, *cell) for cell in grid} for g in fitted]
    cells = [set(cell for cell in grid if cv[cell] >= 0.5) for cv in cov]

    # seams: a cell mostly covered but claimed by nobody joins the region covering most of it
    seams = 0
    for cell in grid:
        if any(cell in s for s in cells):
            continue
        total = sum(cv[cell] for cv in cov)
        if total >= 0.5:
            best = max(range(len(cov)), key=lambda i: cov[i][cell])
            cells[best].add(cell)
            seams += 1

    overlaps = sum(1 for cell in grid if sum(cell in s for s in cells) > 1)

    objs = []
    for g, cs in zip(figure, cells):
        for comp in components(cs):
            loops = sorted(trace(comp), key=area2, reverse=True)
            outer, holes = loops[0], loops[1:]
            if area2(outer) <= 0:
                raise SystemExit("tracing produced no outer ring for " + g["name"])
            objs.append({**g, "cells": len(comp),
                         "poly": to_mm(simplify(outer)),
                         "holes": [to_mm(simplify(h)) for h in holes]})

    # ---- self-check: the traced outlines must reproduce the cells they were traced from
    union_meant = set().union(*cells) if cells else set()
    union_back = set()
    for g in objs:
        for cell in grid:
            x, y = (cell[0] + 0.5) * STUD, (cell[1] + 0.5) * PLATE
            if in_ring(x, y, g["poly"][:-1]) and not any(in_ring(x, y, h[:-1]) for h in g["holes"]):
                union_back.add(cell)
    if union_back != union_meant:
        raise SystemExit("round-trip mismatch: traced outlines fill %d cells, rasterizing meant %d"
                         % (len(union_back), len(union_meant)))

    # the ground: the baseplate's own side profile, under the first ground region's name
    if ground and plate is not None:
        px0 = (plate["col"] + (plate.get("half") or 0)) * STUD
        objs.append({"name": ground[0]["name"], "fill": ground[0]["fill"],
                     "z": plate["d"] * STUD, "z0": ground[0]["z0"], "cells": plate["w"] * plate["h"],
                     "poly": [[round(px0, 2), round(plate["row"] * PLATE, 2)],
                              [round(px0 + plate["w"] * STUD, 2), round(plate["row"] * PLATE, 2)],
                              [round(px0 + plate["w"] * STUD, 2), round((plate["row"] + plate["h"]) * PLATE, 2)],
                              [round(px0, 2), round((plate["row"] + plate["h"]) * PLATE, 2)],
                              [round(px0, 2), round(plate["row"] * PLATE, 2)]],
                     "holes": []})

    # ---- a picture, one character per cell, so the shape can be read before the page draws it
    marks = {}
    for g, cs in zip(figure, cells):
        for cell in cs:
            marks[cell] = "#" if cell in marks else (g["name"][:1] or "?")
    for r in range(r0, r1):
        print("   " + "".join(marks.get((c, r), ".") for c in range(c0, c1)))

    # ---- write the .model, in the shape the source file carries
    out_objs = []
    for i, g in enumerate(objs):
        pts = " ".join("%g,%g" % (p[0], p[1]) for p in g["poly"][:-1])
        out_objs.append({
            "id": i + 1, "tag": "polygon",
            "attrs": [["points", pts], ["data-mosaic", "1"],
                      ["data-z", "%g" % g["z"]], ["data-z0", "%g" % g["z0"]],
                      ["data-studs", "1"], ["data-fill", g["fill"]],
                      ["data-name", g["name"]], ["fill", "none"],
                      ["stroke", "#ff0000"], ["stroke-width", "0.2"]],
            "kind": "cut", "orig": "cut",
            "poly": g["poly"], "holes": g["holes"] or None, "mesh": None, "gpath": None})
    out = {"sangala": "project", "version": src.get("version", 2), "mode3D": True,
           "units": "mm", "showMarks": False, "material": src.get("material", "Cardstock"),
           "offx": build.get("placeX") or 0, "offy": build.get("placeY") or 0,
           "settings": {**(src.get("settings") or {}), "scale": "100"},
           "view": {"zoom": 1, "panX": 0, "panY": 0}, "refImage": None,
           "state": {"objSeq": len(out_objs), "groupSeq": 0, "printFile": False, "objs": out_objs}}
    io.open(model_out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(out, separators=(",", ":")))

    print("%d regions -> %d outlines, %d seam cells joined, %d overlap cells"
          % (len(figure), len(objs), seams, overlaps))
    for g in objs:
        print("  %-8s %-9s z %5.1f  z0 %4.1f  %3d cells  %3d points  %d holes"
              % (g["name"][:8], g["fill"], g["z"], g["z0"], g["cells"],
                 len(g["poly"]) - 1, len(g["holes"])))
    print("wrote", model_out)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    resample(a[0] if len(a) > 0 else r"D:\Code Projects\Block Tools\Projects\Crane.model",
             a[1] if len(a) > 1 else r"D:\Code Projects\Block Tools\Projects\Crane.block",
             a[2] if len(a) > 2 else r"D:\Code Projects\Block Tools\Projects\Crane (video frame).model")
