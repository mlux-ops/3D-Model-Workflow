@echo off
rem Starts the walking-path editor and opens it in the default browser.
rem Paths are saved as .json files in this folder; "Request videos" asks the editor to render them.
cd /d "%~dp0"
start "Path editor server" /min python -I path_server.py
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8766/
