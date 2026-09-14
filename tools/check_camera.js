/* THE CAMERA, FORWARD AND BACK, WITHOUT A BROWSER. pvProject sends a model point to the screen and
   a depth; pvUnproject brings the screen point and the depth back; pvOnPlane meets the line of
   sight with a plane. For a thousand cameras and points this asks that a point comes back where
   it started, that a point on a plane is found on it, and that the line of sight runs the way
   depth increases. Any of them wrong and building in the 3D View would place a part somewhere
   other than where the pointer touched.
       node tools/check_camera.js */
const { load } = require("./geom_harness.js");
const G = load();
let bad = 0, seed = 12345;
const rnd = () => { seed = (seed*1103515245 + 12345) & 0x7fffffff; return seed/0x7fffffff; };
const near = (a, b, tol) => Math.abs(a - b) <= tol;
for(let i = 0; i < 1000; i++){
  const yaw = (rnd()*2 - 1)*Math.PI, pitch = (rnd()*2 - 1)*1.45;
  const cam = {ca: Math.cos(yaw), sa: Math.sin(yaw), ce: Math.cos(pitch), se: Math.sin(pitch),
               scale: 0.5 + rnd()*20, cx: rnd()*1600, cy: rnd()*900, C: [rnd()*400 - 200, rnd()*400 - 200, rnd()*400 - 200]};
  const P = [rnd()*600 - 300, rnd()*600 - 300, rnd()*600 - 300];
  const s = G.pvProject(P, cam), Q = G.pvUnproject(s[0], s[1], s[2], cam);
  if(!near(Q[0], P[0], 1e-7) || !near(Q[1], P[1], 1e-7) || !near(Q[2], P[2], 1e-7)){ bad++; if(bad < 5) console.log("round trip", P, "came back", Q); continue; }
  /* the line of sight: a point one unit deeper projects to the same screen point */
  const v = [cam.ce*cam.sa, cam.ce*cam.ca, -cam.se];
  const s2 = G.pvProject([P[0] + v[0], P[1] + v[1], P[2] + v[2]], cam);
  if(!near(s2[0], s[0], 1e-7) || !near(s2[1], s[1], 1e-7) || !near(s2[2], s[2] + 1, 1e-7)){ bad++; if(bad < 5) console.log("line of sight", s, s2); continue; }
  /* a plane through P: found on it */
  let n = [rnd()*2 - 1, rnd()*2 - 1, rnd()*2 - 1]; const nl = Math.hypot(n[0], n[1], n[2]) || 1; n = n.map(a => a/nl);
  const nv = n[0]*v[0] + n[1]*v[1] + n[2]*v[2];
  const H = G.pvOnPlane(s[0], s[1], P, n, cam);
  if(Math.abs(nv) < 1e-3){ if(H !== null && Math.abs(nv) < 1e-9){ bad++; console.log("edge-on plane answered"); } continue; }
  if(!H || !near(H[0], P[0], 1e-6) || !near(H[1], P[1], 1e-6) || !near(H[2], P[2], 1e-6)){ bad++; if(bad < 5) console.log("plane", P, "met at", H); }
}
console.log(bad ? bad + " camera checks failed" : "all camera checks pass: 1000 cameras, forward, back and onto a plane");
process.exit(bad ? 1 : 0);
