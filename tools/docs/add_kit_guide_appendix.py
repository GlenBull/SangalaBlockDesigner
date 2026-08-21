"""Add the checklist appendix to the LEGO Kit Style Guide, IN PLACE.

Ver 1.1 was edited by hand in Word (the left margins of the table's second and third
columns), so the guide can no longer be rebuilt from make_kit_style_guide.py without
destroying that work. This patches the file instead: it reads a version, appends the
appendix, and writes the next version, leaving every other part of the package byte for
byte as Word wrote it.

    python add_kit_guide_appendix.py "<in.docx>" "<out.docx>"

It is NOT idempotent - running it twice appends the appendix twice - so it refuses a file
that already carries one. The paragraph XML deliberately matches what Word left behind:
no rFonts or sz in the runs, since the font comes from the document defaults, and only
<w:color> on each run.
"""
import os
import sys
import zipfile

APPENDIX_MARK = "Appendix. Checklist for an Assembly Instructions Document"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(text, italic=False, bold=False):
    rpr = "<w:rPr>"
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    rpr += '<w:color w:val="000000"/></w:rPr>'
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(text))


def runs(parts):
    """parts is a string, or a list of (text, italic, bold)."""
    if isinstance(parts, str):
        parts = [(parts, False, False)]
    return "".join(run(t, italic=i, bold=b) for (t, i, b) in parts)


def heading(text, page_break=False):
    """Bold, kept with what follows - the same pPr Word holds for the guide's headings."""
    ppr = "<w:pPr>"
    if page_break:
        ppr += "<w:pageBreakBefore/>"
    ppr += '<w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="60"/></w:pPr>'
    return "<w:p>%s%s</w:p>" % (ppr, runs([(text, False, True)]))


def body(parts, after=100):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="%d"/></w:pPr>%s</w:p>'
            % (after, runs(parts)))


def check(parts):
    """One checklist line. The box is a plain character, so nothing has to be inserted by
    hand and the list can be ticked on paper or on screen.

    THE INDENT HANGS, so a line that wraps aligns under the text rather than under the box -
    without it a two-line check reads as two separate checks, one of them missing its box.
    Three points after, which is the house spacing for a list item.
    """
    if isinstance(parts, str):
        parts = [(parts, False, False)]
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="60"/>'
            '<w:ind w:left="320" w:hanging="320"/></w:pPr>%s</w:p>'
            % runs([("□  ", False, False)] + list(parts)))


BLOCKS = ("Sangala Blocks", True, False)

APPENDIX = []
APPENDIX.append(heading(APPENDIX_MARK, page_break=True))
APPENDIX.append(body([
    ("The checks below are applied to a kit document before it is delivered. Each is a "
     "statement that must be true of the document; one that is not true marks work still "
     "to be done. They cover assembly instructions for a LEGO kit, which are written from "
     "a design made in ", False, False),
    BLOCKS, (".", False, False)]))

APPENDIX.append(heading("The Document as a Whole"))
for t in [
    "The opening names the kit, those who made it, and where the figure came from.",
    "The opening says how the parts are divided into bags.",
    "The names of the applications and of the kit are set in italic.",
    "Sections are numbered and run in the order the builder works.",
    "An element assembled away from the figure is built in one section and attached in another.",
]:
    APPENDIX.append(check(t))

APPENDIX.append(heading("Every Section"))
for t in [
    "The heading is a number and a short noun phrase, each word capitalized except the minor ones.",
    "The section opens with one sentence naming its bag.",
    "The bag named is the bag the section actually uses.",
    "The steps are a lettered list, one action to a line.",
    "Each step names a part and says where the part goes.",
    "Left and right are given from the reader's view of the figure.",
    "The last step tells the builder what the finished element should look like and points to "
    "the picture that shows it.",
]:
    APPENDIX.append(check(t))

APPENDIX.append(heading("Naming the Parts"))
for t in [
    "Each part is named in italic, with each word capitalized, where it is first used in a section.",
    "Dimensions are written with spaces around the multiplication sign: 1 x 3, not 1x3.",
    "A brick carrying studs on its side is called a side-stud brick.",
]:
    APPENDIX.append(check(t))

APPENDIX.append(heading("The Pictures"))
APPENDIX.append(check([("Every picture is a Plan View snapshot taken in ", False, False),
                       BLOCKS, (".", False, False)]))
for t in [
    "Pictures sit in a strip after the steps they illustrate, not between them.",
    "Each picture carries the letter of its step beneath it at the left, lowercase and not bold.",
    "All the pictures in a strip are set to the same height.",
    "Every step whose action can be shown has a picture, and a step whose action cannot be shown "
    "is worded so that it needs none.",
    "In every picture the part being added is selected, and the parts already placed are seated.",
    "A section that builds a sub-assembly shows only that element's parts.",
    "An element joining the figure is shown hovering at its destination, then seated.",
]:
    APPENDIX.append(check(t))

# The last group starts its own page. Left to fall where it lands, two of its checks spilled
# onto a page that then held nothing else, which reads as broken. A whole group on the page is
# the right break.
APPENDIX.append(heading("The Finished File", page_break=True))
for t in [
    "Body text is Times New Roman 11 pt, black.",
    "A page number sits at the bottom center of every page.",
    "No heading stands alone at the foot of a page.",
    "No table splits across a page break.",
    "Spelling is American throughout.",
    "No version number appears inside the document.",
    "The version this one supersedes has been moved to the Archive folder.",
]:
    APPENDIX.append(check(t))

XML = "".join(APPENDIX)


def main(src, dst):
    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    doc = zin.read("word/document.xml").decode("utf-8")

    if APPENDIX_MARK in doc:
        raise SystemExit("refusing: %s already carries the appendix" % os.path.basename(src))

    cut = doc.rfind("<w:sectPr")
    if cut < 0:
        raise SystemExit("refusing: no final sectPr found")
    if doc.rfind("</w:p>") > cut:
        raise SystemExit("refusing: a paragraph closes after the final sectPr")

    out = doc[:cut] + XML + doc[cut:]

    data = {n: zin.read(n) for n in names}
    zin.close()
    data["word/document.xml"] = out.encode("utf-8")

    order = ["[Content_Types].xml"] + [n for n in names if n != "[Content_Types].xml"]
    with zipfile.ZipFile(dst, "x", zipfile.ZIP_DEFLATED) as z:
        for n in order:
            z.writestr(n, data[n])
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
