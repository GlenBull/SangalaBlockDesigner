"""Sangala Blocks Technical Manual, Ver 1.0 — the script the document is built from.

Formatting comes from Sangala Studio's makedocx, imported rather than copied, so the three
applications' documents keep one format.
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"D:\Code Projects\Block Tools\Documents"

d = Doc()
d.title("Sangala Blocks Technical Manual")

d.body("This manual describes how Sangala Blocks is built, how its parts fit together, and what a "
       "developer needs to know before changing it. The companion User Guide describes how the "
       "application is used. Matters common to all three Sangala applications — the shared repository, "
       "the branch and pull request workflow, and the conventions the family holds to — are covered by "
       "the Sangala Tools Technical Manual and are referred to here rather than repeated.")

# ---------------------------------------------------------------- 1
d.heading("1. Downloading and Installing")
d.body("What is needed: a Windows computer, and nothing else. The .NET compiler used to build the "
       "program is already part of Windows, and no administrator rights are required at any point.")
d.body("The repository is obtained from GitHub:", before_list=True)
d.code("https://github.com/GlenBull/SangalaBlockDesigner")
d.body("The program is built once, by double-clicking Build SangalaBlocks.cmd. This compiles "
       "SangalaBlocksServer.cs into SangalaBlockDesigner.exe with the crane icon embedded. Thereafter the "
       "application is started by double-clicking that executable, which serves its page and opens it in "
       "the default browser. The application is running correctly when the page appears, the crane icon "
       "sits in the notification area, and the Snapshot button is offered rather than disabled.")

# ---------------------------------------------------------------- 2
d.heading("2. What Sangala Blocks Is, and the Rule That Shapes It")
d.body("Sangala Blocks plans a kit of real LEGO bricks. A figure designed in Sangala Studio, or a mosaic "
       "made in Sangala Mosaic, is brought in as a frame, and the builder places every brick against it "
       "by hand. Because each part carries the design number it is ordered by, a finished design is also "
       "its own parts list.")
d.body("One constraint shapes every decision in the code: the application must run on a school computer "
       "with no administrator rights, no installation and no dependency fetched from the internet at run "
       "time. That is why the interface is a single HTML file, why the local program is compiled with the "
       "compiler Windows already carries, and why the renderer and the parts it needs travel inside the "
       "application's own folder rather than being installed.")
d.body("A second rule is pedagogical rather than technical: nothing is placed automatically. Choosing "
       "the parts is the work the tool exists to support.")

# ---------------------------------------------------------------- 3
d.heading("3. Architecture")
d.body("Four pieces, and the boundaries between them are deliberate.", before_list=True)
d.item("The Page. ", "SangalaBlockDesigner.html, one self-contained file holding the interface, the brick "
                     "model, the parts catalog, the 3D view and the document writers. It holds everything "
                     "that knows what a brick is.")
d.item("The Bridge. ", "SangalaBlockDesigner.exe, compiled from SangalaBlocksServer.cs. It serves the page "
                       "on a loopback port and does the two things a browser cannot do for itself: read "
                       "the parts library off disk, and run "
                       "another program.")
d.item("The Renderer. ", "LDView, in the LDView folder beside the application, which draws an LDraw model "
                         "as an image.")
d.item("The Parts Library. ", "LDraw part files, in LDraw\\ldraw beside the application, from which the "
                              "catalog and the renderer both draw.")
d.body("The division between the page and the bridge is the one worth stating twice: THE PAGE WRITES THE "
       "MODEL AND THE BRIDGE ONLY RENDERS IT. The bridge receives LDraw text, hands it to LDView and hands "
       "back a PNG; it knows nothing of studs, plates or part numbers. That is what keeps a bridge for "
       "another operating system a transcription of a few dozen lines rather than a second implementation "
       "of the geometry.")

# ---------------------------------------------------------------- 4
d.heading("4. Repository Layout")
d.table("Table 1. What Each File and Folder Holds",
        ["Path", "What it is"],
        [["SangalaBlockDesigner.html", "The whole interface, in one file"],
         ["SangalaBlocksServer.cs", "The local bridge"],
         ["SangalaBlockDesigner.exe", "The built bridge, committed so it need not be rebuilt"],
         ["Build SangalaBlocks.cmd", "Compiles the bridge with the in-box compiler"],
         ["Crane.ico", "The application icon, a crowned crane built from bricks"],
         ["LDView\\", "The renderer, its license and a link to its source"],
         ["LDraw\\ldraw\\", "The parts and primitives the application needs"],
         ["Projects\\", "Sample designs and test models"],
         ["Documents\\", "This manual, the User Guide and the other documents"],
         ["tools\\", "Scripts: the parts catalog, the bundle, the document generators"]],
        weights=[38, 62])

# ---------------------------------------------------------------- 5
d.heading("5. Build and Run")
d.body("Build SangalaBlocks.cmd compiles the single source file with csc.exe from the .NET Framework "
       "already present in Windows, targeting a windowed executable so that managed school systems treat "
       "it as a program rather than blocking it as a script.")
d.body("Changes to the page take effect on a browser refresh, because the page is read from disk on every "
       "request. Changes to the bridge require a rebuild and a restart.")

# ---------------------------------------------------------------- 6
d.heading("6. The Browser Interface")
d.body("The page is one file: markup, style and script together, with no external library and no request "
       "to any host but the bridge. Its four regions are the menu bar, the Toolbar down the left, the "
       "workspace and the control panel; those are the names used throughout the family, and the word "
       "rail appears nowhere.")
d.body("The design is held as an array of bricks, each carrying its part, its color index, its column and "
       "row, its base, its half step, whether it is mirrored, whether it has been tipped forward and "
       "through how many quarter turns. Undo and redo work by serializing that array, and the same "
       "serialization is what a .block file holds.")
d.body("Three canvases are used: the plan view the design is built on; a second, hidden until 3D View is "
       "pressed, on which the design is drawn as layers standing off the plate; and a third, smaller, in a "
       "window over the workspace. The 3D view is a way of looking rather than a mode, and it puts the "
       "building tools aside while it is up. The window does not: the plan view stays in use behind it.")
d.body("The second and third are drawn by the SAME renderer. It takes its canvas and its camera as "
       "arguments rather than reading one set of module values, and both views are built from the one list "
       "of triangles the design produces, so the two cannot disagree about what has been built. The window "
       "redraws only when the design or the selection changes, which is tested by reducing the design to a "
       "short string and comparing it: the plan view is redrawn on every mouse move, and rebuilding tens of "
       "thousands of triangles for a pointer that moved three pixels would be the most expensive thing in "
       "the application.")
d.body("One line of the zoom arithmetic is shared with the rest of the family: SCALE100 is 2.4 CSS "
       "pixels per millimeter, under the same name and value in Sangala Studio, chosen so that 100 "
       "percent fits the working page on a typical screen and the same number typed in two windows "
       "shows the two designs at the same size. The percentage readout is an input — typing a number "
       "applies it — and Fit computes the window's own honest percentage rather than snapping to a "
       "nominal one. When the pannable world overflows the window, thin scrollbars are drawn along the "
       "workspace's bottom and right edges; they are kept in step by wrapping draw itself, and their "
       "bounds are the pan clamp's own, so the bars and the pan cannot disagree about where the world "
       "ends.")

# ---------------------------------------------------------------- 7
d.heading("7. The Brick Model")
d.body("Geometry follows LEGO rather than a drawing grid. A stud is 8 mm and a plate 3.2 mm, so three "
       "plates make a brick. Bricks are drawn in side view with their studs standing proud of the top "
       "face.")
d.body("What a row means depends on the view, and confusing the two is the mistake that looks "
       "plausible until an image is rendered:", before_list=True)
d.item("Side (plates). ", "The design is seen from the side. A column is across in studs, a row is a "
                          "vertical course counted in plates, and depth runs into the screen in studs. "
                          "See Section 8.")
d.item("Top-down (studs). ", "The design is seen face on. A column is across and a row is depth, both in "
                             "studs, and a part's base records how many plates it stands proud of the "
                             "backdrop.")
d.body("The control is the View selector in Settings, and it is a view rather than a kind of design: the "
       "inherent coordinates do not change, only the meaning of the vertical direction. The stored "
       "values keep their older names — standing for the side view, relief for top-down — so every file "
       "already saved opens exactly as it did. On the plan the difference is one function, vUnit, which "
       "answers 3.2 mm from the side and 8 mm top-down; the snap, the rows and the drawing all ask it. "
       "Switching the view clears the bricks placed, because the two readings of a row do not describe "
       "the same brick; the switch commits, so Ctrl-Z restores them. The stud grid draws only top-down — "
       "the grid is the plate's face — and the Grid checkbox is disabled from the side, with the reason "
       "in its tooltip.")
d.body("A brick that overlaps the plate nowhere is parked: drawn and saved, but excluded from the parts "
       "list, the 3D view and every export. That state is derived from where the brick sits rather than "
       "stored as a flag, so it stays true through a save, a reload and a change of page size.")
d.body("THE PLAN DRAWS A PART'S OWN SHAPE. One silhouette per design number and viewing pair is "
       "measured from the part's own mesh — which the plan asks for the first time it draws that part, "
       "whether or not anything 3D has been opened — and kept, drawn at the size the part is. A wedge "
       "therefore shows the flat section at its wide end, and a slope shows how far its ramp truly "
       "reaches. The polygon written out by hand for each family of shapes has not gone: it stands in "
       "until the geometry arrives, and permanently on a page with no bridge to ask.")
d.body("Four things about that measurement are worth stating, because each is a decision rather than a "
       "consequence:", before_list=True)
d.item("Studs Are Not In It. ", "The y coordinate is clamped at the origin plane, so the studs fold onto "
                                "the top face and leave the outline. The workspace draws them itself, "
                                "from the library's measured stud positions, which is what lets a tipped "
                                "part show recesses rather than studs when its attitude disagrees with "
                                "the side being viewed from.")
d.item("A Full Box Keeps Its Rounding. ", "A part whose outline fills its own box is drawn as the rounded "
                                          "rectangle, that rounding being a drawing convention rather "
                                          "than a measurement, and the test is measured so no register "
                                          "of which parts are rectangles is needed.")
d.item("The Cone and the Round Brick Are Exempt. ", "Both keep the shapes drawn for them here, which were "
                                                    "settled against a photograph of the real brick. The "
                                                    "LDraw file draws a collar the part does not have, "
                                                    "and a measured silhouette would put it back.")
d.item("It Is a Rasterization. ", "Not a union of polygons, because overlapping triangles, a hollow "
                                  "underside and a curved edge all rasterize alike. The projection takes "
                                  "the same yaw the 3D view works out, so the two pictures cannot "
                                  "disagree about which way a part is turned — except in relief, "
                                  "deliberately: the outline there takes a tipped part's mapping rather "
                                  "than relief's own 3D matrix, which mirrors, and which is left alone "
                                  "because changing it would alter every relief design at once.")
d.body("NOTHING FALLS. A placed part stays where it was put, whether or not a frame lies behind it. An "
       "earlier version settled each part onto whatever was under it, on the reasoning that a builder "
       "cannot stack a figure in mid-air; what that missed is that this is a plan of a model rather than "
       "the model, and a designer works out the courses in whatever order suits them. The physical rule "
       "belongs to the physical build. In a relief a part still takes its base from what is already "
       "behind it, which is not a fall but how a relief is assembled.")

# ---------------------------------------------------------------- 8
d.heading("8. Depth, the Midline and the Half Step")
d.body("A standing figure is deeper than one course, and the workspace cannot show it: the plan is a side "
       "elevation — the figure in profile — so a part behind another is merely drawn behind it. Depth is therefore carried as a "
       "number and shown in a picture, never inferred from the plan.")
d.body("Depth is measured from the MIDLINE, the plane the figure is built about. A part's base records "
       "where its MOUNTING face sits, in studs, positive toward the viewer and negative away from them "
       "— for a part whose studs face the front that is its rear face, and for one tipped studs-back it "
       "is its front face; the "
       "midline is zero and carries no course of its own. Held beside it is a half step, either zero or "
       "one half, which is what places a part on the midline of a figure whose courses are a whole stud "
       "deep. The two are held apart because a placement recomputes the base and would wash a fraction "
       "straight out of it.")
d.body("Three consequences are worth stating, because each was a defect before it was a rule:", before_list=True)
d.item("Drawing Order. ", "Depth dominates, then height. Anything in front covers anything behind it "
                          "whatever their heights, and the order reverses when the figure is turned round, "
                          "or the far side would be drawn last and hide what it was turned to reveal.")
d.item("What a Part Rests On. ", "A part settles clear of where the brick below it actually is, half step "
                                 "and all, rather than clear of the layer that brick nominally occupies.")
d.item("Tipping a Part. ", "A part tipped forward is as thick as it is high and as tall as it is deep. "
                           "Its own two other dimensions are swapped onto its face, and swapped again by a "
                           "quarter turn.")
d.body("A part's base names the face it is MOUNTED BY, and which of its two faces that is depends on how "
       "it has been tipped. A part whose studs face the front is mounted by its rear face and reaches "
       "toward the viewer from there; a part whose studs face the back is mounted by its front face and "
       "reaches away. The two surfaces are therefore derived rather than assumed, by a single pair of "
       "expressions, rearB and frontB, which the plan's drawing order, its resting-place arithmetic and "
       "the paste all read. The 3D build and the LDraw export apply the same rule in their own terms: "
       "the mesh grows from the mounting face by the part's thickness, and the export offsets its "
       "placement by the part's own box. Writing that arithmetic out at each site is what allowed the "
       "three to hold three different opinions about where a studs-away part sat, each wrong by that "
       "part's own thickness or by twice it. A change to the rule must therefore be made in all three, "
       "and the three are checked against each other by rendering rather than guaranteed by "
       "construction.")
d.body("Settling belongs to PLACEMENT and to nothing else. A part being put down for the first time comes "
       "to rest clear of whatever occupies its columns, measured from the side the builder is standing "
       "on. A part already in the design has a depth its designer chose, so moving it across the plan "
       "leaves that depth alone — including a move out to the cork and back, which is how a part is "
       "lifted aside to reach the one beneath it.")
d.body("The builder moves a part through this axis with the Depth control in the panel, whose two arrows "
       "step it half a layer at a time. Where a step lands is split back into the whole layer the part is "
       "in and the half it stands off, so a part can be carried through any number of layers by repeating "
       "the step.")
d.body("Whether a layer should also be NUMBERED for the builder, and what such a number would count, is "
       "not settled. The panel shows no layer number today: the window over the workspace shows where a "
       "part sits among its neighbours, which is what a number was being asked to say in words.")

# ---------------------------------------------------------------- 9
d.heading("9. Copy and Paste")
d.body("Ctrl-C and Ctrl-V are Sangala Studio's, function for function, because Studio settled the question "
       "first: a copy carries everything about the part, repeated pastes fan out rather than stack, the "
       "new copy becomes the selection, and each paste commits at once so a run of them undoes one at a "
       "time. What differs is the step. A brick lives on the stud grid, so a copy moves one STUD along as "
       "seen, which is a column lower once the builder has walked round to the far side.")
d.body("The clipboard holds the BRICK, not a reading taken from it. While the original is still in the "
       "design a paste reads its current column, row and layer; only a brick deleted since the copy falls "
       "back to the recorded snapshot. A snapshot alone was wrong for the way the application is used: a "
       "part is dragged aside to reach the one beneath it and copied where it has been dragged to, where "
       "it is mounted on nothing, and both its position and its depth were then taken from the staging "
       "area rather than from the figure.")
d.body("A copy of a part lying on the side away from the builder is brought round to the side the "
       "builder is standing on — which is the far side reached through Front / Back, and equally a "
       "far-side part copied while facing the front. The rule for where it lands took three attempts:",
       before_list=True)
d.item("Not the Midline. ", "Reflecting the part's span about the midline is right only where the body it "
                            "is mounted on is itself centered there. A side-stud brick spanning the two "
                            "layers in front of the midline sends a plate mounted on it two layers behind "
                            "the figure, hanging in space.")
d.item("Not Settled. ", "Asking where the part would COME TO REST from the far side is symmetric and still "
                        "wrong, because it settles clear of everything in those columns. A wing eight "
                        "layers away in the same columns takes the copy with it.")
d.item("Its Own Host. ", "The copy is reflected about the mid-plane of the brick the original is mounted "
                         "on, following that chain through tipped detail to the body brick beneath it, so "
                         "a plate on a side-stud brick's front face lands on its back face. A part mounted "
                         "on nothing has no such brick, and the midline is then the only mirror there is.")
d.body("Neither side settles, which is what makes the two behave alike: a copy on the near side is an "
       "exact twin one stud along, and a copy on the far side is that twin's mirror image — and, if the "
       "original was itself tipped, tipped the other way so its studs face the builder. An upright brick "
       "is mirrored and left upright. All of this belongs to a standing figure: a relief has one side "
       "and nothing in it is tipped, so a paste there is always the plain twin. The mirror excludes the "
       "copies a run of pastes has already put down, or a "
       "body brick pasted twice would mirror about its own first copy and march backward through the "
       "figure a course at a time.")

# ---------------------------------------------------------------- 10
d.heading("10. The Frame")
d.body("The frame is held twice, and the doubling is the design. guideRaw is the unscaled geometry — "
       "what a .block file stores — and guide is the working copy, derived from it by the Frame scale "
       "whenever it is needed and never stored, so a restored or reopened design cannot end up scaled "
       "twice. Every edit writes both in step: the drag applies one delta to the working copy and the "
       "same delta over the scale to the raw one, and the resize applies the same factors about the "
       "same anchor in each space.")
d.body("Placement is remembered rather than baked in. placeX and placeY hold where the design sits on "
       "the plate, and draw lays the stud lattice, the frame and the bricks down together at that "
       "offset — one placement over everything that lives in design coordinates, which is what keeps a "
       "brick's studs on the outline it was placed against. Baking the offset into the frame's points "
       "instead once put the frame and the bricks on lattices 4.7 mm apart, which no snapping could "
       "cure.")
d.body("A frame arrives two ways. A .model is read the way Sangala Studio would place it — each "
       "polygon at its own coordinates times the design's scale, offset by its saved position — with a "
       "region's thickness and lift converted from millimeters to plates. A .mosaic is read by Studio's "
       "own importer carried over: the built grid of tiles, each named mass traced into one region "
       "under its name, and tiles in no mass traced one region per same-color patch so the picture "
       "survives. Two rules guard the mosaic path. The backdrop of a photograph — the field of tiles "
       "reachable from the built rectangle's corners in the corner's own color — is left behind, and "
       "that flood runs only when every cell of the rectangle carries a tile, the signature of a "
       "photograph's build; a sparse mosaic already cleaned by hand is not touched, a gate added after "
       "the flood ate the grass out of exactly such a file. And a tile's height follows the view: one "
       "stud wide by two plates tall from the side, so every edge of the frame lands on a line a brick "
       "can land on — 8 mm is 2.5 plates, so square tiles can never be plate-true — and a stud square "
       "top-down. The page is switched to the baseplate, which is the surface a mosaic is built on.")
d.body("The frame answers Studio's selection grammar. Clicking selects the topmost region under the "
       "point — the last drawn, which is how the eye reads it — Shift adds to the set, and the sweep "
       "takes what lies fully inside, bricks and frame elements in the same gesture. A drag re-derives "
       "every position from copies taken at the press plus one total delta, so a snap engaging and "
       "letting go leaves no accumulated drift; the set's minimum corner snaps to the stud-and-plate "
       "lattice absolutely, Studio's rule, with Alt dragging free and the magnet in the zoom cluster "
       "as the switch. The palette follows a selected element's fill and a palette choice recolors it. "
       "Bricks rest against the frame's indexed top, so the index is rebuilt when a drag or a resize "
       "ends.")
d.body("The resize box is Studio's, carried over line for line: eight square handles on the selection's "
       "bounding box, a corner scaling uniformly by projecting the pointer onto the original diagonal "
       "so drifting off it does not wobble the scale, a mid-edge handle scaling one axis about the "
       "opposite side, and the scale floored short of zero so a handle dragged through its anchor "
       "cannot silently mirror the frame. Sizes are reported in studs and plates as the handle moves.")
d.body("Transparent draws the bricks translucent so the frame reads through them — Mosaic's tracing "
       "view with the pair reversed. The alpha is owned by the brick-drawing function itself, whose "
       "first act is to set it; an earlier attempt to set it around the brick pass was stomped brick "
       "by brick, which is worth remembering before adding any translucency elsewhere. The brick's "
       "shadow fades with its brick; the hover ghost and the selection marks keep full strength. The "
       "mode and the slider are view state, saved in no file; the frame itself — raw geometry, scale "
       "and placement — travels in the .block.")

d.heading("11. Groups, Names and the Parts List")
d.body("A group binds bricks so that they select and move as one. The objects stay separate and can be "
       "taken apart again: grouping is a bundle, not a weld.")
d.body("Grouping nests. Each brick carries gpath, the path of group numbers it belongs to, outermost "
       "first, and group is simply the first of them. Group puts a new number on the front of that path, "
       "so a group can sit inside a group, and Ungroup removes the first one — peeling one level "
       "and leaving anything inside it standing.")
d.body("A name belongs to a level, not to a brick, so gnames runs parallel to gpath and gnames[0] is the "
       "outermost group's name. Held as a single field it could only ever carry one name, and naming an "
       "outer group wrote over the name an inner group already had. The name is written on every member "
       "rather than into a table of groups, which is Sangala Studio's arrangement exactly: an attribute "
       "travels with the brick through every copy, save and undo, with no second structure to keep in "
       "step.")
d.body("The parts list buckets by the outermost name. A part used in two groups therefore appears twice, "
       "once under each name, each row counting only that group's pieces — which is what makes a row "
       "unambiguous enough to drag. The bucketed form is also what the by-element Word document and the "
       "kit file are written from. The plain tally the .txt list and the BrickLink order are built from "
       "is not bucketed: those need one line per part and color across the whole design, since the same "
       "brick used in a head and in a wing is one thing to buy.")
d.body("Two pieces of state sit behind the list, and they are deliberately different in kind:", before_list=True)
d.item("The Arrangement Is the Design's. ", "A list of names is written into the .block file, carried in "
       "the undo snapshot, and updated when a group is renamed. It is keyed by name rather than by "
       "position, so building another group cannot silently reorder the rest, and a group re-created with "
       "a name the file already knows returns to its place.")
d.item("The Fold Is the Panel's. ", "Which sections are folded away is held in the page alone and is not "
       "saved. A folded section is still in the design, in the parts list and in the order.")
d.body("Joining and leaving are the same two acts the buttons perform, reached by dragging a row. A row "
       "under Other Parts dropped on a named section takes that group's number and name at the front of "
       "its own path — which is what Group does, except that the number already exists, and that is "
       "the whole of the difference between joining a group and making one. A row under a name dropped "
       "into Other Parts is Ungroup's one-level peel. Other Parts is kept on the list once any group "
       "exists, even when empty, because joining the last loose part would otherwise remove the only "
       "place a part can be dropped to leave a group.")
d.body("The names matter beyond this application. Sangala Studio reads a .block file, and every named "
       "group arrives there as an element that can be given a depth and printed as one piece. What is "
       "named here decides what can be worked with as a piece there.")

d.heading("12. The Parts Catalog")
d.body("Every part the application offers carries a real design number and a real footprint, and both are "
       "read from the LDraw library rather than typed. Two tools do that reading: tools/ldparts.py "
       "resolves a number, reports the part's own description and measures its geometry, and "
       "tools/sizes_from_ldraw.py generates the table of sizes the menu offers.")
d.body("Three facts about the library shape that code. A part's first line is its description, so a "
       "number needs no index to be named. A superseded number answers with a redirection, which must be "
       "followed to reach the geometry. And the measurements are exact: one LDraw unit is 0.4 mm, a stud "
       "is 20 units, a plate 8 and a brick 24, with the Y axis pointing down so that a part's origin sits "
       "at the top of its body.")
d.body("A size that no real part has is reported as such. A parts list that claims a part which cannot be "
       "bought is worse than no parts list.")
d.body("The palette is bound to the selection in both directions. Selecting a brick moves the palette to "
       "its color, and a color chosen while a brick is selected is written onto that brick and "
       "committed, so it undoes as one step and the parts list is rebuilt — the list groups by part AND "
       "color, so a recolor moves a piece from one row to another. With no brick selected the palette is "
       "only the color the next placement will take. The rule that a color chosen while a LIBRARY row is "
       "selected stays with that part number is unchanged and independent: one records what the builder "
       "means a part to be, the other repaints a brick already placed.")
d.body("A library is written as well as read. The Save menu writes what the panel holds, merged, as a "
       ".library file; the extension is the word a student meets at both ends, and the marker inside "
       "says the same. Either marker opens, so every .parts file already made is unaffected - the "
       "format did not change, only what it is called.")
d.body("A library STATES neither color nor quantity. It is a catalog of shapes: what a part is, not "
       "what it is to be made in or how many are owned. Color is chosen from the palette at the moment a "
       "brick is placed and then stays with that part number, so a body brick set to green is placed in "
       "green until it is changed; and a quantity belongs to the parts list, which counts what the design "
       "actually uses and is what a physical build is ordered from. An entry that names a color would be "
       "a choice made on the builder's behalf, and one that names a quantity invites the panel to be read "
       "as stock. The format has not changed: an older file that carries a color still seeds the palette "
       "when its row is picked, and a quantity in one is simply not shown, so nothing already written is "
       "stranded.")
d.body("A .parts library extends that catalog at run time. tools/parts_library.py turns a submitted list "
       "of numbers into one, deriving every field from LDraw but the two a submitted line may name — a "
       "color and a quantity, which are copied through and which the application no longer reads. The "
       "page merges it "
       "into the menu, adding sizes it did not have and whole kinds it did not know. Two consequences "
       "follow. A library may name a part the page's own tables never held, so tools/bundle_parts.py "
       "reads every library in the repository as well as the page — a part that can be placed but was not "
       "shipped renders as nothing at all, with no error. And a design records the libraries it was built "
       "from, so opening it elsewhere reports what is missing rather than quietly offering less.")

# ---------------------------------------------------------------- 11
d.heading("13. The Local Bridge")
d.body("SangalaBlocksServer.cs is Sangala Studio's bridge ported: a loopback TcpListener, which needs "
       "neither administrator rights nor a firewall exception, a notification-area icon, and a single "
       "instance per session — a second double-click opens the page the first is already serving rather "
       "than adding another icon.")
d.body("It takes the first free port in 8830 to 8850. That range is deliberately clear of Sangala "
       "Studio's 8787 to 8807, because a student may have both applications open and two bridges "
       "competing for one port would look like a defect in whichever started second.")
d.table("Table 2. The Routes the Bridge Answers",
        ["Route", "What it does"],
        [["GET /", "Serves SangalaBlockDesigner.html, read from disk on every request"],
         ["GET /status", "Reports that this is Sangala Blocks, and whether the renderer and the parts "
                         "library were found"],
         ["POST /snapshot", "Takes an LDraw model as text, renders it and returns a PNG"],
         ["GET /part", "Serves an LDraw part file and every file it references, as JSON, so the page "
                       "can measure and draw the real part"]],
        weights=[26, 74])
d.body("The page asks /status before it offers the Snapshot button, so a missing renderer is stated in "
       "the interface rather than discovered as a failed snapshot. A page opened directly as a file, "
       "with no bridge behind it, still designs and saves; it simply cannot start a renderer and cannot "
       "ask for a part's geometry, so the plan falls back to the shapes drawn for it by hand, and says "
       "so.")

# ---------------------------------------------------------------- 12
d.heading("14. Snapshots and the LDraw Pipeline")
d.body("A snapshot is produced in three steps. The page writes the design as an LDraw model, one "
       "type-1 line for each brick that is not parked, carrying its color code, a 3 x 4 transform and the "
       "part file. The bridge writes that text to a temporary file and runs LDView over it. The resulting "
       "image is returned to the page and joins the queue.")
d.body("The renderer is asked for the appearance of published building instructions: edges drawn, the "
       "conditional highlights that give a curve its outline, the image cropped to the assembly, and a "
       "transparent background so that no gray field is carried into a document.")
d.body("Two failures are worth knowing about, because neither announces itself:", before_list=True)
d.item("A Folder That Merely Exists. ", "LDView was once given a parts folder that matched only because "
                                        "Windows ignores case — the folder that CONTAINS the library "
                                        "rather than the library itself. It found no parts, drew an empty "
                                        "scene and exited reporting success. A candidate folder is now "
                                        "accepted only if the parts and primitive directories are inside "
                                        "it.")
d.item("A Blank Image. ", "An image too small to hold a brick is treated as a failure and reported, with "
                          "the model kept on disk, since the model is the only evidence of why.")
d.body("The same arithmetic exists twice — in the page for snapshots, and in tools/ldr_export.py for the "
       "command line — and the two must not drift. They are checked against each other by extracting the "
       "page's own function and running both over one design; they agree byte for byte.")

# ---------------------------------------------------------------- 13
d.heading("15. The Bundled Renderer and Parts")
d.body("LDView and the parts it needs are committed to the repository, so a clean checkout renders. "
       "LDView is 4 MB and requires nothing beside it; its license travels with it, as its terms require, "
       "along with a link to its source.")
d.body("The parts are pruned and the primitives are not, and the difference is the trap in this "
       "subsystem. Walking every part number the page can place, through its redirections and its "
       "sub-file references, yields 62 files out of the library's 24,591 — a pruning worth making. That "
       "walk does not find what LDView substitutes as it draws: the logo-bearing stud that puts the "
       "manufacturer's name on every stud top, and the 48-segment versions of the curves. Nothing refers "
       "to those files, and their absence raises no error; it renders a picture that looks correct and "
       "differs from the full library by thousands of pixels, every one of them on a stud.")
d.body("All 2,833 primitives are therefore shipped, at a cost of 9.6 MB. tools/bundle_parts.py computes "
       "the closure and tracks it, reading the part numbers out of the page rather than holding a list of "
       "its own, since a list held here stops matching the day a part is added to the menu. Its --verify "
       "option renders one model against the bundle and against the full library and compares the pixels, "
       "which is the only check that catches geometry that is missing rather than wrong.")

# ---------------------------------------------------------------- 14
d.heading("16. The Documents the Page Writes")
d.body("The snapshots are written into a document by the page itself, with no library and no help from "
       "the bridge, so the same capability exists on every platform the page runs on. A Word file and an "
       "OpenDocument file are both archives of XML, so one archive writer serves both.")
d.body("Each format has one thing that must be right:", before_list=True)
d.item("Word. ", "The content types part must be the first entry in the archive.")
d.item("OpenDocument. ", "The mimetype entry must be first and stored uncompressed, and every part "
                         "including each picture must be declared in the manifest or it does not appear.")
d.item("PDF. ", "There is no text flow. Word and LibreOffice decide where pages break; a PDF places every "
                "line and picture at an absolute point on a numbered page, so the export measures each "
                "step and starts a page when one no longer fits. Its text uses two of the fonts every "
                "reader already has, and its pictures are embedded without loss so that a tool extracting "
                "images recovers what was rendered.")
d.body("All three fit a picture inside a box rather than to the page width alone, which caps both "
       "dimensions and never distorts a proportion, and all three place four steps on a page so that the "
       "three formats are one document rather than three layouts.")
d.body("The parts list is written here too, in four forms: plain text to read; a Word document by "
       "element, one table per named group, in the style a kit's printed instructions use; a kit file; "
       "and a BrickLink Wanted List as XML to order from. The kit is JSON under a sangala marker — the "
       "sections by element, each row carrying the quantity, the color, and the whole part: footprint, "
       "height, shape and the studs on its faces, so a kit opens complete on any machine with no library "
       "beside it. Opened, it arrives as its own panel beside the design; it is session state and is "
       "never written into the .block. The one thing in the BrickLink file which cannot be derived is the color. BrickLink "
       "numbers colors its own way and the numbers do not agree with LDraw — red is 4 to LDraw and 5 to "
       "BrickLink — and no rule converts between them, so each is recorded in the palette beside the LDraw "
       "code, read from BrickLink's own guide. A color with no BrickLink number is left out of the export "
       "and reported. Item numbers need no such table, since BrickLink catalogs basic parts by the design "
       "number the list already carries.")

# ---------------------------------------------------------------- 15
d.heading("17. Verifying Changes")
d.body("A change to the page is tested by refreshing the browser; a change to the bridge requires a "
       "rebuild. Beyond that, three checks have proved worth the trouble:", before_list=True)
d.item("Run the Function, Not a Copy of It. ", "Where a check needs the page's own code, the function is "
                                               "extracted from the file and run as it stands, so what is "
                                               "tested is what ships.")
d.item("Compare Images, Not Descriptions. ", "Missing geometry does not raise an error. The test is to "
                                             "render twice and compare the pixels.")
d.item("Test From a Clean Checkout. ", "Export the tree to an empty folder and run it there. A feature "
                                       "that works only where it was developed is not finished, and this "
                                       "is the check that says so.")
d.body("Documents generated by the scripts in tools/docs are checked with the pagination tool kept with "
       "Sangala Studio, which reports orphaned headings and page fill and must be clean before "
       "publication.")

# ---------------------------------------------------------------- 16
d.heading("18. Contributing")
d.body("Work proceeds one change at a time: make the change, let it be tested on a real machine, then "
       "commit. Batching untested changes has cost this project time before. Commit messages record why a "
       "change was made and what remains unverified, since the reasoning is what a later reader needs and "
       "the code already states what was done.")
d.body("Collaboration is by branch and pull request within the shared repository. Sangala Studio and "
       "Sangala Mosaic are read as reference and are not edited from here: a correction made while "
       "looking at Sangala Blocks belongs to Sangala Blocks.")

# ---------------------------------------------------------------- 17
d.heading("19. Glossary")
d.table("Table 3. Terms Used in This Manual",
        ["Term", "Meaning"],
        [["Backdrop", "The field of tiles a photograph builds around its subject, left behind when a "
                      "photo-full mosaic is imported"],
         ["Base", "Where a part's mounting face sits: in a relief, how many plates it stands proud of the "
                  "backdrop; in a standing figure, how far it stands from the midline, in studs"],
         ["Bridge", "The local program that serves the page and runs the renderer"],
         ["Closure", "The set of files reached by following every reference from a starting part"],
         ["Course", "One horizontal layer of a standing build"],
         ["Depth", "How far a part stands from the midline of a standing figure, positive toward the "
                   "viewer and negative away from them"],
         ["Element", "One selectable piece of the frame: a shape of the Studio design, or a mass of the "
                     "mosaic, it came from"],
         ["Frame", "The outline brought in from a Sangala Studio design or a Sangala Mosaic, built "
                   "against but never built"],
         ["Half step", "Half a stud of depth, which places a part on the midline of a figure whose "
                       "courses are a whole stud deep"],
         ["Kit", "The parts of a finished design saved by element as a .kit file, opened beside a "
                 "project to build from"],
         ["LDraw unit", "0.4 mm. A stud is 20, a plate 8, a brick 24"],
         ["Midline", "The plane a standing figure is built about. Depth is counted from it, and it is "
                     "zero and carries no course of its own"],
         ["Mini 3D viewer", "The small window over the workspace that draws the design in three "
                            "dimensions while the plan view stays in use"],
         ["Parked", "Placed on the cork beside the plate: kept, but not part of the design"],
         ["Plate", "A part one third the height of a brick"],
         ["Primitive", "A shared shape that parts are built from, rather than a part itself"],
         ["Relief", "A design built up from a backdrop, seen face on"],
         ["Standing", "A design stacked in courses, seen from the side"],
         ["Stud", "The 8 mm module everything is measured in"],
         ["Tipped", "Brought to rest against the face of the figure, studs toward the viewer, rather "
                   "than standing upright. Set by Flip Vertical; still recorded in a saved design as "
                   "the field named turn, which the rename did not touch"],
         ["View", "Which way the builder is looking: Side (plates) or Top-down (studs). The stored "
                  "values keep the older names, standing and relief, so saved files open unchanged"]],
        weights=[24, 76])

d.heading("Appendix A. Other Platforms")
d.body("The page runs unchanged on macOS, on Linux and on a Chromebook. What does not is the bridge, "
       "which is a Windows executable. Sangala Studio met the same problem and answered it with one "
       "Python file serving both macOS and the Chromebook. The same answer applies here: because the "
       "bridge only reads files off disk, runs a program and returns what it read or rendered, it "
       "transcribes rather than being reimplemented.")
d.body("Three facts govern that work. LDView is published for Windows, macOS and Linux, so the renderer "
       "is not the obstacle. ChromeOS runs a program of this kind only inside its Linux development "
       "environment, which on a school-managed device is the administrator's setting and on a personally "
       "owned one is the owner's. And every prebuilt LDView for Linux targets Intel processors, so an ARM "
       "Chromebook would require it to be compiled.")

print(d.save(OUT, "Tech Manual"))
