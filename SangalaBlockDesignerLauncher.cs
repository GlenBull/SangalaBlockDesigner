// Sangala Block Designer launcher — Sangala Mosaic's launcher, ported whole, because the two
// applications are the same shape: a page with no bridge behind it. A real program (not a script),
// so managed/school Windows treats it like Sangala Studio's SangalaStudio.exe (which runs fine)
// rather than blocking it the way it blocks .cmd/.bat files. Double-clicking it opens the app page
// (SangalaBlockDesigner.html, kept next to the exe) in the default browser. The crane icon is
// embedded at build time via /win32icon, so the exe and any Desktop shortcut to it show the crane.
// Compiled in-box with the .NET Framework csc.exe — no admin, no install.
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace SangalaBlockDesignerApp
{
    static class Launcher
    {
        [STAThread]
        static void Main()
        {
            string dir = AppDomain.CurrentDomain.BaseDirectory;
            string html = Path.Combine(dir, "SangalaBlockDesigner.html");
            try
            {
                if (!File.Exists(html))
                {
                    MessageBox.Show(
                        "SangalaBlockDesigner.html was not found next to this launcher.\r\n\r\n" +
                        "Keep SangalaBlockDesigner.exe and SangalaBlockDesigner.html together in the same folder.",
                        "Sangala Block Designer", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }
                Process.Start(new ProcessStartInfo(html) { UseShellExecute = true });
            }
            catch (Exception ex)
            {
                MessageBox.Show("Could not open Sangala Block Designer:\r\n" + ex.Message,
                    "Sangala Block Designer", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
