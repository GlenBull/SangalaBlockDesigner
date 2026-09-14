/* HOW LONG THE PIXEL-BY-PIXEL RENDERER TAKES. Opens the page in a windowless Chromium behind the
   stand-in bridge, loads a design with its real meshes, turns the 3D View on at a laptop-sized
   window, and times the three things building in that view would lean on: one frame of
   renderPreview (an orbit step), one rebuild of the triangle list (what every edit forces), and
   one whole edit through draw(). Prints the numbers; changes nothing.
       node tools/measure_render.js [design.block] [width] [height] [--old]
   --old times the JavaScript renderer; without it the graphics card draws, as the application does.
   In a windowless Chromium the graphics card is SwiftShader, a CPU stand-in, so the graphics-card
   numbers here say the path works and nothing about a real card.
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
  const args = process.argv.slice(2), old = args.includes("--old"), rest = args.filter(a => a !== "--old");
  const design = rest[0] || path.join(__dirname, "..", "Projects", "Crane.block");
  const W = +rest[1] || 1600, H = +rest[2] || 900;
  const port = await new Promise(r => start(0, r));
  const browser = await playwright().chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on("pageerror", e => console.error("page error:", e.message));
  await page.goto(`http://127.0.0.1:${port}/${old ? "?renderer=js" : ""}`);   /* the page opens in the 3D View; the address chooses the renderer before its first frame */
  await page.setInputFiles("#fOpen", design);
  await page.waitForFunction(() => bricks.length > 0);
  /* every part asked for has arrived: the fetches in flight are counted, and a mesh still on its way is null */
  await page.waitForFunction(() => Object.keys(ldrMesh).length > 0 && ldrWaiting === 0
                                   && Object.values(ldrMesh).every(v => v !== null), null, { timeout: 180000 });
  const r = await page.evaluate((N) => {
    const med = a => { const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
    const time = f => { const t0 = performance.now(); f(); return performance.now() - t0; };
    syncView3D(true);
    /* the card works on after the call returns, so a frame is timed to the moment a pixel can be read
       back, which waits for it; gl.finish() does not wait in Chromium. The JavaScript renderer is
       finished when it returns. */
    const px = new Uint8Array(4);
    const done = () => { if(typeof gl !== "undefined" && gl) gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
    const frames = []; for(let i = 0; i < N; i++){ pvYaw += 0.02; frames.push(time(() => { renderPreview(); done(); })); }
    const rebuilds = []; for(let i = 0; i < 5; i++)
      rebuilds.push(time(() => pvSetTris(Object.assign(bricksToTris(), { guides: frameToGuideTris() }))));
    const edits = []; for(let i = 0; i < 5; i++){ bricks[0].col += 1; edits.push(time(() => { draw(); done(); })); bricks[0].col -= 1; draw(); }
    const pv = document.getElementById("pv");
    const renderer = (typeof gl !== "undefined" && gl) ? (gl.getExtension("WEBGL_debug_renderer_info") ? gl.getParameter(gl.getExtension("WEBGL_debug_renderer_info").UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)) : "none";
    return { w: pv.width, h: pv.height, tris: pvTris.length, bricks: bricks.filter(b => !parked(b)).length, renderer,
             frame: med(frames), frameMin: Math.min(...frames), frameMax: Math.max(...frames),
             rebuild: med(rebuilds), edit: med(edits), absent: [...ldrAbsent], partial: [...ldrPartial] };
  }, 10);
  await browser.close();
  const ms = v => v.toFixed(0) + " ms";
  console.log(`${old ? "JavaScript renderer" : "graphics card (" + r.renderer + ")"}: window ${W} x ${H}, 3D canvas ${r.w} x ${r.h}, ${r.bricks} bricks, ${r.tris} triangles`);
  console.log(`one frame (orbit step)      ${ms(r.frame)}   (min ${ms(r.frameMin)}, max ${ms(r.frameMax)})`);
  console.log(`one rebuild of the triangles ${ms(r.rebuild)}`);
  console.log(`one edit through draw()      ${ms(r.edit)}`);
  if(r.absent.length)  console.log("parts with no geometry: " + r.absent.join(", "));
  if(r.partial.length) console.log("parts missing subfiles: " + r.partial.join(", "));
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
