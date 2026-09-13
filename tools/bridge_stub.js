/* A STAND-IN FOR THE BRIDGE, so the page can be driven where there is no Windows, no .NET and no
   LDView: it serves the page and answers /status and /part the way SangalaBlocksServer.cs does,
   reading the same LDraw folder through the same file gathering the geometry check uses. /snapshot
   answers that there is no LDView here. It holds no copy of the page's geometry; it only hands the
   page the files the real bridge would.
       node tools/bridge_stub.js [port]      serves on 127.0.0.1:port (default 8765)
   Used by tools/measure_render.js, and by hand for a headless look at the 3D view. */
const http = require("http"), fs = require("fs"), path = require("path");
const { gather } = require("./geom_harness.js");
const ROOT = path.join(__dirname, "..");
const PAGE = path.join(ROOT, "SangalaBlockDesigner.html");

/* the bridge's own test for a name that arrived over a socket, before it becomes a path */
function safeName(n){
  if(!n || n.length > 80) return false;
  if(n.includes("..") || n.includes(":")) return false;
  if(n[0] === "\\" || n[0] === "/") return false;
  return /^[A-Za-z0-9._\-\\/]+$/.test(n);
}
const partKey = n => (n || "").trim().replace(/\\/g, "/").toLowerCase();

/* the part and every file it references, breadth first, "" for one that is not in the folder */
function partJSON(want){
  if(!/\.dat$/i.test(want)) want += ".dat";
  if(!safeName(want)) return null;
  const files = {};
  gather(want, files, 0);
  return JSON.stringify({ name: partKey(want), files });
}

function start(port, ready){
  const srv = http.createServer((req, res) => {
    const u = new URL(req.url, "http://127.0.0.1");
    const send = (code, type, body) => { res.writeHead(code, { "Content-Type": type, "Cache-Control": "no-store" }); res.end(body); };
    if(req.method === "GET" && (u.pathname === "/" || u.pathname === "/index.html"))
      return send(200, "text/html; charset=utf-8", fs.readFileSync(PAGE));
    if(u.pathname === "/status")
      return send(200, "application/json", JSON.stringify({ sangala: "blocks", ldview: false, ldraw: true }));
    if(req.method === "GET" && u.pathname === "/part"){
      const j = u.searchParams.get("f") ? partJSON(u.searchParams.get("f")) : null;
      return j ? send(200, "application/json", j) : send(400, "text/plain", "bad part name");
    }
    if(u.pathname === "/snapshot")
      return send(501, "application/json", JSON.stringify({ ok: false, error: "the stand-in bridge has no LDView" }));
    if(u.pathname === "/quit"){ send(200, "text/plain", "bye"); srv.close(); return; }
    send(404, "text/plain", "not found");
  });
  srv.listen(port, "127.0.0.1", () => ready && ready(srv.address().port, srv));
  return srv;
}
module.exports = { start };

if(require.main === module)
  start(+process.argv[2] || 8765, p => console.log("stand-in bridge on http://127.0.0.1:" + p + "/"));
