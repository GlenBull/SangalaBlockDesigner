@echo off
REM ==========================================================================
REM  Build SangalaBlockDesigner.exe -- the local bridge for Sangala Blocks.
REM  It serves SangalaBlockDesigner.html on a loopback port and runs LDView to
REM  render a snapshot, which a browser cannot do for itself. Same shape as
REM  Sangala Studio's SangalaServer.cs, and like it a real program, so managed
REM  school Windows does not block it the way it blocks .cmd and .bat files.
REM  The crane icon is embedded, so the exe and any Desktop shortcut show it.
REM  Compiled with the .NET compiler already in Windows -- no admin, no install.
REM
REM  Needs, together in this folder:  SangalaBlocksServer.cs  and  Crane.ico
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
  "SangalaBlocksServer.cs"

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
