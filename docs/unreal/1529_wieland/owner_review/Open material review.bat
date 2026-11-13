@echo off
rem Starts the material review page and opens it in the default browser.
rem Answers are written to ..\material_audit.csv (decision, owner_note) and decisions_log.csv.
cd /d "%~dp0"
start "Material review server" /min python -I review_server.py
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8765/
