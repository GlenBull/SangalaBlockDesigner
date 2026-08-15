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
d.body("Sangala Blocks plans a kit of real LEGO bricks. A figure designed in Sangala Studio is brought in "
       "as a frame, and the builder places every brick against it by hand. Because each part carries the "
       "design number it is ordered by, a finished design is also its own parts list.")
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
                       "on a loopback port and does the one thing a browser cannot do for itself: run "
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
       "row, its base and whether it is flipped. Undo and redo work by serializing that array, and the "
       "same serialization is what a .block file holds.")
d.body("Two canvases are used: the plan view the design is built on, and a second, hidden until 3D View "
       "is pressed, on which the design is drawn as layers standing off the plate. The 3D view is a way "
       "of looking rather than a mode, and it puts the building tools aside while it is up.")

# ---------------------------------------------------------------- 7
d.heading("7. The Brick Model")
d.body("Geometry follows LEGO rather than a drawing grid. A stud is 8 mm and a plate 3.2 mm, so three "
       "plates make a brick. Bricks are drawn in side view with their studs standing proud of the top "
       "face.")
d.body("What a row means depends on the way of building, and confusing the two is the mistake that looks "
       "plausible until an image is rendered:", before_list=True)
d.item("Standing. ", "The design is seen from the side. A column is across in studs and a row is a "
                     "vertical course counted in plates.")
d.item("Relief. ", "The design is seen face on. A column is across and a row is depth, both in studs, and "
                   "a part's base records how many plates it stands proud of the backdrop.")
d.body("A brick that overlaps the plate nowhere is parked: drawn and saved, but excluded from the parts "
       "list, the 3D view and every export. That state is derived from where the brick sits rather than "
       "stored as a flag, so it stays true through a save, a reload and a change of page size.")
d.body("NOTHING FALLS. A placed part stays where it was put, whether or not a frame lies behind it. An "
       "earlier version settled each part onto whatever was under it, on the reasoning that a builder "
       "cannot stack a figure in mid-air; what that missed is that this is a plan of a model rather than "
       "the model, and a designer works out the courses in whatever order suits them. The physical rule "
       "belongs to the physical build. In a relief a part still takes its base from what is already "
       "behind it, which is not a fall but how a relief is assembled.")

# ---------------------------------------------------------------- 8
d.heading("8. The Parts Catalog")
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
d.body("A .parts library extends that catalog at run time. tools/parts_library.py turns a submitted list "
       "of numbers into one, deriving every field but color and quantity from LDraw; the page merges it "
       "into the menu, adding sizes it did not have and whole kinds it did not know. Two consequences "
       "follow. A library may name a part the page's own tables never held, so tools/bundle_parts.py "
       "reads every library in the repository as well as the page — a part that can be placed but was not "
       "shipped renders as nothing at all, with no error. And a design records the libraries it was built "
       "from, so opening it elsewhere reports what is missing rather than quietly offering less.")

# ---------------------------------------------------------------- 9
d.heading("9. The Local Bridge")
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
         ["POST /snapshot", "Takes an LDraw model as text, renders it and returns a PNG"]],
        weights=[26, 74])
d.body("The page asks /status before it offers the Snapshot button, so a missing renderer is stated in "
       "the interface rather than discovered as a failed snapshot. A page opened directly as a file, "
       "with no bridge behind it, still designs and saves; it simply cannot start a renderer, and says so.")

# ---------------------------------------------------------------- 10
d.heading("10. Snapshots and the LDraw Pipeline")
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

# ---------------------------------------------------------------- 11
d.heading("11. The Bundled Renderer and Parts")
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

# ---------------------------------------------------------------- 12
d.heading("12. The Documents the Page Writes")
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
d.body("The parts list is written here too, in two forms: plain text to read, and a BrickLink Wanted List "
       "as XML to order from. The one thing in that file which cannot be derived is the color. BrickLink "
       "numbers colors its own way and the numbers do not agree with LDraw — red is 4 to LDraw and 5 to "
       "BrickLink — and no rule converts between them, so each is recorded in the palette beside the LDraw "
       "code, read from BrickLink's own guide. A color with no BrickLink number is left out of the export "
       "and reported. Item numbers need no such table, since BrickLink catalogs basic parts by the design "
       "number the list already carries.")

# ---------------------------------------------------------------- 13
d.heading("13. Verifying Changes")
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

# ---------------------------------------------------------------- 14
d.heading("14. Contributing")
d.body("Work proceeds one change at a time: make the change, let it be tested on a real machine, then "
       "commit. Batching untested changes has cost this project time before. Commit messages record why a "
       "change was made and what remains unverified, since the reasoning is what a later reader needs and "
       "the code already states what was done.")
d.body("Collaboration is by branch and pull request within the shared repository. Sangala Studio and "
       "Sangala Mosaic are read as reference and are not edited from here: a correction made while "
       "looking at Sangala Blocks belongs to Sangala Blocks.")

# ---------------------------------------------------------------- 15
d.heading("15. Glossary")
d.table("Table 3. Terms Used in This Manual",
        ["Term", "Meaning"],
        [["Base", "How many plates a part in a relief stands proud of the backdrop"],
         ["Bridge", "The local program that serves the page and runs the renderer"],
         ["Closure", "The set of files reached by following every reference from a starting part"],
         ["Course", "One horizontal layer of a standing build"],
         ["Frame", "The outline brought in from a Sangala Studio design, built against but never built"],
         ["LDraw unit", "0.4 mm. A stud is 20, a plate 8, a brick 24"],
         ["Parked", "Placed on the cork beside the plate: kept, but not part of the design"],
         ["Plate", "A part one third the height of a brick"],
         ["Primitive", "A shared shape that parts are built from, rather than a part itself"],
         ["Relief", "A design built up from a backdrop, seen face on"],
         ["Standing", "A design stacked in courses, seen from the side"],
         ["Stud", "The 8 mm module everything is measured in"]],
        weights=[24, 76])

d.heading("Appendix A. Other Platforms")
d.body("The page runs unchanged on macOS, on Linux and on a Chromebook. What does not is the bridge, "
       "which is a Windows executable. Sangala Studio met the same problem and answered it with one "
       "Python file serving both macOS and the Chromebook. The same answer applies here: because the "
       "bridge only receives text, runs a program and returns an image, it transcribes rather than being "
       "reimplemented.")
d.body("Three facts govern that work. LDView is published for Windows, macOS and Linux, so the renderer "
       "is not the obstacle. ChromeOS runs a program of this kind only inside its Linux development "
       "environment, which on a school-managed device is the administrator's setting and on a personally "
       "owned one is the owner's. And every prebuilt LDView for Linux targets Intel processors, so an ARM "
       "Chromebook would require it to be compiled.")

print(d.save(OUT, "Tech Manual"))
