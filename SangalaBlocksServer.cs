// SangalaBlocksServer.cs -- the local bridge for Sangala Blocks.
//
// It replaces the launcher, which only opened the page in a browser. The page now needs something a
// browser cannot do for it: run LDView. A snapshot has to look like the pictures in a LEGO booklet,
// and that look comes from the LDraw renderer, not from a canvas drawing of our own.
//
// The division of labor is deliberate and is what keeps the Mac and Chromebook versions cheap: THE
// PAGE WRITES THE LDRAW TEXT, THIS BRIDGE ONLY RENDERS IT. Nothing here knows a stud from a plate.
// It receives a model as text, hands it to LDView, and hands the PNG back. The same twenty lines
// transcribe into Python for the platforms that have no .NET, and the geometry stays in one place.
//
// Loopback TcpListener, so no admin and no firewall exception -- Sangala Studio's SangalaServer.cs,
// ported. Compiled in-box with csc (see Build SangalaBlocks.cmd).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace SangalaBlocksApp
{
    static class Server
    {
        static int _port = 0;
        static string _htmlPath;
        static Mutex _onlyOne;

        // A DIFFERENT PORT RANGE FROM SANGALA STUDIO'S 8787-8807, on purpose: a student may have
        // both applications open, designing bricks against a figure they cut on the die cutter, and
        // two bridges fighting over one port would make that look like a defect in whichever
        // started second.
        const int PORT_LO = 8830, PORT_HI = 8850;

        // ---------------------------------------------------------------- LDView
        // The renderer travels WITH the program, in an LDView folder beside it. It used to be found
        // in a folder on Glen's own machine as well, which is how a feature comes to work for its
        // author and nobody else; that fallback is gone, so a copy of this application either
        // carries what it needs or says plainly that it does not. An installed LDView is still
        // accepted, for anyone who already has one.
        static string FindLDView()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string[] candidates =
            {
                Path.Combine(baseDir, "LDView", "LDView64.exe"),
                Path.Combine(baseDir, "LDView", "LDView.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "LDView", "LDView64.exe")
            };
            foreach (var c in candidates) if (File.Exists(c)) return c;
            return null;
        }

        // The parts library, in LDraw\ldraw beside the program. Only the parts this application can
        // actually place are shipped - 150 files and 224 KB, against the full library's 518 MB - and
        // tools/bundle_parts.py is what works out that closure and tracks it. Anyone who has
        // unzipped the whole library over the same folder simply has more than is needed.
        static string FindLDrawDir()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string[] candidates =
            {
                Path.Combine(baseDir, "LDraw", "ldraw"),
                Path.Combine(baseDir, "ldraw")
            };
            // TEST FOR THE PARTS, NOT FOR THE FOLDER. Windows ignores case, so "ldraw" beside the
            // program matched the repository's own `LDraw` folder - which CONTAINS the library
            // rather than being it. LDView took the wrong root, found no parts, drew an empty
            // scene and exited 0: a failure that arrives looking like a success.
            foreach (var c in candidates)
                if (Directory.Exists(Path.Combine(c, "parts")) && Directory.Exists(Path.Combine(c, "p"))) return c;
            return null;
        }

        // Render one model. Returns the PNG bytes, or null with the reason in `err`.
        // The flags are the ones proved in tools/ldr_export.py: edges on, alpha on (so no gray
        // background survives into the document), auto-cropped to the assembly.
        static byte[] Render(string ldrText, string angle, int width, int height, out string err)
        {
            err = null;
            string ldview = FindLDView();
            if (ldview == null) { err = "LDView was not found. It belongs in an LDView folder beside this program."; return null; }
            string ldrawDir = FindLDrawDir();
            if (ldrawDir == null) { err = "The LDraw parts folder was not found beside this program."; return null; }

            string work = Path.Combine(Path.GetTempPath(), "SangalaBlocks");
            Directory.CreateDirectory(work);
            string stem = "snap" + DateTime.Now.Ticks.ToString();
            string ldr = Path.Combine(work, stem + ".ldr");
            string png = Path.Combine(work, stem + ".png");
            // LDraw files are read by tools that expect Unix line endings; write them that way.
            File.WriteAllText(ldr, ldrText.Replace("\r\n", "\n"), new UTF8Encoding(false));

            var psi = new ProcessStartInfo(ldview)
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                // QUOTE THE WHOLE ARGUMENT, not the value inside it. `-LDrawDir="D:\Block Tools\..."`
                // reaches LDView as an option it cannot read, so it finds no parts and writes a
                // cropped-to-nothing image with a successful exit code - a failure that looks
                // exactly like success from out here. `"-LDrawDir=D:\Block Tools\..."` is right.
                Arguments =
                    Q(ldr) +
                    " " + Q("-LDrawDir=" + ldrawDir) +
                    " " + Q("-SaveSnapshot=" + png) +
                    " -SaveWidth=" + width + " -SaveHeight=" + height +
                    " -SaveAlpha=1" +          // transparent: the gray booklet background is not wanted
                    " -AutoCrop=1" +
                    " -ShowEdges=1" +
                    " -ConditionalHighlights=1" +
                    " -SaveActualSize=0" +
                    // A CIRCLE MUST LOOK LIKE A CIRCLE. LDView's own defaults drew the opening in a
                    // 1 x 1 cone as a polygon, and left a visible gap where that rim met the cone
                    // beneath it - both plain in a snapshot beside a photograph of the brick (Glen,
                    // 2026-08-15, again 2026-08-16). BOTH COME FROM THE STUDS, not from the cone:
                    // LDView substitutes its own coarse geometry for every stud, and the rim of an
                    // open stud is what that opening is. The coarse rim is the polygon, and it does
                    // not meet the smooth cone it sits on, so the eye looks through the slot
                    // between them. -UseQualityStuds=1 ends both at once. Curve quality alone does
                    // NOT: it smooths the cone and leaves the stud coarse, which widens the gap.
                    " -AllowPrimitiveSubstitution=1" +
                    " -CurveQuality=12" +
                    " -HiResPrimitives=1" +
                    " -UseQualityStuds=1" +
                    " -Seams=0" +
                    (string.IsNullOrEmpty(angle) ? "" : " -cg" + angle)
            };
            int exitCode = -1;
            try
            {
                using (var p = Process.Start(psi))
                {
                    // LDView is a GUI-subsystem program and prints nothing at all, so silence is not
                    // failure: the test is whether the file appeared. The wait is generous because a
                    // cold start loads the parts library.
                    if (!p.WaitForExit(60000)) { try { p.Kill(); } catch { } err = "LDView did not finish within a minute."; return null; }
                    exitCode = p.ExitCode;
                }
            }
            catch (Exception ex) { err = "LDView could not be started: " + ex.Message; return null; }

            if (!File.Exists(png)) { err = "LDView produced no image. The model may name a part that is not in the parts folder."; return null; }
            byte[] data = File.ReadAllBytes(png);
            // A cropped-to-nothing PNG is a few dozen bytes and looks like success from here. It
            // means LDView drew no brick at all - a model it could not read, or parts it could not
            // find. Say so, and LEAVE THE TWO FILES in place: the model that produced it is the
            // only evidence of why, and deleting it is how the failure becomes unexplainable.
            if (data.Length < 1000)
            {
                err = "LDView drew nothing (a blank image, exit code " + exitCode + "). Command line: " +
                      ldview + " " + psi.Arguments + "  |  the model is kept at " + ldr;
                return null;
            }
            try { File.Delete(ldr); File.Delete(png); } catch { }
            return data;
        }

        static string Q(string s) { return "\"" + s + "\""; }

        // ---------------------------------------------------------------- start-up
        // One bridge per session, and a second double-click opens the page the first one serves --
        // Studio's rule, arrived at after copies piled up in the tray.
        static int FindRunningBridge()
        {
            for (int p = PORT_LO; p <= PORT_HI; p++)
            {
                try
                {
                    using (var c = new TcpClient())
                    {
                        var iar = c.BeginConnect(IPAddress.Loopback, p, null, null);
                        if (!iar.AsyncWaitHandle.WaitOne(120)) continue;
                        c.EndConnect(iar);
                        using (var ns = c.GetStream())
                        {
                            var req = Encoding.ASCII.GetBytes("GET /status HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n");
                            ns.Write(req, 0, req.Length);
                            ns.ReadTimeout = 700;
                            var sb = new StringBuilder();
                            var buf = new byte[512];
                            for (int i = 0; i < 8; i++)
                            {
                                int n;
                                try { n = ns.Read(buf, 0, buf.Length); } catch { break; }
                                if (n <= 0) break;
                                sb.Append(Encoding.ASCII.GetString(buf, 0, n));
                                if (sb.ToString().IndexOf("\"sangala\"", StringComparison.Ordinal) >= 0) break;
                            }
                            if (sb.ToString().IndexOf("\"sangala\"", StringComparison.Ordinal) >= 0) return p;
                        }
                    }
                }
                catch { }
            }
            return 0;
        }

        [STAThread]
        static void Main()
        {
            bool first;
            _onlyOne = new Mutex(true, "SangalaBlocksBridge", out first);
            if (!first)
            {
                int running = FindRunningBridge();
                try { Process.Start("http://localhost:" + (running > 0 ? running : PORT_LO) + "/"); } catch { }
                return;
            }

            _htmlPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "SangalaBlockDesigner.html");
            if (!File.Exists(_htmlPath))
            {
                MessageBox.Show(
                    "SangalaBlockDesigner.html was not found next to this program.\r\n\r\n" +
                    "Keep SangalaBlockDesigner.exe and SangalaBlockDesigner.html together in the same folder.",
                    "Sangala Blocks", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            TcpListener listener = null;
            for (int p = PORT_LO; p <= PORT_HI && listener == null; p++)
            {
                try { var l = new TcpListener(IPAddress.Loopback, p); l.Start(); listener = l; _port = p; }
                catch (SocketException) { }
            }
            if (listener == null) { MessageBox.Show("Could not open a local port (" + PORT_LO + "-" + PORT_HI + ")."); return; }

            var t = new Thread(() => AcceptLoop(listener)) { IsBackground = true };
            t.Start();

            try { Process.Start("http://localhost:" + _port + "/"); } catch { }

            Application.EnableVisualStyles();
            Application.Run(new TrayContext(_port));
        }

        static void AcceptLoop(TcpListener listener)
        {
            while (true)
            {
                TcpClient c = null;
                try { c = listener.AcceptTcpClient(); }
                catch { break; }
                var client = c;
                ThreadPool.QueueUserWorkItem(_ => { try { Handle(client); } catch { } });
            }
        }

        // ---------------------------------------------------------------- minimal HTTP
        static void Handle(TcpClient client)
        {
            using (client)
            using (var ns = client.GetStream())
            {
                var head = new MemoryStream();
                int b; int matched = 0;
                while ((b = ns.ReadByte()) != -1)
                {
                    head.WriteByte((byte)b);
                    if ((matched == 0 || matched == 2) && b == '\r') matched++;
                    else if ((matched == 1 || matched == 3) && b == '\n') matched++;
                    else matched = (b == '\r') ? 1 : 0;
                    if (matched == 4) break;
                }
                string header = Encoding.ASCII.GetString(head.ToArray());
                string[] lines = header.Split(new[] { "\r\n" }, StringSplitOptions.None);
                if (lines.Length == 0) return;
                string[] rl = lines[0].Split(' ');
                if (rl.Length < 2) return;
                string method = rl[0], path = rl[1], query = "";
                int qi = path.IndexOf('?');
                if (qi >= 0) { query = path.Substring(qi + 1); path = path.Substring(0, qi); }

                int contentLen = 0;
                foreach (var ln in lines)
                    if (ln.ToLowerInvariant().StartsWith("content-length:"))
                        int.TryParse(ln.Substring(15).Trim(), out contentLen);

                string body = "";
                if (contentLen > 0)
                {
                    var buf = new byte[contentLen]; int got = 0;
                    while (got < contentLen) { int r = ns.Read(buf, got, contentLen - got); if (r <= 0) break; got += r; }
                    body = Encoding.UTF8.GetString(buf, 0, got);
                }

                if (method == "GET" && (path == "/" || path == "/index.html")) ServeHtml(ns);
                else if (path == "/status") Respond(ns, "application/json", Status());
                else if (method == "POST" && path == "/snapshot") DoSnapshot(ns, body, query);
                else if (method == "GET" && path == "/part") ServePart(ns, query);
                else Respond(ns, "text/plain", "not found", "404 Not Found");
            }
        }

        // The page asks this before it offers the Snapshot button, so a missing renderer is said
        // plainly in the application rather than discovered as a failed snapshot.
        static string Status()
        {
            string ldview = FindLDView(), ldraw = FindLDrawDir();
            return "{\"sangala\":\"blocks\",\"ldview\":" + (ldview != null ? "true" : "false") +
                   ",\"ldraw\":" + (ldraw != null ? "true" : "false") + "}";
        }

        static void DoSnapshot(NetworkStream ns, string body, string query)
        {
            string angle = "30,45";     // the three-quarter view LEGO booklets are drawn in
            int w = 1000, h = 800;
            foreach (var pair in query.Split('&'))
            {
                int eq = pair.IndexOf('=');
                if (eq <= 0) continue;
                string k = pair.Substring(0, eq), v = Uri.UnescapeDataString(pair.Substring(eq + 1));
                if (k == "angle") angle = v;
                else if (k == "w") int.TryParse(v, out w);
                else if (k == "h") int.TryParse(v, out h);
            }
            if (string.IsNullOrEmpty(body.Trim())) { Respond(ns, "application/json", "{\"ok\":false,\"error\":\"empty model\"}", "400 Bad Request"); return; }

            string err;
            byte[] png = Render(body, angle, w, h, out err);
            if (png == null) { Respond(ns, "application/json", "{\"ok\":false,\"error\":\"" + Esc(err) + "\"}", "500 Error"); return; }
            var headBytes = Encoding.ASCII.GetBytes(
                "HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: " + png.Length +
                "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(headBytes, 0, headBytes.Length);
            ns.Write(png, 0, png.Length);
        }

        static void ServeHtml(NetworkStream ns)
        {
            byte[] html = File.ReadAllBytes(_htmlPath);
            var head = Encoding.ASCII.GetBytes(
                "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " + html.Length +
                "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(head, 0, head.Length); ns.Write(html, 0, html.Length);
        }

        // ---------------------------------------------------------------- the parts themselves
        // THE BRIDGE STILL MAKES NO GEOMETRY. The 3D view is drawn from the library's own part
        // files - the same files LDView reads, so what is on screen and what is in the snapshot are
        // one shape - and a browser cannot read a folder. So this hands over a part and everything
        // that part refers to, as text, in a single reply. It resolves names and nothing else.
        //
        // One rule travels with the text: WHERE p\48\<name> EXISTS IT IS SENT IN THE PLAIN NAME'S
        // PLACE. That is LDView's own high-resolution substitution, and it is what makes a circle
        // read as a circle rather than as the sixteen-sided figure the plain primitives describe.
        // Deciding it here keeps the page's reader simple: it draws what it is given.
        static void ServePart(NetworkStream ns, string query)
        {
            string want = null;
            foreach (var pair in query.Split('&'))
            {
                int eq = pair.IndexOf('=');
                if (eq > 0 && pair.Substring(0, eq) == "f") want = Uri.UnescapeDataString(pair.Substring(eq + 1));
            }
            string ldrawDir = FindLDrawDir();
            if (want == null || ldrawDir == null) { Respond(ns, "text/plain", "no parts folder", "404 Not Found"); return; }
            if (!want.EndsWith(".dat", StringComparison.OrdinalIgnoreCase)) want += ".dat";
            if (!SafeName(want)) { Respond(ns, "text/plain", "bad part name", "400 Bad Request"); return; }

            // Walk the references breadth-first. The count is bounded because a runaway walk on a
            // malformed file would hold the connection open; no real part comes near the limit.
            var files = new Dictionary<string, string>(StringComparer.Ordinal);
            var queue = new Queue<string>();
            queue.Enqueue(want);
            while (queue.Count > 0 && files.Count < 800)
            {
                string name = queue.Dequeue();
                string key = PartKey(name);
                if (files.ContainsKey(key)) continue;
                string file = FindPartFile(ldrawDir, name);
                if (file == null) { files[key] = ""; continue; }   // sent empty, so the page can say what is missing
                string text = File.ReadAllText(file);
                files[key] = text;
                foreach (var ln in text.Split('\n'))
                {
                    var t = ln.Trim().Split(new[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                    if (t.Length >= 15 && t[0] == "1")
                    {
                        string sub = string.Join(" ", t, 14, t.Length - 14);
                        if (SafeName(sub)) queue.Enqueue(sub);
                    }
                }
            }

            var sb = new StringBuilder();
            sb.Append("{\"name\":").Append(JsonStr(PartKey(want))).Append(",\"files\":{");
            bool first = true;
            foreach (var kv in files)
            {
                if (!first) sb.Append(',');
                first = false;
                sb.Append(JsonStr(kv.Key)).Append(':').Append(JsonStr(kv.Value));
            }
            sb.Append("}}");
            Respond(ns, "application/json", sb.ToString());
        }

        // The name as the page will look it up: one spelling, whatever slash the file was written
        // with and whatever case the reference used.
        static string PartKey(string name)
        {
            return (name ?? "").Trim().Replace('\\', '/').ToLowerInvariant();
        }

        // A part name arrives over a socket, so it is checked before it becomes a path. Only the
        // characters LDraw itself uses, no drive letter, no leading slash, and no way upwards.
        static bool SafeName(string name)
        {
            if (string.IsNullOrEmpty(name) || name.Length > 80) return false;
            if (name.IndexOf("..") >= 0 || name.IndexOf(':') >= 0) return false;
            if (name[0] == '\\' || name[0] == '/') return false;
            foreach (char c in name)
                if (!(char.IsLetterOrDigit(c) || c == '.' || c == '-' || c == '_' || c == '\\' || c == '/')) return false;
            return true;
        }

        static string FindPartFile(string ldrawDir, string name)
        {
            string n = name.Replace('/', '\\');
            if (!n.StartsWith("48\\", StringComparison.OrdinalIgnoreCase))
            {
                string hi = Path.Combine(ldrawDir, "p", "48", n);      // the 48-segment curve, where there is one
                if (File.Exists(hi)) return hi;
            }
            string[] dirs = { "parts", "p", Path.Combine("parts", "s"), Path.Combine("p", "48") };
            foreach (var d in dirs)
            {
                string p = Path.Combine(ldrawDir, d, n);
                if (File.Exists(p)) return p;
            }
            return null;
        }

        static string JsonStr(string s)
        {
            var sb = new StringBuilder("\"");
            foreach (char c in s ?? "")
            {
                if (c == '"' || c == '\\') { sb.Append('\\').Append(c); }
                else if (c == '\n') sb.Append("\\n");
                else if (c == '\r') sb.Append("\\r");
                else if (c == '\t') sb.Append("\\t");
                else if (c < ' ') sb.Append("\\u").Append(((int)c).ToString("x4"));
                else sb.Append(c);
            }
            return sb.Append('"').ToString();
        }

        static void Respond(NetworkStream ns, string ctype, string bodyText, string status = "200 OK")
        {
            byte[] data = Encoding.UTF8.GetBytes(bodyText ?? "");
            var head = Encoding.ASCII.GetBytes(
                "HTTP/1.1 " + status + "\r\nContent-Type: " + ctype + "; charset=utf-8\r\nContent-Length: " + data.Length +
                "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(head, 0, head.Length); ns.Write(data, 0, data.Length);
        }

        static string Esc(string s) { return (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\""); }

        // ---------------------------------------------------------------- tray
        class TrayContext : ApplicationContext
        {
            NotifyIcon _icon;
            static System.Drawing.Icon OwnIcon()
            {
                try
                {
                    var ico = System.Drawing.Icon.ExtractAssociatedIcon(Application.ExecutablePath);
                    if (ico != null) return ico;
                }
                catch { }
                return System.Drawing.SystemIcons.Application;
            }
            public TrayContext(int port)
            {
                string url = "http://localhost:" + port + "/";
                var menu = new ContextMenuStrip();
                menu.Items.Add("Open Sangala Blocks", null, (a, b) => { try { Process.Start(url); } catch { } });
                menu.Items.Add("Quit Sangala Blocks", null, (a, b) => { _icon.Visible = false; Application.Exit(); });
                _icon = new NotifyIcon
                {
                    Icon = OwnIcon(),
                    Text = "Sangala Blocks (running)",
                    Visible = true,
                    ContextMenuStrip = menu
                };
                _icon.DoubleClick += (a, b) => { try { Process.Start(url); } catch { } };
                _icon.ShowBalloonTip(4000, "Sangala Blocks", "Running in the tray. Right-click the icon to open or quit.", ToolTipIcon.Info);
            }
            protected override void Dispose(bool disposing)
            {
                if (disposing && _icon != null) { _icon.Dispose(); _icon = null; }
                base.Dispose(disposing);
            }
        }
    }
}
