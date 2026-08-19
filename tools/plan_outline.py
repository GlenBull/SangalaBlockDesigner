"""Measure the PLAN OUTLINE of an LDraw part, and draw it so it can be looked at.

The workspace drew every part from a hand-written polygon - a rectangle, a trapezoid, a wedge -
while the 3D view drew the part's real geometry. So a wedge came out as a generic trapezoid and the
flat section at 43712's wide end did not show at all (Glen, 2026-08-19). The cure is to take the
outline from the part's own geometry, one silhouette per part number, which fixes every part rather
than that one wedge.

This is the ORACLE for that outline, not the application: the page computes its own silhouette from
the mesh it has already loaded for the 3D view, and this script computes the same thing here, from
the same library files, so the two can be compared and LOOKED AT.

    python tools/plan_outline.py 43712 6069 3001        # measure and report
    python tools/plan_outline.py --png out.png 43712    # and draw it

The method, which the page repeats:
  * flatten the part to triangles, following its sub-part references;
  * CLAMP y to the origin plane, so the studs (which stand at negative y, above the body) fold flat
    onto the top face and the outline is the BODY's - the studs are drawn as their own marks;
  * project onto the plane the view uses - the plan is (x, -z), an elevation is (x, y);
  * rasterize the projected triangles, then walk the boundary of the filled cells and simplify it.
Rasterizing rather than unioning polygons is what makes it robust: overlapping triangles, a hollow
underside and a curved edge all rasterize the same way, and no part is a special case.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ldparts                       # which also puts stdout into UTF-8

GRID = 160          # cells along the longer side of the part's box
TOL = 1.2           # simplification tolerance, in cells


def flatten(path, xf=None, depth=0, seen=(), out=None):
    """Every triangle in a part, in the part's own LDU coordinates."""
    out = [] if out is None else out
    xf = xf or (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
    key = os.path.normcase(path)
    if depth > 16 or key in seen or len(out) > 200000:
        return out
    seen = seen + (key,)

    def at(p):
        return (xf[0] * p[0] + xf[1] * p[1] + xf[2] * p[2] + xf[9],
                xf[3] * p[0] + xf[4] * p[1] + xf[5] * p[2] + xf[10],
                xf[6] * p[0] + xf[7] * p[1] + xf[8] * p[2] + xf[11])

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            t = line.split()
            if len(t) < 2:
                continue
            if t[0] == "1" and len(t) >= 15:
                try:
                    v = [float(x) for x in t[2:14]]
                except ValueError:
                    continue
                s = (v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[0], v[1], v[2])
                m = [0.0] * 12
                for i in range(3):
                    for j in range(3):
                        m[i * 3 + j] = (xf[i * 3] * s[j] + xf[i * 3 + 1] * s[3 + j]
                                        + xf[i * 3 + 2] * s[6 + j])
                    m[9 + i] = (xf[i * 3] * s[9] + xf[i * 3 + 1] * s[10]
                                + xf[i * 3 + 2] * s[11] + xf[9 + i])
                sub = ldparts.locate(" ".join(t[14:]))
                if sub:
                    flatten(sub, tuple(m), depth + 1, seen, out)
            elif t[0] in ("3", "4"):
                n = 3 if t[0] == "3" else 4
                try:
                    v = [float(x) for x in t[2:2 + 3 * n]]
                except ValueError:
                    continue
                q = [at(v[3 * i:3 * i + 3]) for i in range(n)]
                out.append((q[0], q[1], q[2]))
                if n == 4:
                    out.append((q[0], q[2], q[3]))
    return out


def project(tris, iu, iv, body=True):
    """Drop to two axes. `body` folds anything above the origin plane onto it - the studs."""
    out = []
    for t in tris:
        q = []
        for p in t:
            y = max(p[1], 0.0) if body else p[1]
            r = (p[0], y, p[2])
            q.append((r[iu], r[iv]))
        out.append(q)
    return out


def raster(flat, grid=GRID):
    """Fill the projected triangles into a boolean grid. Returns the grid and its box."""
    xs = [p[0] for t in flat for p in t]
    ys = [p[1] for t in flat for p in t]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0) or 1.0
    s = grid / span
    W = max(2, int(round((x1 - x0) * s))) + 2      # a one-cell margin, so a loop closes inside
    H = max(2, int(round((y1 - y0) * s))) + 2
    g = [bytearray(W) for _ in range(H)]
    for t in flat:
        px = [((p[0] - x0) * s + 1, (p[1] - y0) * s + 1) for p in t]
        ay = max(0, int(min(p[1] for p in px)))
        by = min(H - 1, int(max(p[1] for p in px)) + 1)
        for row in range(ay, by + 1):
            cy = row + 0.5
            xsx = []
            for i in range(3):
                (ux, uy), (vx, vy) = px[i], px[(i + 1) % 3]
                if (uy <= cy) != (vy <= cy):
                    xsx.append(ux + (cy - uy) * (vx - ux) / (vy - uy))
            if len(xsx) < 2:
                continue
            lo, hi = min(xsx), max(xsx)
            a = max(0, int(lo + 0.5))
            b = min(W - 1, int(hi - 0.5))
            r = g[row]
            for c in range(a, b + 1):
                r[c] = 1
    return g, (x0, y0, s, W, H)


def trace(g):
    """The boundary of the filled cells, as closed loops of grid points.

    Each filled cell contributes the sides that face an empty neighbor, directed so the filled cell
    is on the right. Chained, that gives the outer boundary one way round and any hole the other -
    which is what a nonzero fill needs, and it comes out of the rule rather than being sorted after.
    """
    H, W = len(g), len(g[0])
    edges = {}
    for y in range(H):
        for x in range(W):
            if not g[y][x]:
                continue
            if y == 0 or not g[y - 1][x]:
                edges.setdefault((x, y), []).append((x + 1, y))
            if x == W - 1 or not g[y][x + 1]:
                edges.setdefault((x + 1, y), []).append((x + 1, y + 1))
            if y == H - 1 or not g[y + 1][x]:
                edges.setdefault((x + 1, y + 1), []).append((x, y + 1))
            if x == 0 or not g[y][x - 1]:
                edges.setdefault((x, y + 1), []).append((x, y))
    loops = []
    while edges:
        start = next(iter(edges))
        loop, at = [start], start
        while True:
            nxt = edges.get(at)
            if not nxt:
                break
            to = nxt.pop()
            if not nxt:
                del edges[at]
            at = to
            if at == start:
                break
            loop.append(at)
        if len(loop) > 3:
            loops.append(loop)
    return loops


def area(loop):
    a = 0.0
    for i in range(len(loop)):
        x0, y0 = loop[i]
        x1, y1 = loop[(i + 1) % len(loop)]
        a += x0 * y1 - x1 * y0
    return a / 2


def simplify(loop, tol=TOL):
    """Douglas-Peucker round a closed loop, from its two furthest-apart points."""
    n = len(loop)
    if n < 4:
        return loop
    i0 = 0
    i1 = max(range(n), key=lambda i: (loop[i][0] - loop[0][0]) ** 2 + (loop[i][1] - loop[0][1]) ** 2)
    return dp(loop[i0:i1 + 1], tol)[:-1] + dp(loop[i1:] + [loop[0]], tol)[:-1]


def dp(pts, tol):
    if len(pts) < 3:
        return list(pts)
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    n = (dx * dx + dy * dy) ** .5
    worst, at = -1, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dx * (ay - py) - dy * (ax - px)) / n if n else ((px - ax) ** 2 + (py - ay) ** 2) ** .5
        if d > worst:
            worst, at = d, i
    if worst <= tol:
        return [pts[0], pts[-1]]
    return dp(pts[:at + 1], tol)[:-1] + dp(pts[at:], tol)


def outline(number, iu=0, iv=2, flip_v=True):
    """The measured outline of a part, normalized to its own box: [0,1] across and down."""
    path, _, _ = ldparts.resolve(number)
    if not path:
        return None
    tris = flatten(path)
    if not tris:
        return None
    flat = project(tris, iu, iv)
    if flip_v:
        flat = [[(p[0], -p[1]) for p in t] for t in flat]
    g, (x0, y0, s, W, H) = raster(flat)
    loops = [simplify(l) for l in trace(g)]
    if not loops:
        return None
    big = max(abs(area(l)) for l in loops)
    loops = [l for l in loops if abs(area(l)) >= big * .02]
    ux0 = min(p[0] for l in loops for p in l)
    uy0 = min(p[1] for l in loops for p in l)
    ux1 = max(p[0] for l in loops for p in l)
    uy1 = max(p[1] for l in loops for p in l)
    uw, uh = (ux1 - ux0) or 1, (uy1 - uy0) or 1
    return [[((p[0] - ux0) / uw, (p[1] - uy0) / uh) for p in l] for l in loops]


def draw(numbers, png, iu=0, iv=2):
    from PIL import Image, ImageDraw
    cell, pad = 260, 30
    im = Image.new("RGB", (len(numbers) * (cell + pad) + pad, cell + 2 * pad + 20), "white")
    d = ImageDraw.Draw(im)
    for k, num in enumerate(numbers):
        loops = outline(num, iu, iv, flip_v=(iv == 2))
        ox = pad + k * (cell + pad)
        d.rectangle([ox, pad, ox + cell, pad + cell], outline="#cccccc")
        d.text((ox, pad + cell + 6), num, fill="#000000")
        if not loops:
            continue
        for l in loops:
            d.polygon([(ox + p[0] * cell, pad + p[1] * cell) for p in l],
                      outline="#7a3b12", fill="#f0d9a8")
    im.save(png)
    print("wrote", png)


def main(argv):
    png, nums, plane = None, [], "xz"
    i = 0
    while i < len(argv):
        if argv[i] == "--png":
            png = argv[i + 1]; i += 2
        elif argv[i] == "--plane":
            plane = argv[i + 1]; i += 2
        else:
            nums.append(argv[i]); i += 1
    # xz is the plan a relief or a tipped part shows; xy and zy are the two elevations an upright
    # part shows, and which of them applies is the yaw the 3D view already works out for the part
    iu, iv = {"xz": (0, 2), "xy": (0, 1), "zy": (2, 1)}[plane]
    if not nums:
        print(__doc__); return 1
    for n in nums:
        loops = outline(n, iu, iv, flip_v=(iv == 2))
        if not loops:
            print("%-8s no geometry" % n); continue
        print("%-8s %d loop(s), %s points" % (n, len(loops), ",".join(str(len(l)) for l in loops)))
        for l in loops[:1]:
            print("   " + " ".join("%.2f,%.2f" % p for p in l))
    if png:
        draw(nums, png, iu, iv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
