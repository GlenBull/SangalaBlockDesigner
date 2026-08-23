"""Build the ELEMENT_ID table in SangalaBlockDesigner.html from the validated element ID list.

A LEGO Pick a Brick order is a CSV of elementId,quantity - LEGO's own template - and an
element ID names shape AND color, so it cannot be derived from anything the application
ships. The source is Rebrickable's elements table (downloaded once, with Glen's approval,
2026-08-22, to _Drafts\\Working\\Rebrickable); its trustworthiness was tested against the
24 rows of Jo Watts's real LEGO order before anything was built on it: zero errors in the
list, and it exposed five wrong-color lines in the order itself.

Scope: every part number the application can place (read out of the page's own KINDS and
SIZES tables, bundle_parts.py's rule - a list typed here stops matching the day a part is
added) plus every part named by a library in the repository, crossed with the palette's
colors (read out of the page's COLORS table). For each pair the NEWEST element is taken,
except where a real order proved the store sells an older one - those overrides are listed
below with their provenance.

The acceptance test runs on every build and the table is not written unless it passes:
the 19 rows of Jo's order that carried correct element IDs must be reproduced exactly,
and for the 5 rows his sheet miscopied, the pick must be a real element of the color his
color column names.

    python tools\\elements_table.py
"""
import csv
import gzip
import io
import json
import os
import re
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(REPO, "SangalaBlockDesigner.html")
DUMPS = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts\Working\Rebrickable"

# The store sells these older elements. The first two are proven by Jo's accepted order
# (2026-08-22); the white round plate was proven the other way round - Pick a Brick rejected
# the newest element 6601919 on Glen's real upload (2026-08-23, "currently unavailable"), and
# 614101 is the only other element the part has ever had in white.
OVERRIDES = {("3020", 1): "302023", ("48933", 71): "6030235", ("4073", 15): "614101"}

# LDraw number -> LEGO design number, where the two catalogs renamed the same part. Verified
# on Jo's sheets (2026-08-22); without the bridge the cone's current elements are invisible,
# because they live under 59900 in the element ID list while the page calls the part 4589.
PART_ALIASES = {"4073": "6141", "4589": "59900", "2456": "44237", "3007": "93888"}

# Jo's 24 rows: (page part id, our LDraw color code, expected element, exact).
# exact=True: the store accepted this very element. exact=False: his sheet miscopied the
# element (wrong color); the expectation is any real element of the color his sheet NAMES.
JO_ROWS = [
    ("4589", 14, "4525464", True), ("3665", 14, "366524", True), ("3004", 0, "300426", False),
    ("4073", 15, "614101", False), ("3623", 0, "362326", False), ("3040", 4, "4121934", True),
    ("2453b", 71, "4211362", True), ("15573", 71, "6066097", True), ("3001", 72, "4211085", True),
    ("4286", 72, "4211045", True), ("2434", 0, "4494850", True), ("3021", 14, "302124", False),
    ("3020", 1, "302023", True), ("48933", 71, "6030235", True), ("3039", 71, "4211410", False),
    ("14716", 0, "6065496", True), ("92438", 2, "4610602", True), ("3660", 72, "4211000", True),
    ("2752", 72, "6533357", True), ("86876", 0, "6475339", True), ("47905", 0, "4214559", True),
    ("11211", 72, "6230233", True), ("3004", 72, "4211088", True), ("87087", 71, "4558953", True),
]


def page_ids(src):
    ids = set()
    for name in ("KINDS", "SIZES"):
        block = re.search(r"const %s = \{.*?\n\};" % name, src, re.S) or re.search(r"const %s = \{.*?\};" % name, src, re.S)
        if not block:
            continue
        for m in re.finditer(r'"(\d{3,6}[a-z]?)"', block.group(0)):
            ids.add(m.group(1))
        for m in re.finditer(r'id:"(\d{3,6}[a-z]?)"', block.group(0)):
            ids.add(m.group(1))
    return ids


def library_ids():
    ids = set()
    for folder in ("Projects", "Parts"):
        d = os.path.join(REPO, folder)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            if not n.lower().endswith((".parts", ".library", ".kit")):
                continue
            try:
                lib = json.load(open(os.path.join(d, n), encoding="utf-8"))
            except Exception:
                continue
            for p in lib.get("parts", []):
                if p.get("id"):
                    ids.add(str(p["id"]))
            for s in lib.get("sections", []):
                for r in s.get("rows", []):
                    if r.get("id"):
                        ids.add(str(r["id"]))
    return ids


def palette(src):
    block = re.search(r"const COLORS = \[.*?\n\];", src, re.S).group(0)
    return re.findall(r'code:(\d+),name:"([^"]+)"', block)


def main():
    src = open(HTML, encoding="utf-8").read()
    ids = sorted(page_ids(src) | library_ids())
    cols = palette(src)
    print("parts in scope: %d   palette colors: %d" % (len(ids), len(cols)))

    with gzip.open(os.path.join(DUMPS, "colors.csv.gz"), "rt", encoding="utf-8") as f:
        rb_by_name = {c["name"]: c["id"] for c in csv.DictReader(f)}
    unmapped = [n for _, n in cols if n not in rb_by_name]
    if unmapped:
        raise SystemExit("palette colors with no match in the element ID list: " + ", ".join(unmapped))

    by_pc = defaultdict(set)
    with gzip.open(os.path.join(DUMPS, "elements.csv.gz"), "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_pc[(row["part_num"], row["color_id"])].add(row["element_id"])
            if row.get("design_id"):
                by_pc[("D:" + row["design_id"], row["color_id"])].add(row["element_id"])

    def elements_for(pid, rb_color):
        stem = re.sub(r"[a-z]+$", "", pid)
        cands = {pid, stem} | {stem + s for s in "abcd"}
        alias = PART_ALIASES.get(stem)
        if alias:
            cands |= {alias} | {alias + s for s in "abcd"}
        out = set()
        for c in cands:
            out |= by_pc.get((c, rb_color), set())
        out |= by_pc.get(("D:" + stem, rb_color), set())
        if alias:
            out |= by_pc.get(("D:" + alias, rb_color), set())
        return out

    table, pairs = {}, 0
    for pid in ids:
        for code, name in cols:
            found = elements_for(pid, rb_by_name[name])
            if not found:
                continue
            pick = OVERRIDES.get((pid, int(code))) or max(found, key=lambda e: int(e) if e.isdigit() else 0)
            table[pid + "|" + code] = pick
            pairs += 1
    print("pairs with an element: %d" % pairs)

    # ---- the acceptance test: Jo's order, before anything is written
    bad, skipped = [], []
    idset = set(ids)
    for pid, code, expect, exact in JO_ROWS:
        if pid not in idset:
            skipped.append(pid)      # a part the application does not yet offer - Jo's added
            continue                 # stabilizers stay in the row list for the day it does
        got = table.get(pid + "|" + str(code))
        cname = dict((int(c), n) for c, n in cols)[code]
        if exact and got != expect:
            bad.append("%s in %s: table says %s, the store accepted %s" % (pid, cname, got, expect))
        if not exact:
            valid = elements_for(pid, rb_by_name[cname])
            if not got or got not in valid:
                bad.append("%s in %s: pick %s is not an element of that color" % (pid, cname, got))
    if bad:
        for b in bad:
            print("FAIL  " + b)
        raise SystemExit("acceptance test failed - table NOT written")
    if skipped:
        print("rows SKIPPED, parts the application does not yet offer: " + ", ".join(skipped))
    print("acceptance test: %d of Jo's rows pass" % (len(JO_ROWS) - len(skipped)))

    js = "const ELEMENT_ID=" + json.dumps(table, separators=(",", ":"), sort_keys=True) + ";"
    new, n = re.subn(r"(?m)^const ELEMENT_ID=.*?;$", js.replace("\\", "\\\\"), src, count=1)
    if n != 1:
        raise SystemExit("could not find the ELEMENT_ID constant to replace")
    io.open(HTML, "w", encoding="utf-8", newline="\n").write(new)
    print("written into the page: %d entries" % len(table))


if __name__ == "__main__":
    main()
