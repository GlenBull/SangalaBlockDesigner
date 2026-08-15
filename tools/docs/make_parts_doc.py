"""The parts-library design, into Sangala Blocks' Documents folder."""
import os
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"D:\Code Projects\Block Tools\Documents"
os.makedirs(OUT, exist_ok=True)

d = Doc()
d.title("Adding LEGO Parts to Sangala Blocks")

d.body("Sangala Blocks plans a kit of real LEGO bricks, so every part it offers carries a real design "
       "number and a real footprint. Those facts already exist in the LDraw parts library, which sits "
       "beside the application, and the application derives its catalog from that library rather than "
       "from anything typed by hand. This document records the format that library uses, the form in "
       "which a collaborator should submit a list of parts, and the file that list becomes.")

# ---------------------------------------------------------------- the format
d.heading("What the LDraw Format Is")
d.body("Every part is one plain-text file named by its LEGO design number: 3005.dat is Brick 1 x 1. The "
       "local copy holds 24,591 of them. The first line of a file is the part's description, followed by "
       "header lines and then geometry. Each line is typed by the number it begins with.", before_list=True)

d.table(
    "Table 1. Line Types in an LDraw Part File",
    ["Type", "What It Carries", "Example"],
    [
        ["0", "A comment or a meta command: the description, Name, Author, LDRAW_ORG, LICENSE, BFC and "
              "HISTORY. A retired number redirects here, and the redirection must be followed",
         "0 ~Moved to 3023b"],
        ["1", "A reference to another file, with a 3 x 4 transform in row-major order. Parts are built "
              "from shared sub-files rather than repeating geometry",
         "1 16 0 0 0 1 0 0 0 1 0 0 0 1 s\\3005s01.dat"],
        ["2", "A line, as two points", "2 24 -10 0 -10 10 0 -10"],
        ["3", "A triangle, as three points", "3 16 x y z x y z x y z"],
        ["4", "A quadrilateral, as four points", "4 16 -10 24 -10 10 24 -10 10 0 -10 -10 0 -10"],
        ["5", "An optional line, drawn only at a silhouette edge", "5 24 x y z x y z x y z x y z"],
    ],
    weights=[8, 62, 30], center_cols=(0,))

d.body("Color is not held in the part. The code 16 means \"inherit from whatever placed this\", and the "
       "palette itself is a separate file, LDConfig.ldr, one line per color: "
       "0 !COLOUR Black CODE 0 VALUE #1B2A34 EDGE #808080. A model or an assembly uses the same grammar "
       "in a .ldr or .mpd file, one type-1 line for each brick placed, with 0 STEP marking the steps of "
       "a set of instructions.")
d.body("The measurements matter as much as the grammar. One LDraw unit is 0.4 mm; a stud is 20 units, "
       "which is the 8 mm pitch Sangala Blocks already snaps to; a plate is 8 units and a brick 24. The "
       "Y axis points DOWN, so a part's origin sits at the top of its body rather than the bottom.")

# ---------------------------------------------------------------- the submission
d.heading("The Form a List Should Be Sent In")
d.body("A plain text file, one part to a line: the design number, then a quantity and a color if they "
       "are known. Nothing else.", before_list=True)
d.listing("3001, 12, red\n3003, 8, yellow\n3623, 20\n3040")
d.body("Dimensions and descriptions are deliberately excluded. Both are already in the library, and "
       "entering them a second time creates a second copy that will drift from the first. Where a part "
       "is known by sight rather than by number, its description may be written instead — Slope Brick 45 "
       "2 x 1 — and the builder reports what it matched so the match can be confirmed before the library "
       "is written.")
d.body("Quantities are optional and decide what the list means: included, it is an inventory of bricks "
       "physically in hand and a design's parts list can be checked against it; omitted, it is simply the "
       "set of shapes the application should offer.")

# ---------------------------------------------------------------- derivation
d.heading("What Is Derived Rather Than Typed")
d.body("tools\\ldparts.py resolves each number against the library, follows a retired number to its "
       "replacement, and measures the part. Run against three of the lines above it reports:", before_list=True)
d.listing("3001          Brick  2 x  4              4.00 x 2.00 studs    3.5 plates\n"
          "3623          Plate  1 x  3              3.00 x 1.00 studs    1.5 plates\n"
          "3040 -> 3040b Slope Brick 45  2 x  1     1.00 x 2.00 studs    3.5 plates")
d.body("Two details in that output are worth naming. The number 3040 is retired and answers as 3040b, "
       "which is why a number is resolved rather than trusted. And the height includes the stud: a brick "
       "is three plates of body and half a plate of stud. The library builder records the body and the "
       "stud separately, which is the convention the application's own size table already follows.")

# ---------------------------------------------------------------- the file
d.heading("The Library File")
d.body("The list becomes a .parts file: JSON, in the same shape as the .block file the application "
       "already writes, so it is readable, comparable in a version history, and needs no new machinery.",
       before_list=True)
d.listing('{ "sangala": "parts", "version": 1,\n'
          '  "parts": [ { "id": "3001", "name": "Brick 2 x 4", "kind": "brick",\n'
          '               "w": 4, "d": 2, "h": 3, "shape": "box",\n'
          '               "color": "red", "qty": 12 } ] }')

d.table(
    "Table 2. Where Each Field Comes From",
    ["Field", "Source"],
    [
        ["id", "The design number as submitted, resolved through any redirection"],
        ["name", "The part file's first line"],
        ["kind", "Classified from the description: brick, plate, slope, inverted slope"],
        ["w, d", "Measured footprint in studs"],
        ["h", "Measured body height in plates, the stud excluded"],
        ["shape", "Classified from the geometry: box, wedge, round"],
        ["color", "From the submitted list, matched against LDConfig.ldr"],
        ["qty", "From the submitted list, and absent when no quantity was given"],
    ],
    weights=[16, 84])

d.body("Every field except color and quantity comes out of LDraw. The builder does not guess: a line it "
       "cannot resolve is reported and left out, so a mistyped number appears as a line to correct rather "
       "than as a part that does not exist.")

# ---------------------------------------------------------------- import
d.heading("How a Library Is Imported")
d.body("The Open button already routes by file extension — a .model brings in a frame from Sangala "
       "Studio and a .block opens a design — so .parts becomes a third case. A library ADDS to the parts "
       "menu rather than replacing it, so a student can hold more than one. A design saved afterwards "
       "records which library it was built from, so a .block opened on another machine can say what it "
       "needs rather than failing silently.")

d.heading("What Remains to Be Built")
d.body("Two pieces, neither of them large.", before_list=True)
d.step("tools\\parts_library.py, a companion to ldparts.py, which reads the submitted list and writes "
       "the .parts file, reporting whatever it could not resolve.")
d.step("The import itself in SangalaBlockDesigner.html: the extension added to the Open button's accept "
       "list, and the parts menu extended from the loaded library.")

print(d.save(OUT, "Adding LEGO Blocks"))
