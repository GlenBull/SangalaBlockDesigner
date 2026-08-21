# Insert the nine section headings + instruction paragraphs into the snapshot booklet
# saved by Sangala Blocks, and relabel each "Step N" with its sub-step letter.
# Usage: python add_instructions.py <in.docx> <out.docx>
import zipfile, sys, os

src, dst = sys.argv[1], sys.argv[2]

SECTS = [
 (1, "Section 1. Assemble the Head and Crown",
  "1.a. Place the black 1 x 3 plate on top of the black 1 x 2 brick. "
  "1.b. Then add the red bill. "
  "1.c. Place the white 1 x 1 round plate at the front of the black brick behind the red bill to form the right-hand eye of the crane. "
  "1.d. Then add a second 1 x 1 round plate to the other side to form the left-hand eye. "
  "1.e. Then add the three crown pieces to the top of the head with the cone in the center. "
  "1.f. This completes the crown and head assembly."),
 (6, "Section 2. Assemble the Body",
  "2.a. Place two dark gray 2 x 4 side-stud bricks side by side to form the core of the body. "
  "2.b. Add a blue 2 x 4 plate to the side studs on the front of the body. "
  "2.c. Then add the second blue 2 x 4 plate to the side studs on the back. "
  "2.d. Add a yellow 2 x 3 plate to the front of the body, over the blue plate. "
  "2.e. Then add the second yellow 2 x 3 plate to the back in the same position. "
  "2.f. This completes the body assembly."),
 (11, "Section 3. Assemble the Back",
  "3.a. Place the dark gray 2 x 4 brick on top of the body. "
  "3.b. Place a pair of dark gray 3 x 1 slope bricks, one in front of the other, at the tail. "
  "3.c. Add a second pair of 3 x 1 slope bricks one step up the back. "
  "3.d. Add a third pair of 3 x 1 slope bricks to form the next step. "
  "3.e. Finish with a pair of steeper dark gray 2 x 1 slope bricks at the top of the back, where the neck will stand. "
  "3.f. This completes the back assembly."),
 (17, "Section 4. Assemble the Wings",
  "4.a. Place a light gray 2 x 2 slope brick at the upper root of the large curved wedge that forms the right wing. "
  "4.b. Add a second 2 x 2 slope brick at the lower root. "
  "4.c. This completes the right wing, with all studs facing forward. "
  "4.d. Assemble the left wing from the same three pieces as a mirror image, with all studs facing away: place one slope brick at the upper root of the wedge. "
  "4.e. Add the second slope brick at the lower root. "
  "4.f. This completes both wings."),
 (23, "Section 5. Attach the Wings to the Body",
  "5.a. Attach the right wing to the studs of the blue and yellow plates on the front of the body, with the wing sweeping back toward the tail. "
  "5.b. Attach the left wing to the matching plates on the back of the body. "
  "5.c. The wings are now attached."),
 (26, "Section 6. Add the Legs to the Body",
  "6.a. Attach a black 1 x 1 x 3 brick beneath the body to form the rear leg. "
  "6.b. Attach the second 1 x 1 x 3 brick beneath the body to form the front leg. "
  "6.c. This completes the legs."),
 (29, "Section 7. Place the Crane on the Baseplate",
  "7.a. Place the green 8 x 16 plate on the work surface and stand the crane on it, with the legs toward the middle of the plate. "
  "7.b. The crane now stands on the baseplate."),
 (31, "Section 8. Add the Neck",
  "8.a. Attach the light gray 1 x 2 plate with the center stud to the top of the body, in front of the slope bricks of the back. "
  "8.b. Place the tall light gray neck brick on the center stud. "
  "8.c. This completes the neck."),
 (34, "Section 9. Place the Crown and Head on the Neck",
  "9.a. Place the head and crown assembly from Section 1 on top of the neck, with the bill pointing forward. "
  "9.b. The crane is complete."),
]

# Step number -> sub-step label (Section 1 skips 1.d, which has no picture)
LABELS = {}
LABELS.update({1:"1.a",2:"1.b",3:"1.c",4:"1.e",5:"1.f",
 6:"2.a",7:"2.b",8:"2.c",9:"2.d",10:"2.e",
 11:"3.a",12:"3.b",13:"3.c",14:"3.d",15:"3.e",16:"3.f",
 17:"4.a",18:"4.b",19:"4.c",20:"4.d",21:"4.e",22:"4.f",
 23:"5.a",24:"5.b",25:"5.c",
 26:"6.a",27:"6.b",28:"6.c",
 29:"7.a",30:"7.b",
 31:"8.a",32:"8.b",33:"8.c",
 34:"9.a",35:"9.b"})

def xesc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def heading_para(t):
    return ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="60"/></w:pPr>'
            '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/>'
            '<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
            '<w:t xml:space="preserve">'+xesc(t)+'</w:t></w:r></w:p>')

def body_para(t):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="200"/></w:pPr>'
            '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
            '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'
            '<w:t xml:space="preserve">'+xesc(t)+'</w:t></w:r></w:p>')

zin = zipfile.ZipFile(src)
names = zin.namelist()
doc = zin.read("word/document.xml").decode("utf-8")

# sanity: all 35 step labels present exactly once
for n in range(1, 36):
    tok = '>Step %d</w:t>' % n
    if doc.count(tok) != 1:
        raise SystemExit("expected exactly one of %r, found %d" % (tok, doc.count(tok)))

# 1) insert heading + instructions before each section's first step paragraph
for first, title, text in SECTS:
    tok = '>Step %d</w:t>' % first
    pos = doc.index(tok)
    pstart = doc.rindex("<w:p>", 0, pos)
    doc = doc[:pstart] + heading_para(title) + body_para(text) + doc[pstart:]

# 2) relabel the steps (longest numbers first so Step 3 never matches inside Step 30)
for n in sorted(LABELS, reverse=True):
    doc = doc.replace('>Step %d</w:t>' % n, '>' + LABELS[n] + '</w:t>')

data = {nm: zin.read(nm) for nm in names}
zin.close()
data["word/document.xml"] = doc.encode("utf-8")

order = ["[Content_Types].xml"] + [nm for nm in names if nm != "[Content_Types].xml"]
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    for nm in order:
        z.writestr(nm, data[nm])
print("wrote", dst, os.path.getsize(dst), "bytes")
