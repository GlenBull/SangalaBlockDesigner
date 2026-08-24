"""Take the application's own PLAN snapshots, one per build step, without pressing anything.

WHY THIS EXISTS. The plan view is drawn by the page, not by the bridge, so its pictures live inside
the browser. Sangala Blocks writes them out through a native Save dialog, which is right for a
student and unreachable from a script. The method that solves it is the one already established for
this machine: run the real application in HEADLESS EDGE, append a script to it, and read what that
script leaves in the DOM. Every picture is therefore drawn by the application's own planShotFixed,
at the application's own scale - the same code the Snapshot button runs.

    set PYTHONUTF8=1
    python "D:\\Code Projects\\Block Tools\\tools\\docs\\plan_shots.py" <design.block> <outdir>

It writes step01.png, step02.png ... one per step, and prints what it wrote.
"""
import base64
import json
import os
import re
import subprocess
import sys
import tempfile

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PAGE = r"D:\Code Projects\Block Tools\SangalaBlockDesigner.html"
SHOT = 900          # long side, in pixels, of every picture


def steps_for(design):
    """The order the crane is built in: three sub-assemblies, then put together.

    Each step is a list of INDEXES into the design's bricks - everything placed so far. A step that
    starts a sub-assembly starts from nothing; the assembly steps carry what came before.
    """
    bricks = design["bricks"]

    def gname(b):
        g = b.get("gnames") or []
        return g[0] if g and g[0] else None

    def idx(pred):
        return [i for i, b in enumerate(bricks) if pred(b)]

    head = idx(lambda b: gname(b) == "Head")
    eyes = idx(lambda b: gname(b) == "Eyes")
    crown = idx(lambda b: gname(b) == "Crown")
    beak = idx(lambda b: gname(b) is None and b["id"] == "3040")
    body = idx(lambda b: gname(b) == "Body")
    back = idx(lambda b: gname(b) == "Back")
    wingL = idx(lambda b: gname(b) == "Wing (left)")
    wingR = idx(lambda b: gname(b) == "Wing (right)")
    legs = idx(lambda b: gname(b) == "Legs")
    neck = idx(lambda b: gname(b) == "Neck")
    base = idx(lambda b: b["id"] == "92438")

    out = []

    def run(seq, label):
        """One picture per piece, each showing everything placed so far in this sub-assembly."""
        got = []
        for i in seq:
            got = got + [i]
            out.append({"pieces": list(got), "of": label, "added": i})

    # the head is built first and fitted last
    run(head + beak + eyes + crown, "head")
    run(body + back, "body")
    run(wingL + wingR, "wings")

    # then the pieces are brought together, carrying everything already placed
    torso = body + back
    out.append({"pieces": torso + wingL + wingR, "of": "join", "added": None})
    out.append({"pieces": torso + wingL + wingR + legs, "of": "join", "added": None})
    out.append({"pieces": torso + wingL + wingR + legs + base, "of": "join", "added": None})
    out.append({"pieces": torso + wingL + wingR + legs + base + neck, "of": "join", "added": None})
    out.append({"pieces": list(range(len(bricks))), "of": "join", "added": None})
    return out


HARNESS = r"""
<script>
(function(){
  var DESIGN = __DESIGN__;
  var STEPS  = __STEPS__;
  var SHOT   = __SHOT__;
  function ci(code){ for(var i=0;i<COLORS.length;i++) if(COLORS[i].code===code) return i; return 0; }
  function mk(b){
    return { p:{id:b.id,name:b.name,w:b.w,d:b.d||1,h:b.h,shape:b.shape,side:b.side,top:b.top},
             colorIdx: ci(b.color), col:b.col, row:b.row, flip:b.flip, base:b.base,
             turn:b.turn, rot:b.rot, half:b.half,
             gpath:b.gpath, gnames:b.gnames };
  }
  setTimeout(function(){
    var out=[], all=DESIGN.bricks.map(mk);
    try{
      mode = DESIGN.mode || "standing";
      for(var s=0;s<STEPS.length;s++){
        bricks = STEPS[s].pieces.map(function(i){ return all[i]; });
        selBrick=null; selMulti=[]; hover=null;
        view.zoom=1; view.panX=0; view.panY=0;
        draw();
        var t = planShotFixed(SHOT);
        out.push(t ? t.toDataURL("image/png") : "");
      }
    }catch(e){ out.push("ERROR "+e.message+" "+(e.stack||"")); }
    var pre=document.createElement("pre");
    pre.id="shots";
    pre.textContent = out.join("\n@@\n");
    document.body.appendChild(pre);
  }, 700);
})();
</script>
"""


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    src, outdir = argv[1], argv[2]
    os.makedirs(outdir, exist_ok=True)
    design = json.load(open(src, encoding="utf-8"))
    steps = steps_for(design)

    html = open(PAGE, encoding="utf-8").read()
    harness = (HARNESS.replace("__DESIGN__", json.dumps(design))
                      .replace("__STEPS__", json.dumps(steps))
                      .replace("__SHOT__", str(SHOT)))
    html = html.replace("</body>", harness + "</body>")

    tmp = tempfile.mkdtemp(prefix="sangala_shots_")
    page = os.path.join(tmp, "shots.html")
    open(page, "w", encoding="utf-8").write(html)

    # --headless=OLD for --dump-dom: the new headless returns an empty or hung dump on this machine.
    cmd = [EDGE, "--headless=old", "--disable-gpu", "--no-sandbox",
           "--user-data-dir=" + os.path.join(tmp, "profile"),
           "--window-size=1500,1000", "--virtual-time-budget=20000",
           "--dump-dom", "file:///" + page.replace("\\", "/")]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    dom = res.stdout

    m = re.search(r'<pre id="shots">(.*?)</pre>', dom, re.S)
    if not m:
        print("no shots came back; the harness did not run", file=sys.stderr)
        print(res.stderr[-800:], file=sys.stderr)
        return 2
    body = m.group(1)
    body = body.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    urls = body.split("\n@@\n")
    if urls and urls[0].startswith("ERROR"):
        print(urls[0][:600], file=sys.stderr)
        return 3

    wrote = []
    for i, u in enumerate(urls):
        u = u.strip()
        if not u.startswith("data:image/png;base64,"):
            print("step %02d: EMPTY" % (i + 1), file=sys.stderr)
            continue
        raw = base64.b64decode(u.split(",", 1)[1])
        f = os.path.join(outdir, "step%02d.png" % (i + 1))
        open(f, "wb").write(raw)
        wrote.append((i + 1, steps[i]["of"], len(steps[i]["pieces"]), len(raw)))
    for n, of, k, size in wrote:
        print("step %02d  %-6s %2d pieces  %6d bytes" % (n, of, k, size))
    print("%d of %d steps written to %s" % (len(wrote), len(steps), outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
