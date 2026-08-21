"""Rebuild Sections 2-9 of the Sangala Crane Kit in the Style Guide's form.

Reads one version, replaces everything from the "2. Body" heading to the end of the body
with sections built on Glen's Section 1 pattern - heading, bag lead-in, lettered steps,
centered picture strips with the step letter before each picture - and writes the next
version. Page 1 and Section 1 are left byte for byte as Glen made them.

Every paragraph form is CLONED from Section 1's own XML: the steps use the same
ListParagraph style and lettered numbering (each section gets its own numId with a start
override, or the letters would run on from Section 1), and the strips are the same
centered paragraph with the label run ahead of each inline picture, which is what sets
the letter at the picture's lower left.

Section 2 is reshaped on the way through. Its back-side plates sit directly behind the
front-side plates, so the flat view cannot show them - the pictures for those steps came
out pixel-identical to the front-side ones (verified against the original export). The
Style Guide's rule for the far-side eye applies: each back plate folds into the step that
places its front twin, and the section carries three pictures, not five.

    python kit_restyle_sections.py "<in.docx>" "<out.docx>"
"""
import os
import re
import sys
import zipfile

from PIL import Image

DOCS = r"D:\Code Projects\Block Tools\Documents"
PROCESSED = os.path.join(DOCS, "Assembly Images (processed)")

TNR = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
       '<w:sz w:val="22"/><w:szCs w:val="22"/>')
TNRB = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
        '<w:b/><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/>')
TNRI = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
        '<w:i/><w:iCs/><w:sz w:val="22"/><w:szCs w:val="22"/>')
EMU_IN = 914400


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(text, italic=False, bold=False):
    pr = TNRI if italic else (TNRB if bold else TNR)
    return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (pr, esc(text))


def runs(parts):
    return "".join(run(t, italic=bool(i)) for (t, i) in parts)


def heading(text):
    return ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="120"/>'
            '<w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (TNRB, run(text, bold=True)))


def lead(text):
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:after="120"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>'
            % (TNR, run(text)))


def step(numid, parts):
    return ('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/>'
            '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="%d"/></w:numPr>'
            '<w:spacing w:after="120"/><w:contextualSpacing w:val="0"/>'
            '<w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (numid, TNR, runs(parts)))


_docpr = [2000000000]


def picture(rid, cx, cy):
    _docpr[0] += 1
    n = _docpr[0]
    return ('<w:r><w:rPr><w:noProof/></w:rPr><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            '<wp:docPr id="%d" name="Picture %d"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
            '</wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:nvPicPr><pic:cNvPr id="%d" name=""/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
            % (cx, cy, n, n, n, rid, cx, cy))


def strip(entries, cap_in):
    """entries: list of (letter, rid, aspect). One centered paragraph, the letter ahead of
    each picture so it sits at the picture's lower left - Section 1's own arrangement.
    The height is shared by the whole strip: the widest fit under the cap, within 5.9 in of
    text width less a gap per picture."""
    total = sum(a for (_, _, a) in entries)
    cy_in = min(cap_in, (5.9 - 0.25 * len(entries)) / total)
    cy = round(cy_in * EMU_IN)
    out = ['<w:p><w:pPr><w:keepLines/><w:spacing w:after="180"/><w:jc w:val="center"/></w:pPr>']
    for k, (letter, rid, aspect) in enumerate(entries):
        if k:
            out.append(run("   "))
        out.append(run(letter + ". "))
        out.append(picture(rid, round(cy * aspect), cy))
    out.append("</w:p>")
    return "".join(out)


# ---------------------------------------------------------------- the eight sections
# label -> media rId in the kit package (imageN carries rId N+6)
RID = {"2a": "rId16", "2b": "rId17", "2d": "rId18",
       "3a": "rId19", "3b": "rId20", "3c": "rId21", "3d": "rId22", "3e": "rId23", "3f": "rId24",
       "4a": "rId25", "4b": "rId26", "4c": "rId27", "4d": "rId28", "4e": "rId29", "4f": "rId30",
       "5a": "rId31", "5b": "rId32", "5c": "rId33",
       "6a": "rId34", "6b": "rId35", "6c": "rId36",
       "7a": "rId37", "7b": "rId38",
       "8a": "rId39", "8b": "rId40", "8c": "rId41",
       "9a": "rId42", "9b": "rId43"}

I = True   # italic part name
SECTIONS = [
 dict(numid=2, title="2. Body",
      lead='Locate the bag of LEGO parts labeled \u201cBody.\u201d', cap=0.75,
      flow=[("s", [("Place two ", 0), ("Dark Gray 2 x 4 Side-Stud Bricks", I),
                   (" side by side to form the core of the body.", 0)]),
            ("s", [("Add a ", 0), ("Blue 2 x 4 Plate", I),
                   (" to the side studs on the front of the body. Then add the second "
                    "2 x 4 plate to the back in the same position.", 0)]),
            ("s", [("Add a ", 0), ("Yellow 2 x 3 Plate", I),
                   (" to the front of the body, over the blue plate. Then add the second "
                    "2 x 3 plate to the back.", 0)]),
            ("p", ["2a", "2b", "2d"]),
            ("s", [("The completed body should look like the image on the right (above).", 0)])]),
 dict(numid=3, title="3. Back",
      lead='Locate the bag of LEGO parts labeled \u201cBack.\u201d', cap=0.8,
      flow=[("s", [("Place the ", 0), ("Dark Gray 2 x 4 Brick", I), (" on top of the body.", 0)]),
            ("s", [("Place a pair of ", 0), ("Dark Gray 3 x 1 Sloped Bricks", I),
                   (", one in front of the other, at the tail.", 0)]),
            ("s", [("Add a second pair of 3 x 1 sloped bricks one step up the back.", 0)]),
            ("p", ["3a", "3b", "3c"]),
            ("s", [("Add a third pair of 3 x 1 sloped bricks to form the next step.", 0)]),
            ("s", [("Then add a pair of steeper ", 0), ("Dark Gray 2 x 1 Sloped Bricks", I),
                   (" at the top of the back, where the neck will stand.", 0)]),
            ("p", ["3d", "3e", "3f"]),
            ("s", [("The completed back should look like the image on the right (above).", 0)])]),
 dict(numid=4, title="4. Wings",
      lead='Locate the bag of LEGO parts labeled \u201cWings.\u201d', cap=0.8,
      flow=[("s", [("Place a ", 0), ("Light Gray 2 x 2 Sloped Brick", I),
                   (" at the upper root of the large ", 0), ("Light Gray Curved Wedge", I),
                   (" that forms the right wing.", 0)]),
            ("s", [("Add a second ", 0), ("Light Gray 2 x 2 Sloped Brick", I),
                   (" at the lower root.", 0)]),
            ("s", [("This completes the right wing, with all of its studs facing forward.", 0)]),
            ("p", ["4a", "4b", "4c"]),
            ("s", [("Assemble the left wing as a mirror image of the right wing, with all of its "
                    "studs facing away: place one sloped brick at the upper root of the second "
                    "wedge.", 0)]),
            ("s", [("Add the second sloped brick at the lower root.", 0)]),
            ("p", ["4d", "4e", "4f"]),
            ("s", [("The completed wings should look like the image on the right (above).", 0)])]),
 dict(numid=5, title="5. Wings on the Body",
      lead="Take the two wings assembled in Section 4.", cap=1.3,
      flow=[("s", [("Attach the right wing to the studs of the blue and yellow plates on the "
                    "front of the body, with the wing sweeping back toward the tail.", 0)]),
            ("s", [("Attach the left wing to the matching plates on the back of the body.", 0)]),
            ("p", ["5a", "5b", "5c"]),
            ("s", [("The attached wings should look like the image on the right (above).", 0)])]),
 dict(numid=6, title="6. Legs",
      lead='Locate the bag of LEGO parts labeled \u201cLegs.\u201d', cap=1.3,
      flow=[("s", [("Attach a ", 0), ("Black 1 x 1 x 3 Brick", I),
                   (" beneath the body to form the rear leg.", 0)]),
            ("s", [("Attach the second ", 0), ("Black 1 x 1 x 3 Brick", I),
                   (" beneath the body to form the front leg.", 0)]),
            ("p", ["6a", "6b", "6c"]),
            ("s", [("The completed legs should look like the image on the right (above).", 0)])]),
 dict(numid=7, title="7. Crane on the Baseplate",
      lead="Locate the green LEGO baseplate.", cap=1.3,
      flow=[("s", [("Place the ", 0), ("Green 8 x 16 Baseplate", I),
                   (" on the work surface and stand the crane on it, with the legs toward the "
                    "middle of the plate.", 0)]),
            ("p", ["7a", "7b"]),
            ("s", [("The crane on its baseplate should look like the image on the right "
                    "(above).", 0)])]),
 dict(numid=8, title="8. Neck",
      lead='Locate the bag of LEGO parts labeled \u201cNeck.\u201d', cap=1.3,
      flow=[("s", [("Attach the ", 0), ("Light Gray 1 x 2 Plate with Center Stud", I),
                   (" to the top of the body, in front of the sloped bricks of the back.", 0)]),
            ("s", [("Place the tall ", 0), ("Light Gray 1 x 1 x 5 Brick", I),
                   (" on the center stud to form the neck.", 0)]),
            ("p", ["8a", "8b", "8c"]),
            ("s", [("The completed neck should look like the image on the right (above).", 0)])]),
 dict(numid=9, title="9. Head on the Neck",
      lead="Take the head and crown assembled in Section 1.", cap=1.5,
      flow=[("s", [("Place the head and crown assembly on top of the neck, with the bill "
                    "pointing forward.", 0)]),
            ("p", ["9a", "9b"]),
            ("s", [("The completed crane should look like the image on the right (above).", 0)])]),
]


def trim(im, thr=210, frac=0.02):
    g = im.convert("L")
    bb = g.point(lambda v: 255 if v < thr else 0).getbbox()
    l, t, r, b = bb
    m = max(2, round(frac * max(r - l, b - t)))
    w, h = im.size
    return im.crop((max(0, l - m), max(0, t - m), min(w, r + m), min(h, b + m)))


def main(src, dst):
    aspect = {}
    for label in RID:
        with Image.open(os.path.join(PROCESSED, label + ".png")) as im:
            aspect[label] = im.size[0] / im.size[1]

    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    doc = zin.read("word/document.xml").decode("utf-8")
    num = zin.read("word/numbering.xml").decode("utf-8")

    for guard, why in [(">2. Body<", "the Section 2 heading"),
                       ("<w:sectPr", "the final section properties"),
                       ('w:numId w:val="1"', "Section 1's lettered list")]:
        if guard not in doc and guard not in num:
            raise SystemExit("refusing: cannot find " + why)
    if 'w:numId w:val="2"' in doc:
        raise SystemExit("refusing: numId 2 already exists - already restyled?")

    # ---- build the new sections. Picture k of a section carries letter k: the flows are
    # written so pictures map one to one onto the steps in order (a closing step's picture
    # arrives in the strip just before its sentence, and a step with no picture is last).
    body = []
    for s in SECTIONS:
        body.append(heading(s["title"]))
        body.append(lead(s["lead"]))
        nstep = 0
        npic = 0
        for kind, payload in s["flow"]:
            if kind == "s":
                nstep += 1
                body.append(step(s["numid"], payload))
            else:
                entries = []
                for lab in payload:
                    entries.append(("abcdefgh"[npic], RID[lab], aspect[lab]))
                    npic += 1
                body.append(strip(entries, s["cap"]))
    new_xml = "".join(body)

    cut0 = doc.rfind("<w:p ", 0, doc.index(">2. Body<"))
    cut1 = doc.rfind("<w:sectPr")
    doc = doc[:cut0] + new_xml + doc[cut1:]

    # ---- lettering restarts per section. NOT startOverride: eight numIds sharing one
    # abstract list, each with a startOverride, PRINTED wrongly - Section 5, whose list
    # straddled the page break, restarted at "a." on the page while ListFormat.ListString
    # still reported "c.". The object model and the printed page disagreed, and the page is
    # what the builder reads. Cloning the abstract list per section leaves Word no shared
    # state to resume: each section is its own list and can only start at "a".
    m = re.search(r'<w:abstractNum w:abstractNumId="0".*?</w:abstractNum>', num, re.S)
    if not m:
        raise SystemExit("refusing: cannot find abstract list 0 to clone")
    proto = m.group(0)
    clones = []
    for n in range(1, 9):
        c = proto.replace('w:abstractNumId="0"', 'w:abstractNumId="%d"' % n, 1)
        # nsid and tmpl identify a list definition; clones must not share them or Word may
        # treat the eight as one list again
        c = re.sub(r'(<w:nsid w:val=")([0-9A-Fa-f]{8})("/>)',
                   lambda k: k.group(1) + ("%08X" % ((int(k.group(2), 16) + n) & 0xFFFFFFFF)) + k.group(3), c)
        c = re.sub(r'(<w:tmpl w:val=")([0-9A-Fa-f]{8})("/>)',
                   lambda k: k.group(1) + ("%08X" % ((int(k.group(2), 16) + n) & 0xFFFFFFFF)) + k.group(3), c)
        clones.append(c)
    num = num.replace(proto, proto + "".join(clones), 1)
    add = "".join('<w:num w:numId="%d"><w:abstractNumId w:val="%d"/></w:num>' % (n, n - 1)
                  for n in range(2, 10))
    num = num.replace("</w:numbering>", add + "</w:numbering>")

    data = {n: zin.read(n) for n in names}
    zin.close()
    data["word/document.xml"] = doc.encode("utf-8")
    data["word/numbering.xml"] = num.encode("utf-8")

    order = ["[Content_Types].xml"] + [n for n in names if n != "[Content_Types].xml"]
    with zipfile.ZipFile(dst, "x", zipfile.ZIP_DEFLATED) as z:
        for n in order:
            z.writestr(n, data[n])
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
