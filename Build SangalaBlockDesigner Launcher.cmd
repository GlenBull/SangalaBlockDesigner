@echo off
REM ==========================================================================
REM  Build SangalaBlockDesigner.exe -- the desktop launcher for Sangala Block
REM  Designer. It is a real program (like Sangala Studio's exe), so it is NOT
REM  blocked the way school/managed Windows blocks .cmd scripts. Double-clicking
REM  it opens SangalaBlockDesigner.html (kept next to it) in the browser. The
REM  crane icon is embedded, so the exe and any Desktop shortcut to it show the
REM  crane. Compiled in-box with the .NET compiler already in Windows -- no admin.
REM
REM  Needs, together in this folder:  SangalaBlockDesignerLauncher.cs  and  Crane.ico
REM  After building, keep SangalaBlockDesigner.exe next to SangalaBlockDesigner.html.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "OUT=SangalaBlockDesigner.exe"
set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"
if not exist "%CSC%" ( echo Could not find the built-in .NET compiler ^(csc.exe^). & pause & exit /b 1 )
if not exist "Crane.ico" ( echo Could not find Crane.ico ^(the program icon^) in this folder. & pause & exit /b 1 )

echo Building %OUT% ...
"%CSC%" /nologo /target:winexe /out:"%OUT%" ^
  /win32icon:"Crane.ico" ^
  /reference:System.dll ^
  /reference:System.Drawing.dll ^
  /reference:System.Windows.Forms.dll ^
  "SangalaBlockDesignerLauncher.cs"

if errorlevel 1 (
  echo.
  echo BUILD FAILED. Copy the red error messages above and send them back.
  echo.
  pause
  exit /b 1
)

echo.
echo Build succeeded:  "%~dp0%OUT%"
echo Keep SangalaBlockDesigner.exe next to SangalaBlockDesigner.html, then double-click the exe.
echo.
pause
