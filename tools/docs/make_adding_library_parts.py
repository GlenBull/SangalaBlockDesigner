"""Build "Adding Library Parts" for the _Drafts folder.

A record of the 2026-08-27 investigation into letting a student add a part to their own
Sangala Blocks library by entering a number read off LEGO's Pick a Brick page. Written to
be shared with a collaborator, so it states what was measured, what was built, what broke,
and what is still unanswered.

    python tools\\docs\\make_adding_library_parts.py
"""
import sys

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

DRAFTS = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

d = Doc()
d.title("Adding Library Parts")

d.body("Sangala Blocks offers a fixed menu of LEGO parts, extended by parts library files prepared "
       "in advance. This note records an investigation into a different arrangement: a student "
       "finds a part on LEGO's Pick a Brick page, enters the number printed there, and that part "
       "joins a library of their own, which they can save and reopen. The same numbers order the "
       "physical parts once the design is finished. A working prototype exists; several defects and "
       "one pre-existing gap were found along the way, and some questions remain open.")

# ---------------------------------------------------------------- what existed
d.heading("What the Application Already Provided")

d.body("Three pieces of the workflow turned out to be in place already, which is why the prototype "
       "required no change to the program that runs behind the page.")

d.item("The library speaks in design numbers. ",
       "A part in a .library file is identified by a field named id, and that field already holds "
       "the LEGO design number: 3001 is the 2x4 brick, 4477 the 1x10 plate. The file format "
       "therefore already uses the number a student would read off the store page.")
d.item("The LDraw parts library is bundled. ",
       "The complete LDraw library, 24,591 part files, sits beside the application, carried there "
       "for the building-instruction work. Each part file declares its own name on its first line.")
d.item("The bridge already serves those files. ",
       "The page fetches part geometry through a route the bridge answers, and the response carries "
       "the file's full text. A part's name can therefore be read through the route that already "
       "existed, with no new data bundled into the page and no network access at all.")

d.body("A design number can therefore be turned into a library entry offline, with no account and no "
       "internet connection.")

# ---------------------------------------------------------------- the test
d.heading("Testing the Idea Before Building It")

d.body("The two libraries in the repository, Crane.library and Large Plates.library, hold 39 parts "
       "whose fields were established by hand. They were used as ground truth: each design number "
       "was looked up, its declared name parsed into the fields a library entry needs, and the "
       "result compared against the entry already recorded.", before_list=True)

d.body("All 39 numbers resolved. Thirty-eight reproduced the recorded entry exactly on kind, width, "
       "depth, height and shape. Two conventions had to be learned from the failures, and both are "
       "the kind of detail that is invisible until it is wrong.")

d.item("A retired number must be followed. ",
       "Several numbers answer with a redirection rather than geometry, for example 3040 to 3040b "
       "and 4073 to 6141. The retired number is exactly the one an older parts list carries, so it "
       "cannot simply be rejected.")
d.item("Name order differs by family. ",
       "A plate named 2 x 12 is two studs deep and twelve wide, but a slope's first number is the "
       "length of its ramp, which the library files record as the width. Reading a slope by the "
       "plate convention turns a 3 x 1 part into a 1 x 3 one.")

# ---------------------------------------------------------------- the prototype
d.heading("The Prototype")

d.body("The Library panel gained a Design Number box and an Add button, shown whenever the parts "
       "folder is reachable. The panel itself now appears before any library has been loaded; "
       "previously it stayed hidden until one arrived, which concealed the box from the student it "
       "was written for.")

d.body("Entering a number looks the part up, parses its declared name, and adds it to the library. "
       "The part joins the library whether or not the menu already offered that size, following the "
       "principle already established for library files: a library records what the student has, not "
       "what is new to the application. Behavior was confirmed in the running application.",
       before_list=True)

d.table(
    "Table 1. How Representative Design Numbers Resolve",
    ["Number entered", "Declared name", "Outcome"],
    [["3005", "Brick 1 x 1", "Added; the menu already offered that size"],
     ["3068b", "Tile 2 x 2 with Groove", "Added, bringing a new kind and its own menu button"],
     ["3040", "Slope Brick 45 2 x 1", "Redirection followed to 3040b, then added"],
     ["3626", "Minifig Head with Blocked Hollow Stud", "Refused by name"],
     ["44567", "Hinge Plate 1 x 2 Locking", "Refused by name"],
     ["9999999", "(no such part)", "Reported as not present in the parts folder"]],
    center_cols=(0,))

d.body("A library assembled this way saves through the existing Save command and reopens through "
       "the existing Open command. A full round trip was verified: three parts were added, saved, "
       "reopened in a fresh page, and saved again, producing a byte-identical file, with the tile "
       "kind restored on reload.")

# ---------------------------------------------------------------- limits
d.heading("Shapes the Application Cannot Represent")

d.body("Of the 24,591 parts in the folder, 5,203 parse into something Sangala Blocks can draw. The "
       "remainder are refused, and the refusal is correct rather than a shortfall: the largest "
       "groups are minifigures, stickers, Technic, electrical parts, Duplo, animals and train "
       "components, none of which has any representation in the application. A part that cannot be "
       "represented is named in the panel rather than approximated, because a wrong part in a real "
       "LEGO order arrives in a box some weeks later.")

d.body("That principle is not yet fully honored, and the exception matters. A curved part such as "
       "5841, declared as Brick 2 x 1 x 1 with Curved Top, is accepted and recorded as an ordinary "
       "rectangular brick. Its footprint and height are right and its curve is silently lost. This "
       "is not a hypothetical: the curved bow is required by the African buffalo figure, a "
       "collaborator has already added it to a library, and it did not draw correctly.")

d.body("A related defect was found and corrected. LDraw records fractional brick heights, writing a "
       "two-plate curved slope as 2 x 2 x 0.667. The first version of the parser read only the "
       "digits before the decimal point, producing a part zero plates tall. Three times the "
       "fractional value is exactly the height in plates, so 0.667 yields two and 1.333 yields four.")

# ---------------------------------------------------------------- ordering
d.heading("Ordering, and a Gap That Predates This Work")

d.body("A Pick a Brick order is uploaded as a two-column file of element identifiers and "
       "quantities. An element identifier names a shape and a color together, and it cannot be "
       "computed from a design number: it is a value LEGO assigns, and it must be looked up. The "
       "page carries a table of such identifiers, generated at build time from a published element "
       "list. Its scope is the parts the application can place, plus the parts named by libraries "
       "present in the repository when the table was last generated.")

d.body("That last clause is the gap. A library published after the table was generated is not "
       "covered. Seventeen of the eighteen parts in Large Plates.library have no element identifier "
       "today, so a design built from those plates would lose seventeen lines from its order file. "
       "The omission is reported rather than silent, but it is easily missed. This condition exists "
       "in the shipped application and is unrelated to the design-number feature, which only makes "
       "it easier to encounter.")

d.body("Widening the table was measured rather than estimated. Extending its scope to every part "
       "the application can represent yields 10,356 identifiers covering 1,363 parts, and adds "
       "roughly 215 kilobytes to a page currently near 491. All seventeen uncovered plates are "
       "recovered, most in all ten palette colors. The generator already exists and refuses to "
       "write a table that fails an acceptance test built from a real order, so this is a change of "
       "scope rather than of method. The residual risk is that it chooses among candidate "
       "identifiers by a rule validated across 44 parts, and would apply it across 1,363.")

# ---------------------------------------------------------------- direction
d.heading("Starting from the Store Rather than the Palette")

d.body("A coverage figure of 1,363 parts out of 5,203 understates the position, because it asks how "
       "many parts the application could offer are sold in the palette's ten colors. If the student "
       "begins at Pick a Brick instead, the part is purchasable by definition and the question "
       "largely dissolves.")

d.body("The guarantee holds for the part but not for the pairing of part and color, and an element "
       "identifier names the pairing. A student may find a brick offered in one color, enter its "
       "design number, and then color it from the palette into a combination that is not sold. The "
       "store page carries both numbers, plainly labeled, and the element identifier changes with "
       "the color chosen there. Accepting the element identifier would therefore carry the mould "
       "and the exact color in a single value, and would be orderable by construction. It resolves "
       "cleanly: element 6536123 gives part 5841 in the color LEGO names Earth Blue and the "
       "published list names Dark Blue, a difference of naming that the number itself avoids.")

d.body("Two matters would need settling first. The store offers far more colors than the ten in the "
       "palette, so an element identifier may resolve to a color the application cannot show. And "
       "an identifier that exists is not always a part currently in stock.")

# ---------------------------------------------------------------- geometry field
d.heading("A Field That Nothing Reads")

d.body("Library files carry a field named geometry, which names a different part file to take the "
       "shape from. It exists because a retired number's own file holds a redirection instead of "
       "geometry. No code in the page reads it: the renderer asks for the part's own number.")

d.body("Five numbers in the existing libraries are redirections. For those parts the request "
       "returns no geometry, and the application falls back to its built-in stand-in shape. For a "
       "slope the stand-in resembles a slope, so the substitution has never been visible. Honoring "
       "the geometry field would make those parts draw from their real shapes for the first time.")

d.body("This also corrects a fault introduced by the prototype. The established convention is that "
       "the number a student orders by is the one kept, and the redirection matters only when "
       "reading the shape. The prototype does the reverse, replacing the entered number with the "
       "redirected one, which removed it from the element table.")

# ---------------------------------------------------------------- open
d.heading("Questions Still Open")

d.body("The curved bow is the immediate one, because the buffalo figure depends on it and a student "
       "cannot be expected to construct a working entry by hand.", before_list=True)

d.step("What a correct entry for the curved bow contains. One has already been produced by hand, and "
       "it is the specification for what the resolver must generate.")
d.step("Which view was wrong. The plan view is drawn from the recorded shape, while the three "
       "dimensional view can draw real geometry, so knowing which failed narrows the cause.")
d.step("Whether curved parts should be accepted at all until they draw correctly, or refused by "
       "name in the way minifigures and hinges are.")
d.step("Whether the element identifier should be accepted as an alternative to the design number, "
       "and what the application should do with a color outside its palette.")
d.step("Whether the element table's scope should be widened, accepting a larger page and a rule "
       "applied more widely than it has been tested.")

print(d.save(DRAFTS, "Adding Library Parts"))
