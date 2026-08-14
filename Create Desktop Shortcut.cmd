@echo off
REM ===============================================================
REM  Create Desktop Shortcut.cmd
REM
REM  Puts a "Sangala Blocks" icon on your Desktop so you can
REM  start the program without hunting for this folder.
REM
REM  Double-click this file once. It points the shortcut at
REM  SangalaBlockDesigner.exe sitting next to it (the crane icon is built
REM  in), so it works no matter where you keep the Sangala Blocks
REM  folder.
REM
REM  No admin rights are needed: it only writes to your own Desktop.
REM  Safe to run again - it simply refreshes the shortcut.
REM ===============================================================
setlocal
set "SANGALA_HOME=%~dp0"
set "SANGALA_TARGET=%~dp0SangalaBlockDesigner.exe"
REM  THE SHORTCUT TAKES ITS PICTURE FROM Crane.ico, NOT FROM THE EXE, and the reason is worth
REM  keeping: Windows caches an icon against the file it came from, so rebuilding the launcher in
REM  place leaves the Desktop showing the OLD picture however many times the shortcut is remade.
REM  Clearing the cache did not shift it; a file Windows has not cached does. The icon's home is
REM  the .ico anyway, and the exe still carries it for anyone who runs the exe directly.
set "SANGALA_ICON=%~dp0Crane.ico"

echo.
echo   Creating a Desktop shortcut for Sangala Blocks...

if not exist "%SANGALA_TARGET%" (
  echo.
  echo   Could not find SangalaBlockDesigner.exe in this folder:
  echo     %SANGALA_HOME%
  echo.
  echo   Run "Build SangalaBlockDesigner Launcher.cmd" first, then run this again.
  echo.
  pause
  exit /b 1
)

REM  The paths travel as environment variables, so folder names with
REM  spaces or apostrophes cannot break the quoting. SpecialFolders
REM  finds the real Desktop even when OneDrive has redirected it. The
REM  picture comes from Crane.ico for the reason given above.
REM  The icon is labeled "Sangala Blocks" so the name fits under it on the Desktop instead of
REM  wrapping onto three lines; the full name is in the tooltip. An earlier shortcut made under
REM  the long name is removed, so running this again leaves one icon rather than two.
powershell -NoProfile -Command "try { $ws = New-Object -ComObject WScript.Shell; $desktop = $ws.SpecialFolders('Desktop'); $old = Join-Path $desktop 'Sangala Block Designer.lnk'; if (Test-Path $old) { Remove-Item $old -Force }; $path = Join-Path $desktop 'Sangala Blocks.lnk'; $lnk = $ws.CreateShortcut($path); $lnk.TargetPath = $env:SANGALA_TARGET; $lnk.WorkingDirectory = $env:SANGALA_HOME.TrimEnd('\'); $lnk.IconLocation = $env:SANGALA_ICON + ',0'; $lnk.Description = 'Sangala Blocks - Block Design Tool'; $lnk.Save(); Write-Host ''; Write-Host ('   Shortcut created: ' + $path); exit 0 } catch { Write-Host ''; Write-Host ('   Could not create the shortcut: ' + $_.Exception.Message); exit 1 }"

if errorlevel 1 (
  echo.
  echo   The shortcut was not created. You can still make one by hand:
  echo   right-click SangalaBlockDesigner.exe, choose Show more options,
  echo   then Send to - Desktop.
  echo.
  pause
  exit /b 1
)

echo.
echo   Done. Look for the "Sangala Blocks" icon on your Desktop and
echo   double-click it to start.
echo.
pause
