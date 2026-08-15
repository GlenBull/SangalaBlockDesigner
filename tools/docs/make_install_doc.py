"""Installation instructions for Sangala Block Designer, into the Block Tools folder."""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"D:\Code Projects\Block Tools"

d = Doc()
d.title("Installing Sangala Blocks")

d.body("Sangala Blocks runs in a web browser, like Sangala Mosaic. Nothing is installed and no "
       "administrator rights are needed. The only setup is to put an icon on the Desktop that opens it.")
d.body("Every step below was run on this machine before being written down.")

d.heading("What Has to Be in the Folder")
d.body("These files belong together in one folder, and the program folder is "
       "D:\\Code Projects\\Block Tools.", before_list=True)
d.table(
    "Table 1. The Files the Installation Uses",
    ["File", "What It Is"],
    [
        ["SangalaBlockDesigner.html", "The program itself. The file keeps its longer name; the program is called Sangala Blocks"],
        ["SangalaBlockDesigner.exe", "The launcher. Double-clicking it opens the program in the browser"],
        ["Crane.ico", "The icon, a crowned crane in bricks"],
        ["Build SangalaBlockDesigner Launcher.cmd", "Rebuilds the launcher. Needed only if the exe is missing"],
        ["Create Desktop Shortcut.cmd", "Puts the icon on the Desktop"],
    ],
    weights=[42, 58])

d.heading("Putting the Icon on the Desktop")
d.body("If SangalaBlockDesigner.exe is already in the folder, start at step 2.", before_list=True)
d.step("If there is no SangalaBlockDesigner.exe, double-click Build SangalaBlockDesigner Launcher.cmd. "
       "It reports \"Build succeeded\" and waits for a key. Press any key to close it.")
d.step("Double-click Create Desktop Shortcut.cmd. It reports \"Shortcut created\" and names the file it "
       "wrote. Press any key to close it.")
d.step("Look on the Desktop for an icon named Sangala Blocks, showing a crowned crane on blue tiles. "
       "Double-click it. The program opens in the default browser.")
d.body("The script may be run as often as needed; it replaces the shortcut rather than adding another. "
       "It also removes an older shortcut named Sangala Block Designer, so only one icon remains.")

d.heading("If the Icon Shows the Wrong Picture")
d.body("This is the one fault likely to be met, and it is a fault in Windows rather than in the program. "
       "Windows keeps a cache of icon pictures, indexed by the file the picture came from. When the "
       "launcher is rebuilt with a new icon, the file name has not changed, so Windows goes on showing "
       "the picture it already has. Refreshing the Desktop does not clear it.")
d.body("To clear it, hold the Windows key and press R, type the line below, and press Enter. The screen "
       "may flicker once. No administrator rights are needed.", before_list=True)
d.code("ie4uinit.exe -show")
d.body("Then run Create Desktop Shortcut.cmd again. If the old picture still appears, sign out of Windows "
       "and back in, which rebuilds the cache completely.")

d.heading("If Double-Clicking the Icon Does Nothing")
d.body("Three causes, in the order worth checking.", before_list=True)
d.step("The launcher cannot find the program. It says so in a message box naming the file it looked for. "
       "SangalaBlockDesigner.exe and SangalaBlockDesigner.html must sit in the same folder.")
d.step("The folder has been moved or renamed since the shortcut was made. Run Create Desktop Shortcut.cmd "
       "again from the folder's new place, which points the shortcut at the new path.")
d.step("Windows warns that it protected the computer, because the launcher is not signed. Choose More "
       "info, then Run anyway. Windows asks once and remembers.")

d.heading("What the Launcher Does")
d.body("It is a small program rather than a script, which matters on managed and school computers: those "
       "commonly block a .cmd or .bat file from running while allowing an ordinary program. It checks that "
       "SangalaBlockDesigner.html is beside it, opens that page in the default browser, and exits. It "
       "sends nothing to the internet and writes nothing outside the folder. The Desktop shortcut is "
       "written to the user's own Desktop and nowhere else.")

print(d.save(OUT, "Installing Sangala Blocks"))
