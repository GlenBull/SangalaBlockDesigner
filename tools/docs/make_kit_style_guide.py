"""LEGO Kit Style Guide — the script the document is built from.

Codifies the form of a LEGO kit assembly document, as established by Glen's Section 1 of
Sangala Crane Kit (Ver 1.0). Formatting comes from Sangala Studio's makedocx, imported
rather than copied, so the three applications' documents keep one format.
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"D:\Code Projects\Block Tools\Documents"

d = Doc()
d.title("LEGO Kit Style Guide")

d.body("A LEGO kit document tells a builder how to assemble a figure from the bagged parts "
       "in front of them. It is not a description of a design and not a record of how the "
       "design was made: every sentence exists to get one part into one place. This guide "
       "sets the form such a document takes, so that a kit for any figure reads the same way "
       "as a kit for any other.")

d.heading("The Opening Pages")
d.body("A kit document opens with the title of the kit, the names of those who made it, and "
       "a short account of where the figure came from — the photograph, the mosaic, the "
       "three-dimensional projection, the printed figure, and the design in bricks. Pictures "
       "of those stages carry the account, and the reader meets the finished figure before "
       "being asked to build it.")
d.body("The opening also says how the parts are divided. A kit arrives as bags, one per "
       "element of the figure, and naming them here prepares the reader for the lead-in "
       "sentence that opens every section.")
d.body([("The names of the applications and of the kit itself are set in italic: ", False, False),
        ("Sangala Mosaic", True, False), (", ", False, False),
        ("Sangala Studio", True, False), (", ", False, False),
        ("Sangala Blocks", True, False),
        (", and the name of the kit.", False, False)])

d.heading("Sections and Their Headings")
d.body("The assembly is divided into numbered sections, one per element of the figure, in "
       "the order the builder works. A heading is a number and a short noun phrase naming "
       "the element — 1. Head and Crown, 2. Body — not a sentence and not an instruction. "
       "Each word is capitalized except the minor ones.")
d.body("Sections run in build order, and a sub-assembly is assembled before it is attached. "
       "An element assembled away from the figure and joined to it later takes two sections: "
       "one to build it, one to attach it.")

d.heading("The Bag Lead-In")
d.body("Every section opens with one sentence directing the builder to the parts: "
       "Locate the bag of LEGO parts labeled \u201cHead and Crown.\u201d The sentence names the "
       "bag exactly as the bag is labeled. This line is what makes the document a kit rather "
       "than a description, and no section omits it.")

d.heading("The Steps")
d.body("The steps of a section are a lettered list — a, b, c — one step to a line. A step is "
       "a single action in the imperative: it names the part and says where the part goes. "
       "Steps are not run together into a paragraph; a builder holds their place in a list "
       "and loses it in prose.")
d.body("A step says where a part sits relative to parts already placed, in words a builder "
       "can act on without measuring. Left and right are given from the reader's view of the "
       "figure as the pictures show it.")

d.heading("Naming the Parts")
d.body("A part is named in italic, with each word capitalized, at the size and shape the "
       "builder must pick out of the bag:")
d.item("Black 1 x 3 Plate. ", "Color, then dimensions, then the kind of part.")
d.item("White 1 x 1 Round Plate. ", "The shape qualifies the kind.")
d.item("Red Sloped Brick. ",
       "Where a dimension does not help the builder tell one part from another, a plain "
       "description serves.")
d.body("Dimensions are written with spaces around the multiplication sign: 1 x 3, not 1x3. "
       "A part named a second time within the same section may be written plainly, without "
       "italic, once there is no doubt which part is meant.")
d.body("A brick carrying studs on its side is a side-stud brick. The collectors' abbreviation "
       "for it is never used: these documents are read by children.")

d.heading("The Pictures")
d.body([("Pictures are made with the Snapshot feature of ", False, False),
        ("Sangala Blocks", True, False),
        (", using its Plan View option, so that the picture is a drawing of the design itself "
         "rather than a photograph of a screen. A plan snapshot is cropped to the build and is "
         "independent of the window's zoom, so pictures taken at different times sit together "
         "consistently.", False, False)])
d.body("Pictures are laid out in strips: three to five across a line, about one inch tall, "
       "placed after the steps they illustrate rather than between them. A strip keeps a "
       "section on one page and lets the builder compare one stage against the next at a "
       "glance. All pictures in a strip are set to the same height.")
d.body("Each picture carries the letter of its step, in plain lowercase with a period, sitting "
       "beneath the picture at its left. The label does not sit above the picture and is not "
       "set in bold.")

d.heading("How Many Pictures")
d.body("A picture is made for each step whose action it can show. The count of pictures need "
       "not match the count of steps:", before_list=True)
d.item("Steps that share a picture. ",
       "Two placements that differ only in which side of the figure they occupy are one step "
       "with one picture, because the second cannot be seen.")
d.item("Steps with no picture. ",
       "A closing step that states the section is complete uses the last picture of the "
       "strip and adds none of its own.")
d.body("A step whose action cannot be shown is written so that it needs no picture, rather "
       "than being given one that shows nothing. This is why the second eye of a figure is "
       "folded into the step that places the first.")

d.heading("What Each Picture Shows")
d.body("The pictures follow one grammar throughout a document, so that a builder learns to "
       "read them once:", before_list=True)
d.item("Seated and arriving. ",
       "Parts already placed sit in position. The part being added hovers a short distance "
       "above, or beside, the place it will take, and it is selected, so that it carries the "
       "outline marking it as the part the step is about.")
d.item("Parts mounted on side studs. ",
       "A part that mounts on the side of the figure is shown seated. A hovering position in "
       "front of the figure does not read in a flat view.")
d.item("Sub-assemblies alone. ",
       "A section that builds an element away from the figure is photographed with only that "
       "element's parts in the workspace, so the element fills its picture.")
d.item("Attachments hover, then seat. ",
       "When a finished element joins the figure, one picture shows it hovering at its "
       "destination and the next shows it seated.")
d.item("Mirrored elements. ",
       "An element built as a mirror image of another is assembled beside it, so that the two "
       "can be compared in one picture and told apart.")

d.heading("Closing a Section")
d.body("A section ends with a step that tells the builder what the finished element should "
       "look like and points to the picture that shows it: The completed head and crown "
       "should look like the image on the right (above). The sentence gives the builder a "
       "way to check the work before moving on.")

# The table must not split across a page break - a header row repeating over one orphaned
# row reads as a fault. Started on its own page, it sits whole.
d.page_break()
d.table("Table 1. The Parts of a Section, in Order",
        ["Element", "Form", "Example"],
        [["Heading", "Number and short noun phrase, bold",
          "1. Head and Crown"],
         ["Lead-in", "One sentence naming the bag",
          "Locate the bag of LEGO parts labeled \u201cHead and Crown.\u201d"],
         ["Steps", "Lettered list, one action to a line, part names in italic",
          "a. Place the Black 1 x 3 Plate on top of the Black 1 x 2 Brick."],
         ["Pictures", "A strip across the line, label beneath at the left",
          "a.   b.   c."],
         ["Closing step", "A sentence pointing to the finished picture",
          "e. The completed head and crown should look like the image on the right (above)."]],
        weights=[1.1, 2.4, 3.2])

d.heading("Formatting the Document Carries")
d.body("A kit document follows the same house formatting as every other document in the "
       "Sangala family:", before_list=True)
d.item("Body text. ", "Times New Roman 11 pt, black.")
d.item("Page numbers. ",
       "Bottom center, from a page field, on any document longer than one page.")
d.item("Headings. ",
       "Kept with the text beneath them, so that a heading can never stand alone at the "
       "foot of a page.")
d.item("Spacing. ",
       "Three points after a list item; a lead-in sentence sits tight to the list it "
       "introduces.")
d.item("Spelling. ", "American throughout — color, gray, center, labeled.")
d.body("A version number is never written inside the document. The file name carries it, and "
       "the superseded version moves to the Archive folder beside the current one.")

print(d.save(OUT, "LEGO Kit Style Guide"))
