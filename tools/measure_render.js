/* HOW LONG THE PIXEL-BY-PIXEL RENDERER TAKES. Opens the page in a windowless Chromium behind the
   stand-in bridge, loads a design with its real meshes, turns the 3D View on at a laptop-sized
   window, and times the three things building in that view would lean on: one frame of
   renderPreview (an orbit step), one rebuild of the triangle list (what every edit forces), and
   one whole edit through draw(). Prints the numbers; changes nothing.
       node tools/measure_render.js [design.block] [width] [height]
   Needs the LDraw folder beside the application and the Playwright package (global is fine). */
const path = require("path");
const { start } = require("./bridge_stub.js");
function playwright(){
  try { return require("playwright"); }
  catch(e){
    const g = require("child_process").execSync("npm root -g").toString().trim();
    return require(path.join(g, "playwright"));
  }
}
(async () => {
  const design = process.argv[2] || path.join(__dirname, "..", "Projects", "Crane.block");
  const W = +process.argv[3] || 1600, H = +process.argv[4] || 900;
  const port = await new Promise(r => start(0, r));
  const browser = await playwright().chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on("pageerror", e => console.error("page error:", e.message));
  await page.goto(`http://127.0.0.1:${port}/`);
  await page.setInputFiles("#fOpen", design);
  await page.waitForFunction(() => bricks.length > 0);
  await page.click("#bView3D");
  /* every part asked for has arrived: the fetches in flight are counted, and a mesh still on its way is null */
  await page.waitForFunction(() => Object.keys(ldrMesh).length > 0 && ldrWaiting === 0
                                   && Object.values(ldrMesh).every(v => v !== null), null, { timeout: 180000 });
  const r = await page.evaluate((N) => {
    const med = a => { const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
    const time = f => { const t0 = performance.now(); f(); return performance.now() - t0; };
    syncView3D(true);
    const frames = []; for(let i = 0; i < N; i++){ pvYaw += 0.02; frames.push(time(() => renderPreview())); }
    const rebuilds = []; for(let i = 0; i < 5; i++)
      rebuilds.push(time(() => pvSetTris(Object.assign(bricksToTris(), { guides: frameToGuideTris() }))));
    const edits = []; for(let i = 0; i < 5; i++){ bricks[0].col += 1; edits.push(time(() => draw())); bricks[0].col -= 1; draw(); }
    const pv = document.getElementById("pv");
    return { w: pv.width, h: pv.height, tris: pvTris.length, bricks: bricks.filter(b => !parked(b)).length,
             frame: med(frames), frameMin: Math.min(...frames), frameMax: Math.max(...frames),
             rebuild: med(rebuilds), edit: med(edits), absent: [...ldrAbsent], partial: [...ldrPartial] };
  }, 10);
  await browser.close();
  const ms = v => v.toFixed(0) + " ms";
  console.log(`window ${W} x ${H}, 3D canvas ${r.w} x ${r.h}, ${r.bricks} bricks, ${r.tris} triangles`);
  console.log(`one frame (orbit step)      ${ms(r.frame)}   (min ${ms(r.frameMin)}, max ${ms(r.frameMax)})`);
  console.log(`one rebuild of the triangles ${ms(r.rebuild)}`);
  console.log(`one edit through draw()      ${ms(r.edit)}`);
  if(r.absent.length)  console.log("parts with no geometry: " + r.absent.join(", "));
  if(r.partial.length) console.log("parts missing subfiles: " + r.partial.join(", "));
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
