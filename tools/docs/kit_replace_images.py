"""Swap the Sangala Crane Kit's assembly pictures for the processed (trimmed) set.

Reads one version of the document, replaces the bytes of the 33 assembly media files with
the images in Documents\\Assembly Images (processed), rewrites each placement's display
width to the new picture's proportions - the HEIGHT is kept, so the strip heights Glen set
survive - and writes the next version. The text is not touched. The four provenance
pictures on page 1 are not touched.

    python kit_replace_images.py "<in.docx>" "<out.docx>"

The mapping below is the document order of the 35 assembly placements, established by
reading Ver 1.0: placements 5-39 carry the step pictures; 2.b/2.c share one media file and
2.d/2.e share another (so 33 files serve 35 placements).
"""
import os
import re
import sys
import zipfile

from PIL import Image

PROCESSED = r"D:\Code Projects\Block Tools\Documents\Assembly Images (processed)"

# placement order 5..39 -> step label
PLACEMENTS = ["1a","1b","1c","1d","1e",
              "2a","2b","2c","2d","2e",
              "3a","3b","3c","3d","3e","3f",
              "4a","4b","4c","4d","4e","4f",
              "5a","5b","5c",
              "6a","6b","6c",
              "7a","7b",
              "8a","8b","8c",
              "9a","9b"]

# media file -> the processed image whose bytes it takes (2c and 2e ride along on 2b/2d)
MEDIA = {"image5":"1a","image6":"1b","image7":"1c","image8":"1d","image9":"1e",
         "image10":"2a","image11":"2b","image12":"2d",
         "image13":"3a","image14":"3b","image15":"3c","image16":"3d","image17":"3e","image18":"3f",
         "image19":"4a","image20":"4b","image21":"4c","image22":"4d","image23":"4e","image24":"4f",
         "image25":"5a","image26":"5b","image27":"5c",
         "image28":"6a","image29":"6b","image30":"6c",
         "image31":"7a","image32":"7b",
         "image33":"8a","image34":"8b","image35":"8c",
         "image36":"9a","image37":"9b"}


def main(src, dst):
    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    doc = zin.read("word/document.xml").decode("utf-8")

    sizes = {}
    for label in PLACEMENTS:
        with Image.open(os.path.join(PROCESSED, label + ".png")) as im:
            sizes[label] = im.size

    # Walk the drawings in document order. The first four are the provenance pictures and
    # keep their extents; each of the rest takes the width its new picture's proportions
    # demand at its existing height.
    blocks = list(re.finditer(r"<w:drawing>.*?</w:drawing>", doc, re.S))
    if len(blocks) != 4 + len(PLACEMENTS):
        raise SystemExit("expected %d drawings, found %d - the document has changed shape"
                         % (4 + len(PLACEMENTS), len(blocks)))

    out, last = [], 0
    for i, m in enumerate(blocks):
        out.append(doc[last:m.start()])
        block = m.group(0)
        if i >= 4:
            label = PLACEMENTS[i - 4]
            w, h = sizes[label]

            def resize(match):
                cy = int(match.group(3))
                cx = round(cy * w / h)
                return match.group(1) + str(cx) + match.group(2) + str(cy) + match.group(4)

            block, n1 = re.subn(r'(<wp:extent cx=")\d+(" cy=")(\d+)("/>)', resize, block)
            block, n2 = re.subn(r'(<a:ext cx=")\d+(" cy=")(\d+)("/>)', resize, block)
            if n1 != 1 or n2 != 1:
                raise SystemExit("placement %s: expected one wp:extent and one a:ext, found %d and %d"
                                 % (label, n1, n2))
        out.append(block)
        last = m.end()
    out.append(doc[last:])
    doc = "".join(out)

    data = {n: zin.read(n) for n in names}
    zin.close()
    data["word/document.xml"] = doc.encode("utf-8")
    for media, label in MEDIA.items():
        part = "word/media/" + media + ".png"
        if part not in data:
            raise SystemExit("missing media part " + part)
        with open(os.path.join(PROCESSED, label + ".png"), "rb") as f:
            data[part] = f.read()

    order = ["[Content_Types].xml"] + [n for n in names if n != "[Content_Types].xml"]
    with zipfile.ZipFile(dst, "x", zipfile.ZIP_DEFLATED) as z:
        for n in order:
            z.writestr(n, data[n])
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
