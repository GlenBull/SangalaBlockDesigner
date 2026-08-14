"""Build Crane.ico from the crane MOSAIC, cropped to the head.

    python tools/make_icon.py

WHY A HEADSHOT. Sangala Mosaic settled this for the family already: the turaco's full-figure crop
"read as a color blob at 48px, so head+body (beak/crest/eye legible) won". The crane's whole body
lost the same way — at icon size it was a gray stick. The crop here is the head assembly, measured
rather than eyeballed: crown, head, eye and wattle occupy exactly 64 x 64 points in
Images/Crane Mosaic.png (x 30-94, y 30-94), and the crop adds one tile of margin all round.

WHY THE MOSAIC AND NOT A RENDER. The icon of every application in the family is its species in the
house style, and Mosaic's is a tile mosaic. The crane mosaic already existed in the Mosaic project;
this reuses it rather than making a new picture. Glen, 2026-08-14: "you are not using all the
resources across the family."

There is no Pillow on this machine, so the sizes are rendered with PyMuPDF and the .ico container -
a directory of PNG-compressed entries, which Windows has accepted since Vista - is written by hand.
"""
import os
import struct
import sys

import fitz

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "Images", "Crane Mosaic.png")
OUT = os.path.join(HERE, "Crane.ico")

# WHAT IS IN FRAME. Measured off the mosaic rather than judged by eye: the crown, head, eye and
# wattle occupy y 24-94, the neck runs as a narrow column x 67-85 down to y 134, and the body opens
# out below that to x 162 by y 190. A head-only crop (the first attempt) is unmistakably a bird and
# not recognisably a CRANE - Glen: "you're too close to it". The frame therefore holds crown, head,
# wattle, the whole neck and the top of the body, and stops above the legs and the grass, which is
# what made the original full-figure icon a gray stick at 48 px.
CLIP = (20, 24, 170, 174)
SIZES = (256, 128, 64, 48, 32, 16)
# STUDIO'S BADGE SHAPE, measured from Sangala.ico's 256 px entry: its top row is transparent until
# x=39, so the corner radius is 39/256 - a fraction of the side, not a fixed number of pixels, so it
# holds at every size. The family's icons are rounded squares; a hard-edged one does not belong
# beside them.
RADIUS = 39.0 / 256.0


def round_corners(pm, size):
    """Return RGBA bytes with the corners cut to Studio's radius, edges antialiased.

    There is no Pillow here, so the mask is computed directly: coverage per pixel is sampled on a
    3 x 3 grid inside the pixel, which is enough to keep the arc smooth at 16 px.
    """
    r = RADIUS * size
    src = pm.samples
    out = bytearray(size * size * 4)
    centers = ((r, r), (size - r, r), (r, size - r), (size - r, size - r))
    for y in range(size):
        for x in range(size):
            cov = 0
            for sy in (0.17, 0.5, 0.83):
                for sx in (0.17, 0.5, 0.83):
                    px, py = x + sx, y + sy
                    inside = True
                    for cx, cy in centers:
                        # only the quadrant outside the arc's centre is tested against the circle
                        if ((px < cx) == (cx < size / 2)) and ((py < cy) == (cy < size / 2)):
                            if (px - cx) ** 2 + (py - cy) ** 2 > r * r:
                                inside = False
                            break
                    if inside:
                        cov += 1
            i, o = (y * pm.stride) + x * pm.n, (y * size + x) * 4
            out[o:o + 3] = src[i:i + 3]
            out[o + 3] = (cov * 255) // 9
    return bytes(out)


def render(size):
    d = fitz.open(SRC)
    span = CLIP[2] - CLIP[0]
    pm = d[0].get_pixmap(clip=fitz.Rect(*CLIP), matrix=fitz.Matrix(size / span, size / span))
    if pm.width != size or pm.height != size:
        # Rounding leaves a pixel over. An icon entry MUST be exactly square at its declared size,
        # so the pixmap is re-cropped in place - set_rect on a fresh one, since this build of
        # PyMuPDF will not construct a Pixmap from (Pixmap, IRect).
        pm.set_origin(0, 0)
        out = fitz.Pixmap(pm.colorspace, fitz.IRect(0, 0, size, size), pm.alpha)
        out.copy(pm, fitz.IRect(0, 0, size, size))
        pm = out
    rgba = round_corners(pm, size)
    return fitz.Pixmap(fitz.csRGB, size, size, rgba, True).tobytes("png")


def main():
    if not os.path.isfile(SRC):
        sys.exit("missing: %s" % SRC)
    pngs = [(s, render(s)) for s in SIZES]

    # ICONDIR, then one 16-byte ICONDIRENTRY per size, then the PNG payloads.
    offset = 6 + 16 * len(pngs)
    head = struct.pack("<HHH", 0, 1, len(pngs))
    entries, body = b"", b""
    for size, data in pngs:
        b = 0 if size == 256 else size               # 0 means 256 in an icon directory
        entries += struct.pack("<BBBBHHII", b, b, 0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)
    with open(OUT, "wb") as f:
        f.write(head + entries + body)

    print("wrote %s" % OUT)
    for size, data in pngs:
        print("   %3d x %-3d  %6d bytes" % (size, size, len(data)))
    print("%d bytes total" % os.path.getsize(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
