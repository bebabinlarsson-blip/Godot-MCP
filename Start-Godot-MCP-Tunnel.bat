@echo off
setlocal
title Godot MCP Stable Tunnel

echo Godot MCP stable tunnel launcher
echo.
echo This connects to the Godot MCP server already running in your editor.
echo Keep Godot open while the tunnel is running.
echo.

if not defined GODOT_AI_AUTH_TOKEN (
  echo ERROR: GODOT_AI_AUTH_TOKEN is not set.
  echo Set it in Windows Environment Variables before opening Godot.
  echo The same token must be available to both Godot and this launcher.
  echo.
  pause
  exit /b 1
)

where uvx >nul 2>nul
if errorlevel 1 (
  echo ERROR: uvx was not found.
  echo Install Python 3.11-3.14 and uv, then reopen this window.
  echo https://docs.astral.sh/uv/getting-started/installation/
  echo.
  pause
  exit /b 1
)

where tailscale >nul 2>nul
if errorlevel 1 (
  echo ERROR: Tailscale CLI was not found.
  echo Install Tailscale, sign in, and enable Funnel for your tailnet.
  echo https://tailscale.com/kb/1223/funnel/
  echo.
  pause
  exit /b 1
)

echo Starting Tailscale Funnel on local port 8000...
echo If setup is complete, the stable HTTPS address will appear below.
echo This window must stay open. Press Ctrl+C to stop the tunnel.
echo.
uvx --isolated --no-config --no-env-file --no-sources --no-build --index-strategy first-index --keyring-provider disabled --index https://pypi.org/simple --default-index https://pypi.org/simple --find-links https://pypi.org/simple/godot-ai/ --link-mode copy --from "https://github.com/bebabinlarsson-blip/Godot-MCP/releases/download/v5.0.39/godot_ai-5.0.39-py3-none-any.whl" godot-ai tunnel --provider tailscale-funnel --port 8000
set "RESULT=%ERRORLEVEL%"

if not "%RESULT%"=="0" (
  echo.
  echo Tunnel stopped with error code %RESULT%.
  echo Check that Godot MCP is enabled and connected in the project editor.
  echo.
  pause
)

exit /b %RESULT%
