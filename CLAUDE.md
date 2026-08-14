# Sangala Block Designer — project guide for Claude Code

A browser tool for planning a LEGO kit. The outline of a figure designed in **Sangala Studio** is
brought in as a **frame** — a guide, not extruded geometry — and the student builds that figure by
placing real LEGO bricks against it, choosing every part by hand. Each brick carries the design
number it is ordered by, so a finished design is also its own parts list. Built for the same course
and the same schools as Sangala Studio and Sangala Mosaic.

## THERE ARE THREE APPLICATIONS. THEY ARE SEPARATE. (Glen, 2026-08-11)
**Sangala Studio** (`D:\Code Projects\Silhouette Tools`), **Sangala Mosaic** (`D:\Code Projects\Mosaic`)
and **Sangala Block Designer** (here) are three separate applications, deliberately — each in its own
folder, its own repo, its own history. They share a look and feel and may borrow code.

- **BORROWING IS ONE-WAY: READ Studio and Mosaic, WRITE only here.** Their files are reference. A
  correction Glen makes while looking at Block Designer belongs to Block Designer, whatever file
  happens to be open or reachable.
- **SANGALA STUDIO IS PUT TO BED. Do not change `SangalaStudio.html` or its `.cs` engine — not a
  refinement, not a defect fix, not a version bump — without Glen asking for that change in that
  program.** The book, the User Guide (9.0) and the Tech Manual (3.6) all document Studio as it
  stands, and all three are finished. An unrequested change there can force a rewrite of documents
  that are already published. On 2026-08-11 an icon correction meant for the menu below was committed
  to Studio's `#partmenu` instead and shipped; it had to be reverted.
- **If the file that should change is out of reach, say so and stop.** Never edit a reachable file in
  place of the right one.

## Shared design vocabulary (Glen's inviolable rule, 2026-08-11)
**The same icon means the same thing in all three applications.** An icon used for a 2D/3D toggle in
one may not stand for something else in another, wherever it is placed. Before inventing a control,
find the one the other two already use, and copy it — the plan view's own language, not a new
convention. "Why do you persist in reinventing the wheel?" is the standing correction.

## What is here
- **`SangalaBlockDesigner.html`** — the whole application, one self-contained file. Menu bar, left
  Toolbar (Select / Place / Erase / Flip, then Show: Frame, Grid), parts panel on the right.
  **The column of tools on the left is the TOOLBAR. Never "rail" (Glen, Part 19, 2026-08-11).** The
  applications already say so — the status line reads "Pick a part from the Toolbar" — and the word
  "rail" appears nowhere in this file. It was my coinage, it survived only in my own writing, and it
  reached the first draft of the Sangala Tools Technical Manual because the agreement was never
  written down. The regions are: menu bar across the top, Toolbar down the left, workspace in the
  middle, control panel on the right.
- **`Crane.ico`** — the application icon, a crowned crane built from bricks, made the way Mosaic's
  turaco was made. Studio = buffalo, Mosaic = turaco, Block Designer = crane.
- **`Crane 8.model`** — a Studio model kept beside the application as a sample frame to import.

## Facts about the program
- Its own file extension is **`.block`**; it also opens Studio's **`.model`** to take a frame from it.
- The part flyout is **Studio's `#partmenu` pattern** — a kind menu (Brick, Plate, Slope, Inverted
  Slope) with a size submenu beside it, opening at the Toolbar's right edge.
- Geometry follows LEGO, not the drawing grid: a stud is **8 mm**; bricks are drawn in **side view**,
  studs standing proud above the top face, courses in running bond.
- Nothing is placed automatically. The student picks every part and places it — that is the point of
  the tool, not an implementation detail.

## Where documents go (Glen, 2026-08-14)
A document about this application is published to Dropbox at
`AI Sandbox\Design through Making\Sangala Tools\Sangala Blocks Files\Documents\` — Jo cannot
reach Glen's hard drive, so a file that lives only in this repository has not been delivered.
(The folder was `Sangala Block Design Files` until 2026-08-14, when Glen renamed it to match the
application's new name. **Check the folder still exists before writing into it** — `mkdir -p` silently
recreated the abandoned one behind him while he was renaming it.)
**Publishing is part of writing the document, not a later step, and it is not something to ask about.**
Note the `Documents` SUBFOLDER: Glen made it and moved the first two files into it. (Studio's own
folder still keeps its documents at the top level with an empty `Documents` beside them; do not
"tidy" that — it is his to change.) A copy stays in this repository's `Documents\`, with superseded
versions in `Documents\Archive\`, and the two names are kept identical: he renamed
*Adding LEGO Parts to Sangala Blocks* to **Adding LEGO Blocks** and the repository copy follows.

## Process
Glen's global rules in `C:\Users\glenb\.claude\CLAUDE.md` apply here in full: be concise, ask inline
one question at a time, do exactly what was asked, one change at a time then let it be tested then
commit, American spelling, "application" never "app", and never the word "honest".
