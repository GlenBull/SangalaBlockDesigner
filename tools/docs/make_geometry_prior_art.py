"""Part Geometry in Other Brick Programs - the survey document, into _Drafts.

Written 2026-08-28 to answer a question Glen put directly: rather than reinventing the wheel,
find out whether the difficulties Sangala Blocks has drawing a part correctly have already been
solved in another program. Every claim below traces to a specification, a source file or a data
file that was actually read; the section "What Was Not Established" carries the residue.

House formatting comes from makedocx, imported from Sangala Studio's tools so the three
applications' documents cannot drift into three formats.
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

d = Doc()
d.title("Part Geometry in Other Brick Programs")

d.body("Sangala Blocks reads its part geometry from the LDraw parts library, and a part added by its "
       "LEGO design number has its footprint worked out from the words in the part's declared name. "
       "That last step has failed in practice: two parts of the same shape, named by different "
       "catalogs, resolve to different footprints, and one of them is laid down turned the wrong way. "
       "Before another naming rule is added, this document records what other brick programs do about "
       "the same problem. They have solved it, several times, and not one of them solves it by reading "
       "the name.")

# ------------------------------------------------------------------ measurement
d.heading("Measuring the Mesh: LeoCAD")

d.body("LeoCAD is an open-source brick CAD program whose source was read directly rather than its "
       "documentation, because the two disagree. It never parses a part's description. The description "
       "is copied verbatim from the part file's first line and used only for display, search and "
       "sorting; there is no numeric parsing of it anywhere in the parts library or piece code.")

d.body("A part's size comes from its vertices. The routine that computes it walks every level of "
       "detail and every section of the mesh, takes a minimum and maximum over the vertex positions, "
       "and then folds a section into the part's own extent only when that section is triangles:",
       before_list=True)

d.listing("if (Section.PrimitiveType == LC_MESH_TRIANGLES ||\n"
          "    Section.PrimitiveType == LC_MESH_TEXTURED_TRIANGLES)\n"
          "{\n"
          "    UpdatedBoundingBox = true;\n"
          "    MeshMin = lcMin(SectionMin, MeshMin);\n"
          "    MeshMax = lcMax(SectionMax, MeshMax);\n"
          "}")

d.body("Line and conditional-line sections still receive bounding boxes of their own, but are "
       "deliberately excluded from the part's extent. Edges do not determine how large a part is.")

d.body("The degenerate case is handled explicitly. When no triangle section is found at all, the "
       "minimum and maximum are both set to the origin rather than being left at their sentinel "
       "values. That yields a zero-extent box, which is an unambiguous and testable signal that a "
       "part carries no geometry - precisely the condition that arises when a part file is absent.")

d.body("The measurement is taken once and then cached. The computed box is copied onto the piece "
       "record when its mesh is set, and the mesh serializer writes the minimum, the maximum and a "
       "radius into the disk cache immediately after the mesh flags, reading them back on load. "
       "Everything downstream - ray picking, frustum culling, the part preview's zoom to extents, "
       "and whole-model extents - consults that one box.")

# ------------------------------------------------------------------ the guarantee
d.heading("What the LDraw Specification Guarantees")

d.body("Measurement is safer than it first appears, because the axes and the origin are mandated "
       "rather than incidental. The official parts library specification requires of every "
       "stud-bearing part that", before_list=True)

d.listing("parts that have studs should be oriented such that the top studs\n"
          "point up (-y) and the bottom tubes point down (+y)")

d.body("and, of the origin,", before_list=True)

d.listing("the origin of the parts will be the centered on the top most stud\n"
          "group. The bottom of studs should lie on the x-z plane")

d.body("A measured bounding box therefore arrives in a known frame, which is what makes the "
       "conversion of twenty units to a stud and eight to a plate reliable rather than fortunate.")

d.body("One caution, recorded because it is easy to misread. The specification does contain a rule "
       "that dimensions are given in studs and in the order [z-dimension] x [x-dimension], but that "
       "rule appears in the section governing stickers, not as a general rule for all parts. It does "
       "not settle the ordering dispute between bricks and slopes.")

# ------------------------------------------------------------------ studs by name
d.heading("Identifying Studs by Primitive Name")

d.body("A bounding box gives extent but not which stud positions a part occupies. The LDraw community "
       "answers that separately, and treats it as routine. The wiki states it plainly:", before_list=True)

d.listing("Software which renders a part can easily identify studs at runtime,\n"
          "simply by their filename as a primitive: stud.dat.")

d.body("The named primitives are stud.dat, the hollow stud2.dat, and the -logo, -logo2 through "
       "-logo5 and -high-contrast variants of each. Because every one of these appears as a type-1 "
       "subfile line carrying its own transform matrix, scanning for them yields three facts at "
       "once: whether the part has studs at all, how many, and where each sits. That is the footprint "
       "expressed directly in stud positions, rather than an extent in LDraw units that must "
       "afterwards be divided and rounded. Stud presence is a fact a part's name does not record.")

# ------------------------------------------------------------------ naming
d.heading("Where a Naming Convention Is Actually Written Down")

d.body("The convention Sangala Blocks reverse-engineered turns out to be real and published. "
       "BrickLink's standard states that dimensions are given as width by length by height, counted "
       "in studs and in bricks, and then adds an explicit exception:", before_list=True)

d.listing("For Slopes, the first dimension listed should be that of the\n"
          "direction of the slope. For example, the dimensions for part\n"
          "4286 are 3 x 1, not 1 x 3.")

d.body("So the swap rule applied to slopes is not a hack. It is one catalog's documented habit. The "
       "same page concedes that the width-by-length order \"may be replaced on occasion with the more "
       "widely used standard Length x Width x Height\", and the catalogs disagree with one another in "
       "practice. The part LDraw calls Slope Brick Curved 3 x 1 is Brick with Bow 1 x 3 elsewhere, and "
       "LEGO's own design database names it BRICK W/BOW 1/3. Three catalogs, three orders. A rule for "
       "reading dimensions out of a name is a rule about one catalog, and each further family that "
       "names things differently requires another exception.")

# ------------------------------------------------------------------ LDD
d.heading("Mapping the Studs: LEGO Digital Designer")

d.body("LEGO's own program maps every part's studs onto an explicit grid. Each part primitive carries "
       "a connectivity block holding one or more two-dimensional fields. The community specification "
       "of the format states the governing design decision:", before_list=True)

d.listing("The height and width attributes are always double the number of\n"
          "studs. The contained text is a 2D array that is always height+1\n"
          "and width+1 ... This is done to keep information between and\n"
          "around the studs.")

d.body("The grid therefore runs at half-stud resolution, on purpose, because a bottom tube sits "
       "between four studs rather than on one. A field of type 23 describes the male face, a field of "
       "type 22 the female face. The cells are type codes: 0 is a stud, 7 a bottom tube, 15 an "
       "anti-stud, 18 the space between four studs, 22 a wall, 23 the space between two side-by-side "
       "studs, 29 no connection. A 1 x 1 plate carries its own code, 17, because it has no tube.")

d.body("The top field of a 4 x 4 plate reads as follows, and the indexing was checked against the "
       "code table rather than assumed: studs fall at odd row and odd column, the space between four "
       "studs at even interior positions, and corners and edges take their own codes.", before_list=True)

d.listing("18:1:1,23:4:1,18:2:1,23:4:1,18:2:1,23:4:1,18:2:1,23:4:1,18:1:1,\n"
          "23:4:1, 0:4:1,23:4:1, 0:4:1,23:4:1, 0:4:1,23:4:1, 0:4:1,23:4:1,\n"
          "18:2:1,23:4:1,18:4:1,23:4:1,18:4:1,23:4:1,18:4:1,23:4:1,18:2:1,\n"
          "...")

d.body("Its female field is the exact complement, with anti-studs at odd and odd, and the nine bottom "
       "tubes a 4 x 4 plate really has at the nine even interior cells.")

d.body("Two further pieces of per-part data are recorded alongside, and both bear on questions "
       "Sangala Blocks has open. A collision block decomposes the part into a list of oriented boxes "
       "- a minifigure wig examined for this survey has fifteen - which is how an irregular or curved "
       "shape is given a usable solid form without a single box misrepresenting it. And a logical "
       "bounding volume is recorded separately from a geometric one, as different numbers, which is "
       "the same distinction the parts libraries already make explicit for a part that overhangs what "
       "it rests on.")

# ------------------------------------------------------------------ Studio, LDCad
d.heading("Mapping the Studs: BrickLink Studio and LDCad")

d.body("Every part in BrickLink Studio has a connection information file, one per part number, in the "
       "connectivity folder of the installation. A part lacking one can be given one in the Part "
       "Designer and submitted to a community parts repository. Gabriel Läufer reverse-engineered the "
       "format by extracting the same data from the human-readable part files: each record carries a "
       "group identifier, an element identifier, a three-by-three matrix, a position, two lateral "
       "dimensions and a geometry specification, over roughly forty-three connectivity element types. "
       "The exported file is binary and expressed in LDraw units; the internal part file is text and "
       "expressed in studs.")

d.body("LDCad takes a third approach: a declarative grid parameter on a snap meta. A stud array is "
       "one line, with counts on each axis, a step in LDraw units, and an optional flag to center the "
       "array on the meta's own position.", before_list=True)

d.listing("[grid=Xcnt Zcnt Xstep Zstep]        e.g.  [grid=C 4 C 8 20 20]")

d.body("These metas are distributed as a shadow library - a set of files mirroring the official parts "
       "library structure, so that loading a part also loads its metadata from the matching shadow "
       "file. The arrangement is documented, but the specification behind it is marked unofficial and "
       "unratified, and the shadow library itself covers a growing subset of official parts rather "
       "than all of them.")

# ------------------------------------------------------------------ JBrickBuilder
d.heading("Deriving the Connections: JBrickBuilder")

d.body("One program generates its connectivity from LDraw geometry rather than obtaining a curated "
       "database, and it is the closest match to what Sangala Blocks needs. JBrickBuilder, written in "
       "Java by Mario Pascucci and released under the GNU General Public License version 3, is "
       "unmaintained since October 2015 but complete and readable. Its author states the design in "
       "one sentence: adding a connection type and an autodetect strategy using LDraw primitives does "
       "not require changing program code, only a configuration file.")

d.body("The source bears this out. A map described in its own comment as mapping a primitive to a "
       "connection placement is filled from an autodetect definitions file whose schema names an "
       "LDraw primitive and lists the connection points that primitive implies, each as a base point "
       "and a head point:", before_list=True)

d.listing("<autodetect>\n"
          "  <primitive checkdup=\"1\">\n"
          "    <name p=\"...\" />\n"
          "    <cp type=\"...\" bx=\"\" by=\"\" bz=\"\" hx=\"\" hy=\"\" hz=\"\" />\n"
          "  </primitive>\n"
          "</autodetect>")

d.body("Any part referencing that primitive then acquires those connection points automatically. A "
       "new family of parts is a data edit, not a code change - which is the property that removes a "
       "class of faults rather than one instance of it.")

d.body("Where autodetection is insufficient there is a hand-authored override database of 585 "
       "per-part files, and it contains the curved bow the African buffalo requires. Its entry, read "
       "against the 1 x 1 brick's entry in the same database, settles by measurement the question the "
       "name parser answered wrongly:", before_list=True)

d.listing("<!--Part: 50950.dat  Description: Slope Brick Curved  3 x  1-->\n"
          "<connections>\n"
          "  <cpoint type=\"R_STUD\"><base x=\"0.0\" y=\"16.0\" z=\"20.0\"/></cpoint>\n"
          "  <cpoint type=\"R_STUD\"><base x=\"0.0\" y=\"24.0\" z=\"0.0\"/></cpoint>\n"
          "  <cpoint type=\"R_STUD\"><base x=\"0.0\" y=\"24.0\" z=\"-20.0\"/></cpoint>\n"
          "  <cpoint type=\"R_STUD\"><base x=\"0.0\" y=\"24.0\" z=\"-10.0\"/></cpoint>\n"
          "</connections>")

d.body("A 1 x 1 brick in the same database has one stud at the top, at y=0, and one receptacle at the "
       "bottom, at y=24. Reading 50950 against that: the part is one stud wide along x and runs three "
       "stud pitches along z, has no studs on its upper face at all, and carries a receptacle at a "
       "half-pitch position. The name's leading 3 is the run of the curve, exactly as BrickLink's "
       "slope rule says - but here it is a measured coordinate rather than a word.")

d.body("Two limits belong beside this. The license is the GNU General Public License version 3, which "
       "has consequences for any code taken rather than merely studied. And the 585 override files are "
       "not a complete library: the 1 x 1 brick is present and the 2 x 4 brick is not, so the set "
       "cannot be characterized as exactly those parts on which autodetection failed.")

# ------------------------------------------------------------------ closed
d.heading("Solved, but Not Inspectable")

d.body("Three further programs solve part of the same problem behind closed doors, and are recorded "
       "here so the survey is not mistaken for exhaustive.", before_list=True)

d.item("Mecabricks. ", "A browser-based builder by Nicolas Jarraud with its own part library, "
       "distinct from both LDraw and LEGO's, and its own snap points. No public documentation of the "
       "underlying format was found.")
d.item("Bricker. ", "A commercial Blender add-on that builds brick models from arbitrary meshes on a "
       "stud grid, with a constraint that restricts the result to real brick sizes. It solves the "
       "opposite direction - mesh to bricks rather than part to footprint.")
d.item("BrickGPT and LegoGPT. ", "Academic work from Carnegie Mellon that represents each brick as a "
       "height, a width and a position on a stud grid and emits LDraw. Open, but built on a small "
       "fixed vocabulary of bricks; it shows how to represent a stud grid, not how to derive one from "
       "an arbitrary part.", after=100)

# ------------------------------------------------------------------ missing parts
d.heading("What Others Do About a Part They Cannot Find")

d.body("Sangala Blocks substitutes a hand-drawn stand-in for a part it cannot read, silently. That "
       "silence cost a collaborator an hour of building a part by hand that was already described "
       "exactly in a file the application could not reach. Both behaviors have precedents, and the "
       "precedents differ from the current one in a single respect.")

d.body("LDView, by default, attempts to download a part it cannot find from the LDraw.org parts "
       "tracker, and generates a warning whenever it uses an unofficial file obtained that way. The "
       "fetch is the same mechanism Sangala Blocks now ships; the warning is not.")

d.body("LeoCAD substitutes as well. Its placeholder builds a hardcoded box measuring twenty by twenty "
       "by twenty-eight LDraw units, which is exactly a 1 x 1 brick and its stud. The difference is "
       "one line: the piece is marked as a placeholder type, and the rest of the program can ask "
       "whether it is one. The substitution is tagged rather than silent.")

# ------------------------------------------------------------------ summary
d.heading("The Two Strategies")

d.table(
    "Table 1. How Each Program Determines What a Part Occupies",
    ["Program", "Method", "Open"],
    [
        ["LeoCAD", "Bounding box measured from triangle vertices, cached to disk. No stud grid; "
                   "snapping uses fixed grid values", "Yes, GPL 2"],
        ["LEGO Digital Designer", "Authored half-stud grid per part, separate male and female fields, "
                                  "plus a collision decomposition into oriented boxes", "No"],
        ["BrickLink Studio", "Authored connection file per part number, community-extensible through "
                             "a parts repository", "Partly"],
        ["LDCad", "Authored snap metas with a declarative stud-array grid, distributed as a shadow "
                  "library mirroring the parts library", "Yes, unratified"],
        ["JBrickBuilder", "Derived from LDraw primitives through a configuration file, with a "
                          "hand-authored override database for the residue", "Yes, GPL 3"],
        ["Sangala Blocks", "Footprint read from the words of the part's declared name", "Yes"],
    ],
    weights=[22, 62, 16])

d.body("Every program that has solved this took one of two routes. The first is to author a per-part "
       "database: correct and complete for what it covers, but it requires a maintainer, its coverage "
       "is always partial, and in two of three cases the data belongs to someone else. The second is "
       "to derive the answer from the primitives a part already references, keeping a hand-authored "
       "override for what derivation cannot reach. Only one program took the second route, and it is "
       "the route available to Sangala Blocks, because it needs no licensed dataset and no maintainer, "
       "and it degrades to the same override mechanism where it fails.")

d.body("A related utility by the same author converts part numbers between LEGO's design "
       "identifiers, LDraw's and BrickLink's. That is the cross-catalog problem the element "
       "identifier work runs into, already solved and readable.")

# ------------------------------------------------------------------ not established
d.heading("What Was Not Established")

d.body("Four things were left open rather than filled in.", before_list=True)

d.item("The second grid on the curved bow. ", "LEGO's entry for 50950 carries two fields at different "
       "heights and offsets rather than one. Why the middle row holds three consecutive anti-stud "
       "cells where the odd-and-even rule predicts two was not decoded.")
d.item("Automatic stud detection in LDCad. ", "A forum exchange with its author states that top studs "
       "inherit from the stud primitive without explicit definition. The meta reference page does not "
       "document any such behavior, and it was not confirmed in code.")
d.item("The completeness of the override database. ", "585 files were read, but not the criterion by "
       "which a part enters that set.")
d.item("The cost of building a stud map. ", "Deriving a per-part grid from LDraw geometry is a larger "
       "piece of work than changing the resolver, and it was not costed.", after=100)

# ------------------------------------------------------------------ sources
d.heading("Sources")

d.table(
    "Table 2. Where Each Claim Was Read",
    ["Claim", "Source"],
    [
        ["Orientation and origin rules; the sticker dimension order",
         "LDraw.org Official Parts Library Specifications"],
        ["Studs identified at runtime by primitive filename",
         "LDraw.org wiki, Studs with Logos"],
        ["Slope dimension order; width by length by height",
         "BrickLink, Item Dimensions"],
        ["Bounding box from triangle vertices; the tagged placeholder",
         "leozide/leocad, common/lc_meshloader.cpp and common/pieceinf.cpp"],
        ["The half-stud grid and its type codes",
         "sttng/LDD, doc/Custom2DField.md, with part primitives read from a community mirror"],
        ["Connection files per part; the reverse-engineered record layout",
         "LDraw.org forums, File Format for the Studio Connectivity Files"],
        ["The snap metas, the grid parameter and the shadow library",
         "melkert.net, LDCad technical pages; LDraw.org wiki, Part Snapping Language Extension"],
        ["Autodetection from primitives; the override database and 50950",
         "Bricksnspace/ldrawlib and Bricksnspace/brickDB"],
        ["Fetching and warning on an unofficial part",
         "LDView documentation"],
    ],
    weights=[52, 48])

print(d.save(OUT, "Part Geometry in Other Brick Programs"))
