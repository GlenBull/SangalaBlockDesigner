"""Documentation Process — the script the document is built from.

Records how the crane assembly instructions (Crane Snapshots 2.docx) were produced with
the built-in Snapshot feature, so the method can be repeated for another figure.
Formatting comes from Sangala Studio's makedocx, imported rather than copied, so the three
applications' documents keep one format.
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"D:\Code Projects\Block Tools\Documents"

d = Doc()
d.title("Documentation Process")

d.body("This document records how the assembly instructions for the LEGO crane "
       "(Crane Snapshots 2.docx) were produced from the finished design with the Snapshot "
       "feature built into Sangala Blocks. The method extends the proof of concept in "
       "Documentation Demo.docx to a complete figure, and it can be repeated for any design "
       "the application holds.")

d.heading("The Source Design")
d.body("The pictures were made from Projects\\Crane.block, the finished crane: thirty-four "
       "parts, most of them collected into named groups (Head, Crown, Body, Back, the two "
       "Wings, Legs, and Neck), standing on an 8 x 16 baseplate. Every part is photographed "
       "at the position the design records for it, so the instructions and the design cannot "
       "disagree.")

d.heading("The Order of Assembly")
d.body("The instructions build the crane in nine sections, each a sub-assembly or an "
       "attachment:", before_list=True)
d.step("Assemble the head and crown.")
d.step("Assemble the body.")
d.step("Assemble the back.")
d.step("Assemble the wings.")
d.step("Attach the wings to the body.")
d.step("Add the legs to the body.")
d.step("Place the crane on the baseplate.")
d.step("Add the neck.")
d.step("Place the crown and head on the neck.")

d.heading("The Picture Grammar")
d.body("Every picture follows the pattern set by the worked example for Section 1:",
       before_list=True)
d.item("Seated and arriving. ",
       "Pieces already placed sit seated in position. The piece being added hovers a few "
       "plates above, or a few studs beside, the place it will take, and it is selected so "
       "it carries the blue outline that marks it as the piece the sentence is about.")
d.item("Face-mounted pieces. ",
       "A piece that mounts on side studs (an eye, a side plate) is shown seated, since a "
       "hovering position in front of the figure would not read in the flat view.")
d.item("Sub-assemblies photographed alone. ",
       "Sections 1 through 4 are photographed with only their own pieces on the workspace. "
       "The plan snapshot crops to the build, so each sub-assembly fills its picture.")
d.item("Attachments hover, then seat. ",
       "When a finished sub-assembly joins the model (a wing, the whole crane onto the "
       "baseplate, the head onto the neck), one picture shows it hovering at its "
       "destination and the next shows it seated.")
d.item("Hidden pieces. ",
       "A piece on the far side of the figure - the left-hand eye - receives an instruction "
       "sentence but no picture, because the flat view cannot show it. The worked example "
       "set this rule.")

d.heading("Taking the Pictures")
d.new_list()
d.body("The pictures were taken in the running application:", before_list=True)
d.step("The crane design was opened in Sangala Blocks.")
d.step("For each sub-step, the pieces of the current state were arranged: everything "
       "already placed at its design position, the arriving piece offset three or four "
       "plates from its seat, and the arriving piece selected.")
d.step("Snapshot was clicked, and Plan View chosen from its menu. The picture joined the "
       "queue in the Snapshots panel.")
d.step("Thirty-five snapshots were taken this way, in section order, from the first brick "
       "of the head to the completed crane.")
d.body("The placements and snapshots can be made entirely by hand. In this production run "
       "they were driven programmatically through the application's own controls, so that "
       "each state could be staged exactly; every picture was still rendered and recorded "
       "by the Snapshot feature itself.")

d.heading("Saving and Adding the Written Instructions")
d.new_list()
d.body("The document was then assembled in three steps:", before_list=True)
d.step("Save, then Snapshots, wrote the queue as a Word document, with a numbered label "
       "over each picture and the page number in the footer.")
d.step("A script inserted a heading and an instruction paragraph ahead of each section's "
       "first picture, and replaced each numbered label with its sub-step letter (1.a "
       "through 9.b). The script is kept in tools\\docs\\crane_snapshots_2_instructions.py, "
       "so the document can be rebuilt from a fresh export.")
d.step("The finished document was checked for pagination (every heading keeps with the "
       "text below it), and the PDF was printed from the finished Word file so the two "
       "formats match. The exports without instructions were moved to Documents\\Archive.")

d.table("Table 1. The Nine Sections and Their Pictures",
        ["Section", "Content", "Sub-steps", "Pictures"],
        [["1", "Assemble the Head and Crown", "1.a - 1.f", "5"],
         ["2", "Assemble the Body", "2.a - 2.f", "5"],
         ["3", "Assemble the Back", "3.a - 3.f", "6"],
         ["4", "Assemble the Wings", "4.a - 4.f", "6"],
         ["5", "Attach the Wings to the Body", "5.a - 5.c", "3"],
         ["6", "Add the Legs to the Body", "6.a - 6.c", "3"],
         ["7", "Place the Crane on the Baseplate", "7.a - 7.b", "2"],
         ["8", "Add the Neck", "8.a - 8.c", "3"],
         ["9", "Place the Crown and Head on the Neck", "9.a - 9.b", "2"]],
        weights=[1, 4, 1.6, 1.2], center_cols=(0, 2, 3))
d.body("A sub-step without a picture is one whose action the flat view cannot show (the "
       "far-side eye in 1.d) or a closing sentence that shares the final picture of its "
       "section (2.f). Thirty-five pictures cover the thirty-seven sub-steps across twelve "
       "pages.")

d.heading("A Note on This Production Run")
d.body("The save was made from the application running inside an embedded preview panel, "
       "and that panel refused the Save dialog's write step, leaving zero-byte files. The "
       "document bytes were taken unchanged from the application's own builders and written "
       "to disk by a small local relay. A save made in an ordinary browser needs no such "
       "step.")

print(d.save(OUT, "Documentation Process"))
