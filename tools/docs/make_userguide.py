"""Sangala Blocks User Guide, Ver 1.0 — the script the document is built from.

House formatting comes from makedocx, which lives with Sangala Studio's tools; it is imported from
there rather than copied, so the three applications' documents cannot drift into three formats.
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"D:\Code Projects\Block Tools\Documents"

d = Doc()
d.title("Sangala Blocks User Guide")

d.body("Sangala Blocks is a tool for planning a figure built from real LEGO bricks. A design drawn in "
       "Sangala Studio is brought in as a frame — an outline to build against — and the builder places "
       "every brick against it by hand, choosing each part. Because each part carries the design number "
       "it is ordered by, a finished design is also its own parts list, and a second builder can obtain "
       "the same bricks and reproduce it.")
d.body("Nothing is placed automatically. Choosing the parts is the work the tool exists to support, not a "
       "step it performs on the builder's behalf.")

# ---------------------------------------------------------------- 1
d.heading("1. The Screen")
d.body("The window has four regions, and they carry the same names in all three Sangala applications:",
       before_list=True)
d.item("Menu Bar. ", "Across the top: Open, Save and Snapshot, with Settings beside them, and 3D View "
                     "and About at the right.")
d.item("Toolbar. ", "Down the left, headed Tools: Select, Part, Erase, Flip, Turn and Rotate, with a "
                    "button at the foot naming the side of the figure the builder is standing on, Front "
                    "or Back.")
d.item("Workspace. ", "The middle, where the design is built. The plate sits on a cork surface.")
d.item("Control Panel. ", "Down the right: the color palette, the brick size, the parts list, the "
                          "library and the snapshots, with the zoom control at the foot.")
d.body("A line above the palette reports what to do next, and the name of the open project appears above "
       "it once a design has been opened or saved. Beneath the project name is the brick currently "
       "selected: its name at the left, then the Depth control that moves it toward the front or the "
       "back, and at the right the Mini 3D Viewer button. The name and the Depth control belong to the "
       "selected brick and appear only while one is selected; the button belongs to no brick and is "
       "always there.")

# ---------------------------------------------------------------- 2
d.heading("2. Starting a Design")
d.body("Open accepts three kinds of file. A Sangala Studio design, ending in .model, is brought in as a "
       "frame to build against; the shapes of the Studio design become an outline and nothing else. A "
       "Sangala Blocks design, ending in .block, reopens work already begun, with every brick where it "
       "was left. A parts library, ending in .parts, adds the parts it holds to those the application "
       "offers, and is described in Section 16.")
d.body("A design may also be started with no frame at all, by placing bricks on the empty plate.")

# ---------------------------------------------------------------- 3
d.heading("3. The Frame")
d.body("The frame is a guide, not material. It is drawn behind the bricks and is never built, exported or "
       "counted in the parts list. Its purpose is to answer the question a builder keeps asking: does this "
       "brick belong where the figure's shoulder is.")
d.body("Two controls govern it, both in Settings. Show Frame draws it or hides it, which is useful when "
       "judging the bricks alone. Frame scale resizes it, and this matters more than it appears: a design "
       "drawn in Studio and a model built from bricks are rarely the same size in studs, so the frame is "
       "scaled until the figure it describes is the figure being built. The scale is a judgment, not a "
       "constant, because a single factor rarely makes every feature agree at once.")

# ---------------------------------------------------------------- 4
d.heading("4. Standing Figures and Reliefs")
d.body("Settings offers two ways of building, and the choice decides what a row means.", before_list=True)
d.item("Standing Figure. ", "The figure is seen from the side and stacked in courses, studs upward, the "
                            "way a model is built on a table. A row is a course, counted in plates.")
d.item("Relief. ", "The parts lie on the plate with their studs toward the viewer, a plate of depth at a "
                   "time, the way a relief is built up from a backdrop. Each part carries a base, which is "
                   "how far it stands proud.")
d.body("The two are not interchangeable views of one design. They are different ways of building, and a "
       "design is made in one of them.")

# ---------------------------------------------------------------- 5
d.heading("5. The Page")
d.body("The surface the design sits on is chosen in Settings: a LEGO baseplate of 32 x 32 studs, a Letter "
       "sheet, or a 12 x 12 inch sheet. The page never changes size to accommodate a design. A design too "
       "large for its page is reported rather than silently rescaled, because the page represents something "
       "real — a baseplate that can be bought, or a sheet that can be printed.")

# ---------------------------------------------------------------- 6
d.heading("6. Choosing a Part")
d.body("The Part tool opens a menu of kinds — brick, plate, slope, inverted slope, round brick, cone and "
       "wedge plate — and the size is set beneath it, in the Brick Size fields, by typing the number of "
       "columns and rows. Typing the size rather than choosing from a short list matters, because the "
       "commonest brick of all is 2 x 3 and no short list holds every size a builder reaches for.")
d.body("Every size offered corresponds to a part that exists. The design number is looked up from the "
       "LDraw parts library that ships with the application, so a parts list can be ordered from. A size "
       "that no real part has is reported as such rather than invented.")

# ---------------------------------------------------------------- 7
d.heading("7. Color")
d.body("The palette at the top of the control panel sets the color of the next brick placed. Each of the "
       "ten colors carries the official LDraw color code alongside its name — White is 15, Light Bluish "
       "Gray is 71 — so the color travels with the design number when the design is rendered. Each also "
       "carries BrickLink's own number for the same color, which is a different number and is what an "
       "order needs.")

# ---------------------------------------------------------------- 8
d.heading("8. Placing Bricks")
d.body("With a part and a color chosen, clicking the workspace places a brick, and the brick stays where "
       "it is put. Nothing falls: a design is a plan of a model rather than the model, so the courses are "
       "worked out in whatever order suits the designer. In a relief the click places the part where it "
       "is put in the same way, and its base is taken from whatever is already behind it.")
d.body("The Select tool moves a brick that is already placed; the Erase tool removes one. Ctrl-Z undoes "
       "the last change and Ctrl-Y restores it, so a misplaced brick costs nothing.")

# ---------------------------------------------------------------- 9
d.heading("9. Parking a Brick on the Cork")
d.body("A brick may be placed on the cork surface outside the plate. A brick parked there is drawn and is "
       "saved with the design, but it is left out of the parts list, out of the 3D view and out of every "
       "export: it is a candidate being tried for fit, not part of the design.")
d.body("Whether a brick is parked is decided by where it sits rather than by a setting, so dragging one "
       "onto the plate makes it part of the design with nothing else to do. A brick overlapping the plate "
       "at all counts as being on it.")

# ---------------------------------------------------------------- 10
d.heading("10. Flipping a Slope")
d.body("A slope faces one way. The Flip tool turns the chosen part to face the other. It is a turn and not "
       "a mirror image, because a mirrored slope would be a part that does not exist and could not be "
       "ordered.")

# ---------------------------------------------------------------- 11
d.heading("11. Turning a Part onto Its Side")
d.body("A part may be laid on the side of the figure, with its studs toward the viewer, instead of standing "
       "upright. The Turn tool does this, and it stays on until it is pressed again, so several parts may be "
       "laid the same way in succession. It is how an eye is set into a head and how a flat plate becomes a "
       "wing.")
d.body("Rotate turns a part already laid on its side through a quarter turn counterclockwise, about the face "
       "it is resting on, so that a wedge may point where the shape needs it to. It does nothing to an "
       "upright part: a quarter turn means something only in a view where the part presents a face.")

# ---------------------------------------------------------------- 12
d.heading("12. Depth in a Standing Figure")
d.body("A standing figure is more than one course deep, and that depth runs into and out of the screen. The "
       "workspace shows the figure from the front, so depth cannot be read there directly: a brick behind "
       "another is simply drawn behind it.")
d.body("Depth is counted from the midline of the figure, the plane the design is built about. A part in "
       "front of the midline has a positive depth and a part behind it a negative one, and the midline "
       "itself is zero.")
d.body("The Depth control sits beside the name of the selected brick in the control panel. Its two arrows "
       "move that brick half a layer at a time, the upper one toward the viewer and the lower one away, so "
       "two presses carry a part through a whole layer. The half step is what places a part on the midline "
       "of a figure whose courses are a whole stud deep, where a jumper plate's centered stud carries it.")

# ---------------------------------------------------------------- 13
d.heading("13. Working on the Far Side")
d.body("A standing figure is deep, and the near side hides the far one, so a wing or an eye belonging to the "
       "far side cannot be reached while the near side faces the builder. The button at the foot of the "
       "Toolbar names the side being worked from. It reads Front, and pressing it turns the figure round: it "
       "then reads Back, and the workspace is mirrored.")
d.body("Nothing in the design is changed by it. No brick's column, depth or facing is rewritten — it records "
       "where the builder is standing, and may be turned on and off freely without touching the model.")

# ---------------------------------------------------------------- 14
d.heading("14. Seeing the Design in Three Dimensions")
d.body("3D View shows the design as layers standing off the plate, and the view can be turned by dragging "
       "and zoomed by scrolling. It is a way of looking rather than a mode to build in: while it is up the "
       "building tools are set aside, and pressing 3D View again returns to the design.")
d.body("A second, smaller view of the same design is opened by the Mini 3D Viewer button, beside the Depth "
       "control. It draws the design in three dimensions in a small window over the workspace while the plan "
       "view remains in use, so a brick's depth can be seen while it is being placed. The window is carried "
       "by its title bar, resized by its lower corner, and turned by dragging the picture itself; the "
       "selected brick is ringed within it in the same blue the workspace uses. It opens closed.")
d.body("The two are not the same control. 3D View replaces the workspace with the whole design and sets the "
       "tools aside while it is up; the mini viewer is a window beside the work, and building continues "
       "behind it.")

# ---------------------------------------------------------------- 15
d.heading("15. The Parts List")
d.body("The Parts section of the control panel lists every brick in the design — the part, its design "
       "number, its color and the quantity — with the total piece count in its heading. The heading folds "
       "the list away, since the count is consulted constantly and the list itself only occasionally. "
       "Bricks parked on the cork are not counted.")
d.body("Save writes that list to a file, in either of two forms chosen in the Save dialog:", before_list=True)
d.item("A List to Read (.txt). ", "The parts, their design numbers, their colors and the quantities, as "
                                  "plain text to keep or to send.")
d.item("An Order to Place (.xml). ", "A BrickLink Wanted List. It is uploaded whole, once, and BrickLink "
                                     "then finds sellers who can fill it — so a design of dozens of parts "
                                     "becomes an order or two, and no number is typed by hand. BrickLink "
                                     "is owned by LEGO.")

# ---------------------------------------------------------------- 16
d.heading("16. A Parts Library")
d.body("A library is the bricks a builder owns or can get at, written as a plain list of design numbers "
       "and turned into a .parts file. Opening one adds what it holds to the parts the application offers, "
       "so a design can be planned from bricks that are actually to hand.")
d.body("A library adds to the menu and never replaces it: nothing already offered disappears, and more "
       "than one library may be held at a time. A kind of part the menu did not have — a tile, say — "
       "arrives with its own button on the Part tool.")
d.body("The Library section of the control panel lists what has been loaded: each part with its design "
       "number, its color and, where the list gave one, the quantity. That section answers what there is; "
       "the Parts section above it answers what has been used.")

# ---------------------------------------------------------------- 17
d.heading("17. Snapshots")
d.body("Snapshot records a picture of the build as it stands. The pictures collect in the Snapshots "
       "section of the control panel, in the order they were taken, and clicking one opens it full size, "
       "where it can be removed if it is not wanted.")
d.body("The pictures are drawn by an LDraw renderer rather than captured from the screen, so they have the "
       "appearance of the illustrations in published building instructions: flat brick colors, studs "
       "modeled, and no background behind the assembly. Taking a snapshot at the end of each phase of a "
       "build produces the sequence a second builder needs to follow.")

# ---------------------------------------------------------------- 18
d.heading("18. Saving the Snapshots as a Document")
d.body("The Save menu offers the collected snapshots as a document, and the format is chosen in the Save "
       "dialog itself, from its Save as type list:", before_list=True)
d.item("Word Document. ", "A .docx file, opened by Microsoft Word.")
d.item("PDF Document. ", "A .pdf file. The pictures are embedded without loss, so a tool that extracts "
                         "images from a PDF recovers exactly what was rendered.")
d.item("OpenDocument Text. ", "An .odt file, written natively by LibreOffice and opened by Word as well.")
d.body("Each document holds one line naming the project, then each picture in turn with space beneath it. "
       "The words are left to the person who writes them: the application exports the pictures and says "
       "nothing about what they are for. Written up as numbered steps they become building instructions; "
       "they are equally a record of a design, a page for a display, or figures for a report.")

# ---------------------------------------------------------------- 19
d.heading("19. Saving and Reopening a Design")
d.body("Save writes the whole design as a .block file — every brick with its part, color and position, "
       "the frame it was built against, the page, and the way of building. Reopening it restores the work "
       "exactly. The Save dialog asks where the file should go, and the application reads the file back "
       "afterward to confirm that it arrived.")
d.body("Everything the application writes is reached from the one Save menu. A project keeps the name it "
       "was opened with: saving a parts list or a set of snapshots does not rename the design.")

# ---------------------------------------------------------------- 20
d.heading("20. Quick Reference")
d.table("Table 1. Where Each Task Is Done",
        ["To do this", "Go here"],
        [["Build against a Studio design", "Open, and choose a .model file"],
         ["Add the bricks you own", "Open, and choose a .parts file"],
         ["Resize the outline to the figure", "Settings, Frame scale"],
         ["Stack in courses, or build a relief", "Settings, Build"],
         ["Change the plate or sheet", "Settings, Page size"],
         ["Choose a part", "Toolbar, Part, then Brick Size"],
         ["Choose a color", "Control panel, Color"],
         ["Move a brick", "Toolbar, Select"],
         ["Remove a brick", "Toolbar, Erase (Ctrl-Z undoes)"],
         ["Turn a slope around", "Toolbar, Flip"],
         ["Lay a part on its side", "Toolbar, Turn"],
         ["Point a part laid on its side", "Toolbar, Rotate"],
         ["Move a brick toward the front or the back", "Control panel, Depth"],
         ["Build on the far side of the figure", "Toolbar, Front / Back"],
         ["Watch the design in three dimensions while building", "Control panel, Mini 3D Viewer"],
         ["Try a brick without using it", "Place it on the cork beside the plate"],
         ["See the design in three dimensions", "3D View"],
         ["Read the piece count", "Control panel, Parts"],
         ["See what a loaded library holds", "Control panel, Library"],
         ["Write the parts list to a file", "Save, Parts List"],
         ["Order the parts", "Save, Parts List, and choose the BrickLink type"],
         ["Record the build so far", "Snapshot"],
         ["Write the snapshots into a document", "Save, Snapshots"],
         ["Keep the design to continue later", "Save, Design"]],
        weights=[46, 54])

d.heading("Appendix A. Installing Sangala Blocks")
d.body("Installation is covered by its own document, Installing Sangala Blocks, which is published beside "
       "this guide. In outline: the application is a folder of files that is copied to the computer and "
       "started from an icon. It requires no administrator rights, no driver and no internet connection "
       "once it has been copied.")
d.body("One part of the installation matters to the snapshots described in Section 17. The renderer that "
       "draws them, and the parts library it draws from, travel inside the same folder as the application. "
       "If the Snapshot button is not offered, the application has been started by opening its page "
       "directly rather than from its own icon; started from the icon, it supplies the renderer itself.")

print(d.save(OUT, "User Guide"))
