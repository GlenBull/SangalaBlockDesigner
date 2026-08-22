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
       "Sangala Studio, or a mosaic made in Sangala Mosaic, is brought in as a frame — an outline to "
       "build against — and the builder places every brick against it by hand, choosing each part. "
       "Because each part carries the design number it is ordered by, a finished design is also its own "
       "parts list, and a second builder can obtain the same bricks and reproduce it.")
d.body("Nothing is placed automatically. Choosing the parts is the work the tool exists to support, not a "
       "step it performs on the builder's behalf.")

# ---------------------------------------------------------------- 1
d.heading("1. The Screen")
d.body("The window has four regions, and they carry the same names in all three Sangala applications:",
       before_list=True)
d.item("Menu Bar. ", "Across the top: Open, Save, Snapshot and Transparent, with Settings beside them, "
                     "and 3D View and About at the right.")
d.item("Toolbar. ", "Down the left, headed Tools: Select, Part, Erase, Flip Horizontal, Flip Vertical "
                    "and Rotate, with a "
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
d.body("The zoom cluster sits at the foot of the control panel. The percentage between the minus and "
       "plus buttons is typed: click it, enter a number, and the view is at that scale — the same "
       "number in Sangala Studio shows the same size, and at 100 the page fits a typical window. Fit "
       "shows the whole plate. The magnet beside Fit governs Snap to Studs for the frame, described in "
       "Section 3. When the view is larger than the window, thin scrollbars appear along the "
       "workspace's bottom and right edges; the view also pans by holding Space and dragging, or by "
       "dragging with the middle mouse button.")

# ---------------------------------------------------------------- 2
d.heading("2. Starting a Design")
d.body("Open accepts five kinds of file.", before_list=True)
d.item("A Studio Design (.model). ", "Brought in as a frame to build against; the shapes of the Studio "
                                     "design become an outline and nothing else.")
d.item("A Mosaic (.mosaic). ", "Brought in as a frame directly, without passing through Sangala Studio. "
                               "What arrives, and what stays behind, is described in Section 3.")
d.item("A Blocks Design (.block). ", "Reopens work already begun, with every brick where it was left.")
d.item("A Parts Library (.library or .parts). ", "Adds the parts it holds to those the application "
                                                 "offers, described in Section 18.")
d.item("A Kit (.kit). ", "The parts of a finished design, opened beside the current work to build from, "
                         "described in Section 19.")
d.body("A design may also be started with no frame at all, by placing bricks on the empty plate.")

# ---------------------------------------------------------------- 3
d.heading("3. The Frame")
d.body("The frame is a guide, not material. It is drawn behind the bricks and is never built, exported or "
       "counted in the parts list. Its purpose is to answer the question a builder keeps asking: does this "
       "brick belong where the figure's shoulder is.")
d.body("The frame is made of elements — one for each shape of the Studio design, or each mass of the "
       "mosaic, it came from — and the elements answer the same gestures as bricks. Clicking one selects "
       "it, and the palette moves to its color; Shift+click adds another to the selection, and a sweep "
       "across empty ground takes every element fully inside the box. A selected element, or the whole "
       "selected set, is dragged to move it, and with the magnet on it lands on the stud-and-plate "
       "lattice, so the bricks placed against it line up; holding Alt drags it freely, and the magnet "
       "button in the zoom cluster turns Snap to Studs off altogether. Choosing a palette color recolors "
       "the selected element, which is how a region is given contrast against the bricks being placed on "
       "it. Ctrl-Z takes any of this back.")
d.body("A selected element also wears a resize box — a dashed frame with eight square handles, the same "
       "box Sangala Studio puts around a selected shape. Dragging a corner handle scales the element "
       "with its proportions kept; dragging a mid-edge handle stretches that one direction only, which "
       "is how a region is made taller or shorter without growing wider. The size is reported in studs "
       "and plates as the handle moves. Sweeping the whole frame into one selection and dragging an "
       "edge re-proportions the entire figure in one gesture.")
d.body("The Transparent button in the menu bar makes the bricks translucent so the frame shows through "
       "them — the same tracing view Sangala Mosaic offers over a photograph, with the pair reversed. "
       "While it is on, a Transparency slider appears beside the Show checkboxes in Settings: more "
       "transparency, more frame. Judging how a placed brick sits against the region under it is what "
       "the mode is for; the selection marks and the part being placed stay at full strength.")
d.body("A mosaic arrives as a frame under three rules. Each mass named in Sangala Mosaic becomes one "
       "element under its name; tiles in no mass arrive as elements of their own colors, one per patch, "
       "so the picture survives. A photograph's backdrop stays behind: when every cell of the mosaic's "
       "rectangle carries a tile — the signature of a mosaic built from a photograph — the import "
       "removes the field of tiles reachable from the corners in the corner's own color, the same rule "
       "as Mosaic's Remove Background button, and the status line reports how many tiles were left "
       "behind. And seen from the side, each tile arrives one stud wide and two plates tall, so every "
       "edge of the frame lands on a line a brick can land on; seen top-down, a tile is a stud square. "
       "The page switches to the 32 x 32 baseplate, which is the surface a mosaic is built on.")
d.body("Two controls in Settings complete the picture. Show Frame draws the frame or hides it, which is "
       "useful when judging the bricks alone. Frame scale resizes the whole frame by one percentage; "
       "the handles above are the finer tool, because a single factor rarely makes every feature agree "
       "at once.")

# ---------------------------------------------------------------- 4
d.heading("4. The View: Top-Down or Side")
d.body("The View control in Settings says which way the builder is looking at the design, and the choice "
       "decides what a row means.", before_list=True)
d.item("Side (plates). ", "The figure is seen from the side and stacked in courses from the ground, the "
                          "way a standing model is built on a table: studs across, plates of height up. "
                          "This is the view a standing figure such as the crane is built in, and the "
                          "view the application opens in.")
d.item("Top-down (studs). ", "The builder looks at the face of the baseplate, so both axes are studs — "
                             "the way a relief or a mosaic is built. The parts lie with their studs "
                             "toward the viewer, each layer standing one plate proud of the one behind, "
                             "and each part carries a base, which is how far it stands proud.")
d.body("The coordinates of a design do not change with the view; what changes is the meaning of the "
       "vertical direction — plates from the side, studs from the top. The stud grid is drawn only "
       "top-down, because the grid is the plate's face: from the side there is no grid to draw, and the "
       "Grid checkbox is disabled there and says so. Switching the view clears the bricks placed, since "
       "the two readings of a row do not describe the same brick; Ctrl-Z brings them back, and a saved "
       "design reopens in the view it was made in.")

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
d.body("The palette and the selected brick are bound both ways. Selecting a brick moves the palette to "
       "that brick's color, so what the palette shows is always the color in hand; and choosing a color "
       "while a brick is selected repaints that brick, which is how a part is recolored without losing "
       "the depth, facing and quarter turn that erasing and replacing it would cost. Ctrl-Z takes a "
       "recolor back like any other change. With no brick selected the palette is simply the color the "
       "next brick will be placed in.")
d.body("A parts library made today names no color. A library is a catalog of shapes — what a part is, "
       "not what it is to be made in — so the color of a brick is chosen from the palette at the moment "
       "it is placed. An older library that does carry one uses it only to set the palette when its row "
       "is clicked; it never decides what is placed. A color chosen while a library part is selected stays with that part, so a body brick "
       "set to green is placed in green each time until it is changed.")

# ---------------------------------------------------------------- 8
d.heading("8. Placing Bricks")
d.body("With a part and a color chosen, clicking the workspace places a brick, and the brick stays where "
       "it is put. Nothing falls: a design is a plan of a model rather than the model, so the courses are "
       "worked out in whatever order suits the designer. In either view the click places the "
       "part where it is put and its depth is taken from whatever already occupies its columns: "
       "top-down it stands clear of what is behind it, and from the side it comes to rest just "
       "clear of what is already there, on the side the builder is standing on.")
d.body("The Select tool moves a brick that is already placed; the Erase tool removes one. Ctrl-Z undoes "
       "the last change and Ctrl-Y restores it, so a misplaced brick costs nothing. Moving a brick "
       "across the plan does not change its depth: a part keeps the layer it was given, and the Depth "
       "control described in Section 13 is what changes it. A brick taken out to the cork and brought "
       "back comes back unaltered. Selecting more than one brick, and binding a selection into a "
       "group, is Section 9.")
d.body("Each part is drawn at its own shape rather than as a rectangle standing in for it. The outline "
       "is measured from the part itself, so a wedge shows the flat section at its wide end and a slope "
       "shows how far its ramp actually reaches. The studs are not part of that outline: the workspace "
       "draws them as its own marks, so a part tipped onto its face shows the studs that are then on it.")
d.body("What the plan draws and what the 3D view builds come from the same geometry, so a wedge or a "
       "slope is the same part seen two ways rather than two drawings kept in step. The cone and the "
       "round brick are the exception and keep their own drawn shapes, which were settled against a "
       "photograph of the real brick.")

# ---------------------------------------------------------------- 9
d.heading("9. Selecting Several Bricks, and Groups")
d.body("Shift+click adds a brick to the selection — the whole of its group, if it belongs to one — and a "
       "sweep across empty ground selects every brick that lies fully inside the box, along with any "
       "frame elements fully inside it. A brick merely grazed by the box is not taken, so a sweep past a "
       "part does not capture it.")
d.body("A press on any brick of the selection drags the whole selection, all of it by the same amount — "
       "the same rule the frame's elements follow. A press on a brick outside the selection selects that "
       "brick instead. Delete removes everything selected; Ctrl-Z restores it.")
d.body("Group, beside the Depth control, binds the selected bricks so they select and move as one from "
       "then on: clicking any member takes the whole group. A group can be grown — select it, Shift+click "
       "a new brick, Group again — and groups nest, so Ungroup takes apart the outermost binding and any "
       "group inside it survives. Once a selection is bound, the Name button gives it a name: Crown, "
       "Head, Wing. The names matter beyond tidiness — they become the sections of the parts list "
       "(Section 17), the elements of a kit (Section 19), and the pieces a figure is divided into if it "
       "is ever opened in Sangala Studio for printing.")

# ---------------------------------------------------------------- 10
d.heading("10. Parking a Brick on the Cork")
d.body("A brick may be placed on the cork surface outside the plate. A brick parked there is drawn and is "
       "saved with the design, but it is left out of the parts list, out of the 3D view and out of every "
       "export: it is a candidate being tried for fit, not part of the design.")
d.body("Whether a brick is parked is decided by where it sits rather than by a setting, so dragging one "
       "onto the plate makes it part of the design with nothing else to do. A brick overlapping the plate "
       "at all counts as being on it.")

# ---------------------------------------------------------------- 11
d.heading("11. Flip Horizontal")
d.body("Flip Horizontal selects the mirror image of a part, left to right, so that a slope faces the other "
       "way. A slope is symmetrical, so its mirror image is the same part turned round and one design "
       "number serves both hands.")
d.body("Not every part is symmetrical. LEGO makes left and right versions of many wedges, each with its "
       "own design number, and for those the mirror image is a separate part to order. The application "
       "does not yet make that substitution: it mirrors the drawing and keeps the number, so a design "
       "using both hands should be checked against its parts list before ordering.")

# ---------------------------------------------------------------- 12
d.heading("12. Flip Vertical and Rotate")
d.body("Flip Vertical tips a part forward, the way a chess piece is tipped over on a board, so that it comes "
       "to rest against the face of the figure with its studs toward the builder rather than pointing "
       "upward. It stays on until it is pressed again, so several parts may be set down the same way in "
       "succession. It is how an eye is set into a head and how a flat plate becomes a wing.")
d.body("Rotate turns a part already tipped forward through a quarter turn counterclockwise, about the face "
       "it is resting on, so that a wedge may point where the shape needs it to. It does nothing to an "
       "upright part: a quarter turn means something only in a view where the part presents a face.")

# ---------------------------------------------------------------- 13
d.heading("13. Depth in a Standing Figure")
d.body("A standing figure is more than one course deep, and that depth runs into and out of the screen. The "
       "workspace shows the figure in profile, so depth cannot be read there directly: a brick behind "
       "another is simply drawn behind it.")
d.body("Depth is counted from the midline of the figure, the plane the design is built about. A part in "
       "front of the midline has a positive depth and a part behind it a negative one, and the midline "
       "itself is zero.")
d.body("The Depth control sits beside the name of the selected brick in the control panel. Its two arrows "
       "move that brick half a layer at a time, the upper one toward the viewer and the lower one away, so "
       "two presses carry a part through a whole layer. The half step is what places a part on the midline "
       "of a figure whose courses are a whole stud deep, where a jumper plate's centered stud carries it.")
d.body("Once a part is placed, that control is what changes its depth. Sliding a brick sideways across the plan "
       "leaves its layer exactly as it was, which is what allows a part to be lifted out of the way and "
       "put back without losing the position it was given.")

# ---------------------------------------------------------------- 14
d.heading("14. Working on the Far Side")
d.body("A standing figure is deep, and the near side hides the far one, so a wing or an eye belonging to the "
       "far side cannot be reached while the near side faces the builder. The button at the foot of the "
       "Toolbar names the side being worked from. It reads Front, and pressing it turns the figure round: it "
       "then reads Back, and the workspace is mirrored.")
d.body("Nothing in the design is changed by it. No brick's column, depth or facing is rewritten — it records "
       "where the builder is standing, and may be turned on and off freely without touching the model.")

# ---------------------------------------------------------------- 15
d.heading("15. Copying a Brick")
d.body("Ctrl-C copies the selected brick and Ctrl-V places a copy of it. The copy carries everything "
       "about the original — its part, its color, its layer, and the way it has been tipped or turned — "
       "and arrives one stud along, so that it can be seen and moved rather than hidden underneath. "
       "Pressing Ctrl-V again places another, each a stud further on, and each may be undone on its own.")
d.body("A copy of a part lying on the side away from the builder is brought round to the side the "
       "builder is standing on — whether that is the far side reached through the Front / Back button, "
       "or a far-side part copied while facing the front. A part that had been tipped forward has its "
       "studs turned to face the builder; an upright brick stays upright.")
d.body("It is placed at the mirror image of the original's position on the body brick its stack is "
       "mounted on, followed down through any tipped parts between: a plate resting on the front face "
       "of a side-stud brick is copied onto the back face of that same brick, and a second plate "
       "resting on the first comes round with it. A part mounted on nothing has no such brick to mirror "
       "about, and is placed at the mirror image of its depth about the midline instead, which is what "
       "reproduces a leg or a crest slope from its opposite number.")
d.body("A copy of a part already on the side being worked from is an exact twin, at the same depth, one "
       "stud along. The two sides therefore behave alike: near or far, a copy lands beside the original "
       "and never settles onto whatever else happens to lie in its columns.")

# ---------------------------------------------------------------- 16
d.heading("16. Seeing the Design in Three Dimensions")
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

# ---------------------------------------------------------------- 17
d.heading("17. The Parts List")
d.body("The Parts section of the control panel lists every brick in the design — the part, its design "
       "number, its color and the quantity — with the total piece count in its heading. The heading folds "
       "the list away, since the count is consulted constantly and the list itself only occasionally. "
       "Bricks parked on the cork are not counted.")
d.body("Where groups have been named, the list organizes itself by those names: each name heads a "
       "section, with its parts indented beneath it and its own piece count beside it, and anything "
       "belonging to no group falls under Other Parts at the end. A heading folds its own parts away, "
       "the way the Parts heading folds the whole list, and the count stays in the heading so a folded "
       "section still says how big it is.")
d.body("Three things can be done from the list itself.", before_list=True)
d.item("Arrange the Elements. ", "A heading is dragged onto another to put it there, so the sections can "
                                 "be read in the order the figure is built — crown, head, body — "
                                 "rather than the order the groups happened to be made in. The "
                                 "arrangement is kept with the design and follows a group through a "
                                 "rename.")
d.item("Find a Part in the Model. ", "Clicking a row selects every brick of that part in that color, so "
                                     "the pieces are outlined in the workspace. Selecting a brick in the "
                                     "workspace lights its row in return.")
d.item("Move a Part Between Groups. ", "A row under Other Parts is dragged onto a named heading to add "
                                       "those bricks to that group, and a row under a name is dragged "
                                       "into Other Parts to take them out again. The whole section is the "
                                       "target, not the heading alone, and it lights while the pointer is "
                                       "over it. Other Parts stays on the list once any group exists, so "
                                       "there is always somewhere to put a part back.")
d.body("Save writes that list to a file, in any of four forms chosen in the Save dialog:", before_list=True)
d.item("A List to Read (.txt). ", "The parts, their design numbers, their colors and the quantities, as "
                                  "plain text to keep or to send.")
d.item("A Document by Element (.docx). ", "A Word document with a table for each named element of the "
                                          "figure — the form a kit's printed instructions list their "
                                          "parts in.")
d.item("A Kit (.kit). ", "The same parts, kept by element, in a file that reopens in Sangala Blocks so "
                         "another builder can build from it. Described in Section 19.")
d.item("An Order to Place (.xml). ", "A BrickLink Wanted List. It is uploaded whole, once, and BrickLink "
                                     "then finds sellers who can fill it — so a design of dozens of parts "
                                     "becomes an order or two, and no number is typed by hand. BrickLink "
                                     "is owned by LEGO.")

# ---------------------------------------------------------------- 18
d.heading("18. A Parts Library")
d.body("A library is the bricks a builder owns or can get at, written as a plain list of design numbers "
       "and turned into a .parts file. Opening one adds what it holds to the parts the application offers, "
       "so a design can be planned from bricks that are actually to hand.")
d.body("A library adds to the menu and never replaces it: nothing already offered disappears, and more "
       "than one library may be held at a time. A kind of part the menu did not have — a tile, say — "
       "arrives with its own button on the Part tool.")
d.body("A library is saved from the Save menu, as a .library file. What is written is everything loaded "
       "at that moment, merged into one catalog, so a library assembled by opening two of them, or "
       "pruned to the parts a finished design actually uses, can be kept and passed on. It records no "
       "color and no quantity, so a library that arrived carrying either is cleaned by being saved. A "
       ".parts file made before the name changed still opens unaltered.")
d.body("The Library section of the control panel lists what has been loaded: each part with its design "
       "number. It names no color and no quantity, because a library says what a part is and not what it "
       "is to be made in or how many are owned. That section answers what there is to build with; the "
       "Parts section above it answers what has been used, and it is the Parts section that a physical "
       "build is ordered from.")

# ---------------------------------------------------------------- 19
d.heading("19. A Kit")
d.body("A kit is the parts of a finished design, saved by element: Save, Parts List, and the Kit type in "
       "the dialog. The file carries everything each part needs — footprint, height, shape, the studs on "
       "its faces — so it opens complete on any machine, with nothing else to install or load.")
d.body("Opening a .kit does not replace the work in progress; the kit arrives beside it, as its own "
       "section of the control panel between Parts and Library, and the project keeps its name. Each "
       "element of the kit heads its own rows — Crown, Head, Body, with a piece count — and each row "
       "shows the quantity, the part, its design number and a swatch of its color.")
d.body("The rows are how the kit is built from. Clicking a row sets the palette to that part's color and "
       "readies the part, so the next click on the workspace places it; dragging a row onto the "
       "workspace places that part where it lands. Either way the kit's own color wins — a kit records "
       "what the pieces are, and the palette follows it. The kit panel's heading folds it away when it "
       "is in the way, and it belongs to the session rather than the design: it is not written into the "
       ".block file, and is opened again when it is wanted.")

# ---------------------------------------------------------------- 20
d.heading("20. Snapshots")
d.body("Snapshot records a picture of the build as it stands. The pictures collect in the Snapshots "
       "section of the control panel, in the order they were taken, and clicking one opens it full size, "
       "where it can be removed if it is not wanted.")
d.body("The pictures are drawn by an LDraw renderer rather than captured from the screen, so they have the "
       "appearance of the illustrations in published building instructions: flat brick colors, studs "
       "modeled, and no background behind the assembly. Taking a snapshot at the end of each phase of a "
       "build produces the sequence a second builder needs to follow.")

# ---------------------------------------------------------------- 21
d.heading("21. Saving the Snapshots as a Document")
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

# ---------------------------------------------------------------- 22
d.heading("22. Saving and Reopening a Design")
d.body("Save writes the whole design as a .block file — every brick with its part, color and position, "
       "the frame it was built against, the page, and the view it was made in. Reopening it restores the work "
       "exactly. The Save dialog asks where the file should go, and the application reads the file back "
       "afterward to confirm that it arrived.")
d.body("Everything the application writes is reached from the one Save menu. A project keeps the name it "
       "was opened with: saving a parts list or a set of snapshots does not rename the design.")
d.body("A saved design can also be opened in Sangala Studio, where it becomes geometry for a 3D printer "
       "rather than a plan for bricks. Each part arrives as its own measured shape, and each named group "
       "arrives as an element that can be given a depth and printed as a piece. Sangala Blocks itself "
       "sends nothing to a machine; it is Sangala Studio that prints. What is named here decides what can "
       "be worked with as one piece there, so it is worth naming the groups of a figure — head, "
       "crown, wing — before saving it.")

# ---------------------------------------------------------------- 23
d.heading("23. Quick Reference")
d.table("Table 1. Where Each Task Is Done",
        ["To do this", "Go here"],
        [["Build against a Studio design", "Open, and choose a .model file"],
         ["Build against a mosaic", "Open, and choose a .mosaic file"],
         ["Add the bricks you own", "Open, and choose a .library or .parts file"],
         ["Move a frame element", "Click it, then drag; the magnet lands it on the lattice"],
         ["Resize a frame element", "Drag a corner handle; an edge handle stretches one way"],
         ["Recolor a frame element", "Select it, then Control panel, Color"],
         ["See the frame through the bricks", "Transparent, in the menu bar"],
         ["Resize the whole outline at once", "Settings, Frame scale"],
         ["Choose the view: side or top-down", "Settings, View"],
         ["Change the plate or sheet", "Settings, Page size"],
         ["Set the zoom exactly", "Type into the percentage in the zoom cluster"],
         ["Choose a part", "Toolbar, Part, then Brick Size"],
         ["Choose a color", "Control panel, Color"],
         ["Recolor a brick", "Select it, then Control panel, Color"],
         ["Move a brick", "Toolbar, Select"],
         ["Select several bricks", "Shift+click, or sweep across empty ground"],
         ["Move a selection together", "Drag any brick in it"],
         ["Bind a selection into a group", "Group, beside the Depth control"],
         ["Name a group", "Name, once the group is bound"],
         ["Remove a brick", "Toolbar, Erase (Ctrl-Z undoes)"],
         ["Face a slope the other way", "Toolbar, Flip Horizontal"],
         ["Tip a part forward, studs toward you", "Toolbar, Flip Vertical"],
         ["Point a tipped part", "Toolbar, Rotate"],
         ["Move a brick toward the front or the back", "Control panel, Depth"],
         ["Build on the far side of the figure", "Toolbar, Front / Back"],
         ["Copy the selected brick", "Ctrl-C"],
         ["Place a copy of it", "Ctrl-V"],
         ["Watch the design in three dimensions while building", "Control panel, Mini 3D Viewer"],
         ["Try a brick without using it", "Place it on the cork beside the plate"],
         ["See the design in three dimensions", "3D View"],
         ["Read the piece count", "Control panel, Parts"],
         ["See what a loaded library holds", "Control panel, Library"],
         ["Keep the library to share or reopen", "Save, Library"],
         ["Write the parts list to a file", "Save, Parts List"],
         ["Save the parts as a kit", "Save, Parts List, and choose the Kit type"],
         ["Build from a kit", "Open the .kit; click a row, or drag it onto the workspace"],
         ["Order the parts", "Save, Parts List, and choose the BrickLink type"],
         ["Record the build so far", "Snapshot"],
         ["Write the snapshots into a document", "Save, Snapshots"],
         ["Keep the design to continue later", "Save, Design"],
         ["Read the list by element", "Name the groups; the Parts list follows the names"],
         ["Put the elements in order", "Drag a heading in the Parts list onto another"],
         ["Find every brick of one part", "Click its row in the Parts list"],
         ["Move a part into or out of a group", "Drag its row between sections of the Parts list"],
         ["Print the figure", "Open the saved .block file in Sangala Studio"]],
        weights=[46, 54])

d.heading("Appendix A. Installing Sangala Blocks")
d.body("Installation is covered by its own document, Installing Sangala Blocks, which is published beside "
       "this guide. In outline: the application is a folder of files that is copied to the computer and "
       "started from an icon. It requires no administrator rights, no driver and no internet connection "
       "once it has been copied.")
d.body("One part of the installation matters to the snapshots described in Section 20. The renderer that "
       "draws them, and the parts library it draws from, travel in the same folder as the application. If "
       "the Snapshot button is not offered, the application was started by opening its page directly "
       "rather than from its icon; started from the icon, it supplies the renderer itself.")

print(d.save(OUT, "User Guide"))
